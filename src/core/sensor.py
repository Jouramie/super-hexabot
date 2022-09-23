import logging
import os
from datetime import datetime
from pathlib import Path

import pyautogui
import pyscreeze
import win32gui
from PIL.Image import Image

import properties

logger = logging.getLogger(__name__)


_game_position: pyscreeze.Box | None = None
_game: Image | None = None


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
    global _game
    if _game_position is None or _game_position.left < 0:
        logger.info(f"Sensor requires calibration. Game located at {_game_position}")
        return None

    _game = pyautogui.screenshot(region=_game_position)
    logger.debug(f"Screenshot size is {_game.size}.")
    if properties.SCREENSHOT_LOGGING_ENABLED:
        log_screenshot(_game)


def detect_player() -> float:
    """
    Find player orientation.
    :return: The orientation of the player between -1 and 1 where 0 is up.
    """
    pass


def detect_obstacle_distances():
    """
    Shoot rays in equally split directions
    :return:
    """
    pass
