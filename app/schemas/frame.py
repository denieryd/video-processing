"""Domain schemas."""


class Frame:
    def __init__(
        self,
        frame_obj,
        video_name: str = None,
        frame_number: int = None,
        timestamp: str = None,
        rle: str = None,
    ):
        self.frame_obj = frame_obj
        self.video_name = video_name
        self.frame_number = frame_number
        self.timestamp = timestamp
        self.rle = rle
