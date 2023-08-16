import logging
import os
from datetime import datetime
from pathlib import Path

import PIL
import numpy as np
from PIL.Image import Image

import properties

logger = logging.getLogger(__name__)

_image: np.ndarray | None = None


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


def publish():
    global _image
    if not properties.SCREENSHOT_LOGGER_ENABLED or _image is None:
        return

    name = properties.SCREENSHOT_LOGGER_IMAGE_NAME
    if name is None:
        name = f"{datetime.now().replace().isoformat().replace(':', '')}.tiff"

    image = PIL.Image.fromarray(_image)

    logger.info(f"Logging image {name}.")
    image.save(Path(f"{properties.SCREENSHOT_LOGGER_LOGS_PATH}/{name}"))

    saved_screenshots = os.listdir(properties.SCREENSHOT_LOGGER_LOGS_PATH)

    if len(saved_screenshots) > properties.SCREENSHOT_LOGGER_ROLLING_IMAGE_AMOUNT:
        os.remove(Path(f"{properties.SCREENSHOT_LOGGER_LOGS_PATH}/{sorted(saved_screenshots)[0]}"))

    _image = None


def log(image, name=None):
    submit(image)
    publish(name)
