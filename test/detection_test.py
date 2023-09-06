import os
import typing
from unittest import TestCase
from unittest.mock import MagicMock

import numpy as np
from PIL import Image
from pyscreeze import Box

import properties
from core import sensor, brain
from util import img_logger, img_edit


class BaseDetectionTest(TestCase):
    path: typing.ClassVar[str] = None

    def setUp(self) -> None:
        sensor._game_position = Box(
            0, 0, properties.GAME_WINDOW_WITHOUT_MARGIN[2], properties.GAME_WINDOW_WITHOUT_MARGIN[3]
        )
        sensor._camera = MagicMock()
        # img_logger.start()

    def tearDown(self) -> None:
        # img_logger.finalize()
        pass

    def test_detection(self):
        if self.path is None:
            return

        test_images = os.listdir(self.path)

        for test_image in test_images:
            with self.subTest(test_image):
                sensor._camera.get_latest_frame.return_value = np.array(Image.open(self.path + "/" + test_image))
                properties.SCREENSHOT_LOGGER_IMAGE_NAME = test_image

                try:
                    sensor.capture()
                    position, distance = sensor.detect_player()
                    available_distances = sensor.detect_available_distances()
                    unsafe, direction = brain.choose_direction(position, distance, available_distances)

                    img_logger.edit(img_edit.draw_player_rotation(position, direction, unsafe))
                    img_logger.edit(img_edit.draw_safe_area(distance))
                    img_logger.edit(img_edit.draw_unsafe_area(distance))

                    assert position is not None
                    assert len(set(available_distances)) > 1
                finally:
                    sensor.clear()


class TestHexagoner(BaseDetectionTest):
    path = "test/resources/hexagoner"


class TestHexagonest(BaseDetectionTest):
    path = "test/resources/hexagonest"


class TestHyperHexagoner(BaseDetectionTest):
    path = "test/resources/hyper_hexagoner"
