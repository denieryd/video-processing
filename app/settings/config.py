import os


class Config:
    dir_in = os.getenv("dir_in", default="in")
    dir_out = os.getenv("dir_out", default="out")
    workers_count = 3
