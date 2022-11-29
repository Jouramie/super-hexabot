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
_mask: np.ndarray | None = None


@dataclass(frozen=True)
class ColorBoundary:
    color: str
    lower_bound: np.array
    upper_bound: np.array


color_boundary = ColorBoundary("red", np.array([0, 150, 160]), np.array([255, 255, 255]))


class NoPlayerFoundException(Exception):
    pass


def calibrate() -> None:
    """
    Basically find the game window and save it.
    """
    global _game_position
    window = find_window_region(properties.GAME_WINDOW_TITLE)
    set_calibration(window)
    logger.info(f"Game located at {repr(_game_position)}.")


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


def set_calibration(window: pyscreeze.Box) -> None:
    global _game_position
    _game_position = pyscreeze.Box(
        window.left + properties.GAME_WINDOW_WITHOUT_MARGIN[0],
        window.top + properties.GAME_WINDOW_WITHOUT_MARGIN[1],
        properties.GAME_WINDOW_WITHOUT_MARGIN[2],
        properties.GAME_WINDOW_WITHOUT_MARGIN[3],
    )


def capture() -> None:
    """
    Take a screenshot of the game region and cache it.
    :return:
    """
    global _game_position
    global _image

    if _game_position is None or _game_position.left < 0:
        logger.info(f"Sensor requires calibration. Game located at {_game_position}")
        return

    set_capture(pyautogui.screenshot(region=_game_position))
    logger.debug(f"Screenshot size is {_image.size}.")
    if properties.SCREENSHOT_LOGGING_ENABLED:
        log_screenshot(_image)


def log_screenshot(screenshot: Image):
    screenshot.save(Path(f"{properties.LOGS_PATH}/{datetime.now().replace().isoformat().replace(':', '')}.tiff"))

    saved_screenshots = os.listdir(properties.LOGS_PATH)

    if len(saved_screenshots) > properties.SAVED_SCREENSHOT_QUANTITY:
        os.remove(Path(f"{properties.LOGS_PATH}/{sorted(saved_screenshots)[0]}"))


def set_capture(screenshot: Image):
    global _image
    global _mask
    _image = screenshot
    _mask = None


def detect_player() -> float:
    """
    Find player orientation.
    :return: The orientation of the player between -1 and 1 where 0 is up.
    """
    global _mask
    if _mask is None:
        apply_mask()

    assert isinstance(_mask, np.ndarray)

    mark_player_cut = _mask[
        properties.EXPECTED_PLAYER_AREA[0] : properties.EXPECTED_PLAYER_AREA[2], properties.EXPECTED_PLAYER_AREA[1] : properties.EXPECTED_PLAYER_AREA[3]
    ]

    cnts = cv2.findContours(mark_player_cut, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    image_number = 0
    pos = []
    for c in cnts:
        approx = cv2.approxPolyDP(c, 0.07 * cv2.arcLength(c, True), True)
        area = cv2.contourArea(c)
        if len(approx) == 3 and properties.PLAYER_MIN_SIZE < area < properties.PLAYER_MAX_SIZE:
            image_number += 1
            moments = cv2.moments(approx)
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])
            pos.append(np.array([cy + properties.EXPECTED_PLAYER_AREA[0], cx + properties.EXPECTED_PLAYER_AREA[1]]))

    if not pos:
        raise NoPlayerFoundException()

    if len(pos) > 1:
        print(f"Found {image_number} that could be player. Will use the first one.")

    from_center = pos[0] - properties.EXPECTED_CENTER
    angle = np.angle(from_center[0] + from_center[1] * 1j) / np.pi
    return 1 - angle if angle > 0 else -1 - angle


def detect_available_distances() -> list[int]:
    """
    Shoot rays in equally split directions
    :return: A list of the available space in different directions, starting from the bottom, going clockwise.
    """
    global _mask
    if _mask is None:
        apply_mask()

    assert isinstance(_mask, np.ndarray)

    distances = []
    center = np.array(properties.EXPECTED_CENTER)
    for ray in range(properties.RAY_AMOUNT):
        position = center
        for i in range(properties.RAY_START_ITERATION, properties.RAY_MAX_ITERATION):
            position = center + np.int_(
                np.array(
                    [
                        i * properties.RAY_PIXEL_SKIP * np.cos(np.deg2rad(ray / properties.RAY_AMOUNT * 360)),
                        -i * properties.RAY_PIXEL_SKIP * np.sin(np.deg2rad(ray / properties.RAY_AMOUNT * 360)),
                    ]
                )
            )

            if _mask.shape[0] < position[0] or _mask.shape[1] < position[1]:
                break

            if _mask[position[0], position[1]] == 255:
                break

        distances.append(int(np.linalg.norm(position - center)))

    return distances


def apply_mask():
    global _image
    global _mask
    image = np.array(_image)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    _mask = cv2.inRange(hsv, color_boundary.lower_bound, color_boundary.upper_bound)
