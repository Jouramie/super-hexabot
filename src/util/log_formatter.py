import time
from datetime import timedelta


class ElapsedFormatter:
    def __init__(self):
        self.start_time = time.time()

    def format(self, record):
        elapsed_seconds = record.created - self.start_time
        # using timedelta here for convenient default formatting
        elapsed = timedelta(seconds=elapsed_seconds)
        return "{} {}".format(elapsed, record.getMessage())

    def start(self):
        self.start_time = time.time()
