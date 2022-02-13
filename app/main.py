import os
import threading
from multiprocessing import Process, Queue
from os.path import join
from threading import Thread

import cv2

from app.db.repository.video_frame import VideoFrameRepository
from app.schemas.frame import Frame
from app.services.logger import logger
from app.services.rle import rle_encoding
from app.services.utils import (calculate_chunk_size_for_thread,
                                get_video_files_names, move_file)
from app.settings.config import Config

config = Config()


def process_frames_and_move_to_queue(
    frames_queue: Queue, resulted_queue: Queue
) -> None:
    """Process frames from `frames_queue` and put them to `resulted_queue`."""

    for process_number in range(config.workers_count):
        Process(
            target=_process_frames_and_move_to_queue,
            args=(frames_queue, resulted_queue),
        ).start()


def write_processed_frames_to_db(resulted_queue: Queue) -> None:
    """Get frames from `resulted_queue` and write them to db."""
    for process_number in range(config.workers_count):
        process = Process(target=_write_processed_frames_to_db, args=(resulted_queue,))
        process.start()


def extract_frames_from_videos(video_files_names, frames_queue: Queue) -> None:
    """Extract frames from video files and move to queue `frames_queue`.

    Each video file processed in separate process.
    """

    for file_name in video_files_names:
        process = Process(
            target=_extract_frames_from_video, args=(file_name, frames_queue)
        )
        logger.info(
            f"allocate separate process {process.pid} to extract frames from {file_name}"
        )
        process.start()


def run_processing_pipeline():
    """Run pipeline that process videos."""

    frames_queue = Queue()
    resulted_queue = Queue()

    video_files_names = get_video_files_names(dir_path=config.dir_in)
    logger.info(
        f"found {len(video_files_names)} video files in dir {config.dir_in} to process"
    )

    extract_frames_from_videos(
        video_files_names=video_files_names, frames_queue=frames_queue
    )
    process_frames_and_move_to_queue(
        frames_queue=frames_queue, resulted_queue=resulted_queue
    )
    write_processed_frames_to_db(resulted_queue=resulted_queue)


def _extract_frames_from_video(video_file_name, frames_queue: Queue):
    """Extract frames from video file and put them in queue.

    Extracting frames happening using threads, their counts depends on config.
    """
    logger.info(
        f"process video file {video_file_name} in separate process PID {os.getpid()}"
    )

    video_capture = cv2.VideoCapture(join(config.dir_in, video_file_name))

    chunk_size = calculate_chunk_size_for_thread(video_capture, config.workers_count)
    frames_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    last_frames_chunk = frames_count - chunk_size

    threads = []
    for chunk_start_pos in range(0, last_frames_chunk, chunk_size):
        thread = Thread(
            target=_extract_frames_from_video_capture,
            args=(
                chunk_start_pos,
                chunk_start_pos + chunk_size,
                video_file_name,
                frames_queue,
            ),
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    move_file(
        join(config.dir_in, video_file_name), join(config.dir_out, video_file_name)
    )
    logger.info(f"extracting frames from {video_file_name} has been done")


def _extract_frames_from_video_capture(
    frame_start_pos: int,
    frame_end_pos: int,
    video_file_name: str,
    frames_queue: Queue,
):
    """Extract specific range of frames from video.

    Processing happening in separate thread.
    """
    logger.info(
        f"extracting frames from {frame_start_pos} to {frame_end_pos} in file {video_file_name} thread id {threading.get_ident()}"
    )
    video_capture = cv2.VideoCapture(join(config.dir_in, video_file_name))
    video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_start_pos)

    for frame_number in range(frame_start_pos, frame_end_pos):
        frame_timestamp = str(video_capture.get(cv2.CAP_PROP_POS_MSEC))
        grabbed, frame_obj = video_capture.read()
        if grabbed:
            frames_queue.put(
                Frame(
                    frame_obj=frame_obj,
                    video_name=video_file_name,
                    frame_number=frame_number,
                    timestamp=frame_timestamp,
                )
            )


def _process_frames_and_move_to_queue(frames_queue: Queue, resulted_queue: Queue):
    """Process frames from `frames_queue` and put them in `resulted_queue`."""
    while True:
        frame: Frame = frames_queue.get()
        if frame:
            logger.info(
                f"process frame {frame.frame_number} from video {frame.video_name}"
            )
            frame.frame_obj = cv2.resize(src=frame.frame_obj, dsize=(200, 200))
            frame.frame_obj = cv2.cvtColor(frame.frame_obj, cv2.COLOR_BGR2GRAY)
            frame.rle = rle_encoding(frame.frame_obj)
            resulted_queue.put(frame)
            logger.info(
                f"frame {frame.frame_number} from video {frame.video_name} has been put to resulted queue"
            )
        else:
            continue


def _write_processed_frames_to_db(resulted_queue: Queue):
    """Get processed frames from `resulted_queue` in write them to db."""

    while True:
        frame: Frame = resulted_queue.get()
        if frame:
            logger.info(
                f"write frame {frame.frame_number} from {frame.video_name} to database"
            )
            VideoFrameRepository.insert(
                video_name=frame.video_name,
                frame_number=frame.frame_number,
                timestamp=frame.timestamp,
                rle=frame.rle,
            )


if __name__ == "__main__":
    run_processing_pipeline()