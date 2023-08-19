import os
from unittest import TestCase
from unittest.mock import MagicMock

import numpy as np
from PIL import Image
from pyscreeze import Box

import properties
from core import sensor
from util import img_logger

TEST_IMAGES_PATH = "test/resources/hexagonest"

test_images = os.listdir(TEST_IMAGES_PATH)


class TestHexagonest(TestCase):
    def setUp(self) -> None:
        sensor._game_position = Box(0, 0, properties.GAME_WINDOW_WITHOUT_MARGIN[2], properties.GAME_WINDOW_WITHOUT_MARGIN[3])
        sensor._camera = MagicMock()

    def tearDown(self) -> None:
        img_logger.finalize()

    def test_detection(self):
        for test_image in test_images:
            with self.subTest(test_image):
                sensor._camera.get_latest_frame.return_value = np.array(Image.open(TEST_IMAGES_PATH + "/" + test_image))
                properties.SCREENSHOT_LOGGER_IMAGE_NAME = test_image

                sensor.capture()

                try:
                    assert len(set(sensor.detect_available_distances())) > 1
                    assert sensor.detect_player()
                finally:
                    sensor.clear()
