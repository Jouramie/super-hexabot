from unittest import TestCase
from unittest.mock import patch

from PIL import Image
from pyscreeze import Box

import properties
from core import sensor, brain

properties.LOGS_PATH = "../logs"
properties.SCREENSHOT_LOGGING_NAME = "test.tiff"
properties.SCREENSHOT_LOGGING_ENABLED = False


class Test(TestCase):
    def setUp(self) -> None:
        sensor._game_position = Box(0, 0, 767, 479)

    @patch("pyautogui.screenshot")
    # @skip
    def test_manual(self, screenshot):
        properties.SENSOR_LOG_DISTANCES = True
        screenshot.return_value = Image.open("../logs/2022-11-29T005417.525807.tiff")

        sensor.capture()

        distances = sensor.detect_available_distances()
        position = sensor.detect_player()
        chosen_direction = brain.choose_direction(position, distances)

        self.assertAlmostEqual(chosen_direction, 0.0, delta=properties.MOTOR_MIN_ROTATION)
