import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import pyautogui
import pyscreeze
import win32gui
from PIL.Image import Image

import properties

logger = logging.getLogger(__name__)


_game_position: pyscreeze.Box | None = None
_image: Image | None = None


@dataclass(frozen=True)
class ColorBoundary:
    color: str
    lower_bound: np.array
    upper_bound: np.array


color_boundary = ColorBoundary("red", np.array([0, 150, 160]), np.array([255, 255, 255]))


def find_window_region(title) -> pyscreeze.Box | None:
    # activate_window(title)

    possible_game_windows = [window.title for window in pyautogui.getWindowsWithTitle(title)]
    logger.info(f"Found {len(possible_game_windows)} possible game windows: {possible_game_windows}.")

    actual_game_window = title if title in possible_game_windows else possible_game_windows[0]

    try:
        window_handle = win32gui.FindWindow(None, actual_game_window)
        win_region = win32gui.GetWindowRect(window_handle)
    except Exception as e:
        return None

    return pyscreeze.Box(win_region[0], win_region[1], win_region[2] - win_region[0], win_region[3] - win_region[1])


def log_screenshot(screenshot: Image):
    screenshot.save(Path(f"logs/{datetime.now().replace().isoformat().replace(':', '')}.tiff"))

    saved_screenshots = os.listdir("logs")

    if len(saved_screenshots) > properties.SAVED_SCREENSHOT_QUANTITY:
        os.remove(Path(f"logs/{sorted(saved_screenshots)[0]}"))


def calibrate() -> None:
    """
    Basically find the game window and save it.
    """
    global _game_position
    window = find_window_region(properties.GAME_WINDOW_TITLE)
    _game_position = pyscreeze.Box(
        window.left + properties.GAME_WINDOW_WITHOUT_MARGIN[0],
        window.top + properties.GAME_WINDOW_WITHOUT_MARGIN[1],
        properties.GAME_WINDOW_WITHOUT_MARGIN[2],
        properties.GAME_WINDOW_WITHOUT_MARGIN[3],
    )
    logger.info(f"Game located at {repr(_game_position)}.")


def capture() -> None:
    """
    Take a screenshot of the game region and cache it.
    :return:
    """
    global _image
    if _game_position is None or _game_position.left < 0:
        logger.info(f"Sensor requires calibration. Game located at {_game_position}")
        return None

    _image = pyautogui.screenshot(region=_game_position)
    logger.debug(f"Screenshot size is {_image.size}.")
    if properties.SCREENSHOT_LOGGING_ENABLED:
        log_screenshot(_image)


def detect_player() -> float:
    """
    Find player orientation.
    :return: The orientation of the player between -1 and 1 where 0 is up.
    """
    global _image

    image = np.array(_image)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, color_boundary.lower_bound, color_boundary.upper_bound)

    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    image_number = 0
    for c in cnts:
        area = cv2.contourArea(c)
        if properties.PLAYER_MIN_SIZE <= area < properties.PLAYER_MAX_SIZE:
            print(area)
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(mask, (x, y), (x + w, y + h), (127, 127, 127), 1)
            image_number += 1

    print(f"Found {image_number} that could be player")

    return 0


def detect_obstacle_distances():
    """
    Shoot rays in equally split directions
    :return:
    """
    pass
