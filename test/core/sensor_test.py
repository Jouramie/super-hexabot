from unittest import TestCase
from unittest.mock import patch

from PIL import Image
from pyscreeze import Box

import properties
from core import sensor

properties.LOGS_PATH = "../logs"
properties.SCREENSHOT_LOGGING_ENABLED = False


class TestPlayerDetection(TestCase):
    def setUp(self) -> None:
        sensor._game_position = Box(10, 56, 777 - 10, 535 - 56)

    @patch("pyautogui.screenshot")
    def test_detect_player_1(self, screenshot):
        screenshot.return_value = Image.open("resources/session-yellow-red/Image-025.png").crop((10, 56, 777, 535))

        sensor.capture()

        player = sensor.detect_player()

        self.assertAlmostEqual(player, 0, delta=0.05)

    @patch("pyautogui.screenshot")
    def test_detect_player_2(self, screenshot):
        screenshot.return_value = Image.open("resources/session-yellow-red/Image-233.png").crop((10, 56, 777, 535))

        sensor.capture()

        player = sensor.detect_player()

        self.assertAlmostEqual(player, 0.66, delta=0.05)

    @patch("pyautogui.screenshot")
    def test_detect_player_3(self, screenshot):
        screenshot.return_value = Image.open("resources/session-yellow-red/Image-256.png").crop((10, 56, 777, 535))

        sensor.capture()

        player = sensor.detect_player()

        self.assertAlmostEqual(player, -0.35, delta=0.05)

    @patch("pyautogui.screenshot")
    def test_detect_player_4(self, screenshot):
        screenshot.return_value = Image.open("resources/session-yellow-red/Image-208.png").crop((10, 56, 777, 535))

        sensor.capture()

        player = sensor.detect_player()

        self.assertAlmostEqual(player, -0.53, delta=0.05)
