import os
import shutil
from os.path import isfile, join

import cv2


def get_video_files_names(dir_path: str) -> list[str]:
    """Read all files in `dir_path` and returned video file names (with .mp4 at end)."""
    all_files_in_dir = [
        file for file in os.listdir(dir_path) if isfile(join(dir_path, file))
    ]
    video_file_names = [file for file in all_files_in_dir if file.endswith(".mp4")]

    return video_file_names


def move_file(source_path: str, destination_path: str) -> None:
    """Move file from `source_path` to `destination_path`"""
    shutil.move(source_path, destination_path)


def calculate_chunk_size_for_thread(video_capture: cv2.VideoCapture, workers_count):
    """Calculate frames chunk size each thread will process."""
    frames_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    chunk_size = int(frames_count / workers_count)

    return chunk_size
