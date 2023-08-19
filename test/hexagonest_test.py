import os
from unittest import TestCase
from unittest.mock import MagicMock

import numpy as np
from PIL import Image
from pyscreeze import Box

import properties
from core import sensor, brain
from util import img_logger, img_edit

TEST_IMAGES_PATH = "test/resources/hexagonest"

test_images = os.listdir(TEST_IMAGES_PATH)


class TestHexagonest(TestCase):
    def setUp(self) -> None:
        sensor._game_position = Box(
            0, 0, properties.GAME_WINDOW_WITHOUT_MARGIN[2], properties.GAME_WINDOW_WITHOUT_MARGIN[3]
        )
        sensor._camera = MagicMock()

    def tearDown(self) -> None:
        img_logger.finalize()

    def test_detection(self):
        for test_image in test_images:
            with self.subTest(test_image):
                sensor._camera.get_latest_frame.return_value = np.array(Image.open(TEST_IMAGES_PATH + "/" + test_image))
                properties.SCREENSHOT_LOGGER_IMAGE_NAME = test_image

                sensor.capture()
                position, distance = sensor.detect_player()
                available_distances = sensor.detect_available_distances()
                unsafe, direction = brain.choose_direction(position, distance, available_distances)

                img_logger.edit(img_edit.draw_player_rotation(position, direction, unsafe))
                img_logger.edit(img_edit.draw_safe_area(distance))
                img_logger.edit(img_edit.draw_unsafe_area(distance))

                try:
                    assert position, distance
                    assert len(set(available_distances)) > 1
                finally:
                    sensor.clear()
