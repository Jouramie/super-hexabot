import logging
import os
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path

import PIL
import numpy as np
from PIL.Image import Image

import properties

MAX_BUFFER_SIZE = 50

logger = logging.getLogger(__name__)

_image: np.ndarray | None = None


_running = properties.SCREENSHOT_LOGGER_ENABLED
_buffer = deque(maxlen=MAX_BUFFER_SIZE)
_lock = threading.Lock()


def log_next_image():
    global _buffer, _lock
    while _running:
        if not _buffer:
            time.sleep(0.01)
            continue

        with _lock:
            name, image = _buffer.popleft()
            size = len(_buffer)

        logger.info(f"Logging image {name}, {size} more images to log.")
        image = PIL.Image.fromarray(image)
        image.save(Path(f"{properties.SCREENSHOT_LOGGER_LOGS_PATH}/{name}"))

        saved_screenshots = os.listdir(properties.SCREENSHOT_LOGGER_LOGS_PATH)

        if len(saved_screenshots) > properties.SCREENSHOT_LOGGER_ROLLING_IMAGE_AMOUNT:
            os.remove(Path(f"{properties.SCREENSHOT_LOGGER_LOGS_PATH}/{sorted(saved_screenshots)[0]}"))


def push_image_to_buffer(name, image):
    global _buffer, _lock
    with _lock:
        _buffer.append((name, image))


_thread = threading.Thread(target=log_next_image)
_thread.start()


def submit(image):
    global _image
    if not properties.SCREENSHOT_LOGGER_ENABLED:
        return

    _image = image


def transform(transformation):
    global _image
    if not properties.SCREENSHOT_LOGGER_ENABLED or not properties.SCREENSHOT_LOGGER_TRANSFORMATION_ENABLED or _image is None:
        return

    _image = transformation(_image)


def publish(name=None):
    global _image
    if not properties.SCREENSHOT_LOGGER_ENABLED or _image is None:
        return

    if name is None:
        name = properties.SCREENSHOT_LOGGER_IMAGE_NAME
    if name is None:
        name = f"{datetime.now().replace().isoformat().replace(':', '')}.tiff"

    logger.debug(f"Pushing image {name} to log buffer.")
    push_image_to_buffer(name, _image)

    _image = None


def log_now(image, name=None):
    image = PIL.Image.fromarray(image)
    image.save(Path(f"{properties.SCREENSHOT_LOGGER_LOGS_PATH}/{name}"))


def finalize():
    global _buffer, _running
    while _buffer:
        logger.info(f"Waiting buffer to empty before leaving.")
        time.sleep(0.01)

    _running = False
