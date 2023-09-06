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
            try:
                os.remove(Path(f"{properties.SCREENSHOT_LOGGER_LOGS_PATH}/{sorted(saved_screenshots)[0]}"))
            except PermissionError:
                logger.warning(f"Could not delete {name}.")


def push_image_to_buffer(name, image):
    global _buffer, _lock
    with _lock:
        _buffer.append((name, image))


def submit(image):
    global _image
    if not properties.SCREENSHOT_LOGGER_ENABLED:
        return

    name = f"{datetime.now().replace().isoformat().replace(':', '')}.tiff"
    logger.info(f"Submit {name} to log buffer.")
    _image = name, image


def edit(edit_func):
    global _image
    if not properties.SCREENSHOT_LOGGER_ENABLED or not properties.SCREENSHOT_LOGGER_EDIT_ENABLED or _image is None:
        return

    _image = _image[0], edit_func(_image[1])


def publish():
    global _image
    if not properties.SCREENSHOT_LOGGER_ENABLED or _image is None:
        return

    name = properties.SCREENSHOT_LOGGER_IMAGE_NAME
    if name is None:
        name = _image[0]

    logger.debug(f"Pushing image {name} to log buffer.")
    push_image_to_buffer(name, _image[1])

    _image = None


def log_now(image, name=None):
    image = PIL.Image.fromarray(image)
    image.save(Path(f"{properties.SCREENSHOT_LOGGER_LOGS_PATH}/{name}"))


def start():
    global _running
    thread = threading.Thread(target=log_next_image)
    thread.start()


def finalize():
    global _buffer, _running
    while _buffer:
        logger.info(f"Waiting buffer to empty before leaving.")
        time.sleep(0.01)

    _running = False
