from unittest import TestCase
from unittest.mock import MagicMock

import numpy as np
from PIL import Image
from pyscreeze import Box

import properties
from core import sensor, brain

properties.SCREENSHOT_LOGGER_LOGS_PATH = "target"
properties.SCREENSHOT_LOGGER_IMAGE_NAME = "test.tiff"
properties.SCREENSHOT_LOGGER_ENABLED = False


class Test(TestCase):
    def setUp(self) -> None:
        sensor._game_position = Box(0, 0, properties.GAME_WINDOW_WITHOUT_MARGIN[2], properties.GAME_WINDOW_WITHOUT_MARGIN[3])

    # @skip
    def test_manual(self):
        properties.SCREENSHOT_LOGGER_TRANSFORMATION_ENABLED = True
        properties.SCREENSHOT_LOGGER_IMAGE_NAME = "test.tiff"
        sensor._camera = MagicMock()
        sensor._camera.get_latest_frame.return_value = np.array(Image.open("logs/2023-08-15T211527.729694.tiff"))

        sensor.capture()

        distances = sensor.detect_available_distances()
        position = sensor.detect_player()
        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, 0.0, delta=properties.MOTOR_MIN_ROTATION)
