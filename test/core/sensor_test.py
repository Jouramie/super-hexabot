from unittest import TestCase
from unittest.mock import patch

from PIL import Image
from pyscreeze import Box

import properties
from core import sensor

properties.LOGS_PATH = "../logs"
properties.SCREENSHOT_LOGGING_ENABLED = False
properties.SENSOR_RAY_MAX_ITERATION = 50
properties.SENSOR_RAY_AMOUNT = 24


class TestDetection(TestCase):
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

    @patch("pyautogui.screenshot")
    def test_detect_obstacles_without_blur(self, screenshot):
        properties.SENSOR_APPLY_BLUR = False
        screenshot.return_value = Image.open("resources/session-yellow-red/Image-047.png").crop((10, 56, 777, 535))

        sensor.capture()

        obstacles = sensor.detect_available_distances()

        self.assertEqual(len(obstacles), properties.SENSOR_RAY_AMOUNT)
        self.assertAlmostEqual(obstacles[0], 240, delta=10)
        self.assertAlmostEqual(obstacles[1], 249, delta=10)
        self.assertAlmostEqual(obstacles[2], 245, delta=10)
        self.assertAlmostEqual(obstacles[3], 82, delta=10)
        self.assertAlmostEqual(obstacles[4], 77, delta=10)
        self.assertAlmostEqual(obstacles[5], 80, delta=10)
        self.assertAlmostEqual(obstacles[6], 80, delta=10)
        self.assertAlmostEqual(obstacles[7], 243, delta=10)
        self.assertAlmostEqual(obstacles[8], 218, delta=10)
        self.assertAlmostEqual(obstacles[9], 204, delta=10)
        self.assertAlmostEqual(obstacles[10], 212, delta=10)
        self.assertAlmostEqual(obstacles[11], 73, delta=10)
        self.assertAlmostEqual(obstacles[12], 75, delta=10)
        self.assertAlmostEqual(obstacles[13], 72, delta=10)
        self.assertAlmostEqual(obstacles[14], 75, delta=10)
        self.assertAlmostEqual(obstacles[15], 247, delta=10)
        self.assertAlmostEqual(obstacles[16], 246, delta=10)
        self.assertAlmostEqual(obstacles[17], 250, delta=10)
        self.assertAlmostEqual(obstacles[18], 245, delta=10)
        self.assertAlmostEqual(obstacles[19], 80, delta=10)
        self.assertAlmostEqual(obstacles[20], 73, delta=10)
        self.assertAlmostEqual(obstacles[21], 72, delta=10)
        self.assertAlmostEqual(obstacles[22], 82, delta=10)
        self.assertAlmostEqual(obstacles[23], 248, delta=10)
