import logging
from collections import namedtuple
from dataclasses import dataclass

import cv2
import dxcam
import numpy as np
import pyautogui
import win32gui

import properties
from util import img_logger, img_edit
from util.profiling import timeit

logger = logging.getLogger(__name__)

BLUR_SIZE = int(properties.SENSOR_RAY_AMOUNT / properties.SENSOR_BLUR_RATIO)
CONVOLUTION_MATRIX = np.array([1 / BLUR_SIZE] * BLUR_SIZE)

Region = namedtuple("Region", ["left", "top", "right", "bottom"])


_game_position: Region | None = None
_image: np.ndarray | None = None
_mask: np.ndarray | None = None
_player_distance: int | None = None
_camera: dxcam.DXCamera | None = None


@dataclass(frozen=True)
class ColorBoundary:
    color: str
    lower_bound: np.array
    upper_bound: np.array


color_boundary = ColorBoundary("red", np.array([0, 65, 150]), np.array([255, 255, 255]))


class NoPlayerFoundException(Exception):
    pass


def calibrate() -> None:
    """
    Basically find the game window and save it.
    """
    global _game_position
    global _camera
    window = find_window_region_on_left_screen(properties.GAME_WINDOW_TITLE)
    set_calibration(window)
    logger.info(f"Game located at {repr(_game_position)}.")

    _camera = dxcam.create(output_idx=1)
    _camera.start(_game_position)


def stop() -> None:
    if _camera is not None:
        _camera.release()


def find_window_region_on_left_screen(title) -> Region | None:
    # activate_window(title)

    possible_game_windows = [window.title for window in pyautogui.getWindowsWithTitle(title)]
    logger.info(f"Found {len(possible_game_windows)} possible game windows: {possible_game_windows}.")

    actual_game_window = title if title in possible_game_windows else possible_game_windows[0]

    try:
        window_handle = win32gui.FindWindow(None, actual_game_window)
        win_region = win32gui.GetWindowRect(window_handle)
        logger.info(f"Raw window  {win_region}")
    except Exception as e:
        return None

    return Region(
        win_region[0] - properties.SCREEN_OFFSET[0],
        win_region[1] - properties.SCREEN_OFFSET[1],
        win_region[2] - properties.SCREEN_OFFSET[0],
        win_region[3] - properties.SCREEN_OFFSET[1],
    )


def set_calibration(window: Region) -> None:
    global _game_position
    _game_position = Region(
        window.left + properties.GAME_WINDOW_WITHOUT_MARGIN[0],
        window.top + properties.GAME_WINDOW_WITHOUT_MARGIN[1],
        window.left + properties.GAME_WINDOW_WITHOUT_MARGIN[2],
        window.top + properties.GAME_WINDOW_WITHOUT_MARGIN[3],
    )


@timeit(name="capture", print_each_call=True)
def capture() -> None:
    """
    Take a screenshot of the game region and cache it.
    :return:
    """
    global _game_position
    global _image

    if _game_position is None:
        logger.info(f"Sensor requires calibration. Game located at {_game_position}")
        return

    grab = _camera.get_latest_frame()
    if grab is None:
        return
    set_capture(grab)
    logger.debug(f"Screenshot size is {_image.size}.")
    img_logger.submit(_image)


def clear() -> None:
    global _image
    img_logger.publish()
    _image = None


def set_capture(screenshot: np.ndarray):
    global _image
    global _mask
    _image = screenshot
    _mask = None


def detect_player() -> (float, int):
    """
    Find player orientation.
    :return: The orientation of the player between -1 and 1 where 0 is up.
    """
    global _mask
    global _player_distance
    if _mask is None:
        apply_mask()

    assert isinstance(_mask, np.ndarray)

    mask_player_cut = crop_circle_center(_mask)

    img_logger.edit(img_edit.draw_player_area())

    cnts = find_all_contours(mask_player_cut)

    image_number = 0
    pos = []
    for c in cnts:
        approx = cv2.approxPolyDP(c, 0.07 * cv2.arcLength(c, True), True)
        area = cv2.contourArea(c)
        # log_screenshot(debug)
        if len(approx) == 3 and properties.PLAYER_MIN_SIZE < area < properties.PLAYER_MAX_SIZE:
            image_number += 1
            centroid = compute_centroid(approx)
            pos.append(
                np.array([centroid[1], centroid[0]])
                + np.array([properties.EXPECTED_PLAYER_AREA[0], properties.EXPECTED_PLAYER_AREA[1]])
            )

            img_logger.edit(img_edit.draw_player(c))

    if not pos:
        raise NoPlayerFoundException()

    if len(pos) > 1:
        print(f"Found {image_number} that could be player. Will use the first one.")

    from_center = pos[0] - properties.EXPECTED_CENTER
    _player_distance = int(np.linalg.norm(from_center))
    angle = np.angle(from_center[0] + from_center[1] * 1j) / np.pi
    return 1 - angle if angle > 0 else -1 - angle, _player_distance


def compute_centroid(contour):
    moments = cv2.moments(contour)
    cx = int(moments["m10"] / moments["m00"])
    cy = int(moments["m01"] / moments["m00"])
    return np.array([cx, cy])


def find_all_contours(mask_player_cut):
    cnts = cv2.findContours(mask_player_cut, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return cnts[0] if len(cnts) == 2 else cnts[1]


def crop_circle_center(_mask):
    mask_player_cut = _mask[
        properties.EXPECTED_PLAYER_AREA[0] : properties.EXPECTED_PLAYER_AREA[2],
        properties.EXPECTED_PLAYER_AREA[1] : properties.EXPECTED_PLAYER_AREA[3],
    ]
    mask_player_circle = np.ones_like(mask_player_cut) * 255
    mask_player_circle = cv2.circle(
        mask_player_circle,
        (properties.EXPECTED_PLAYER_AREA_RADIUS, properties.EXPECTED_PLAYER_AREA_RADIUS),
        properties.EXPECTED_PLAYER_AREA_RADIUS,
        (0, 0, 0),
        cv2.FILLED,
    )
    mask_player_cut = cv2.subtract(mask_player_cut, mask_player_circle)
    return mask_player_cut


@timeit(name="walls", print_each_call=True)
def detect_available_distances() -> list[int]:
    """
    Shoot rays in equally split directions
    :return: A list of the available space in different directions, starting from the bottom, going clockwise.
    """
    global _mask
    global _player_distance
    if _mask is None:
        apply_mask()

    assert isinstance(_mask, np.ndarray)

    distances = []
    center = np.array(properties.EXPECTED_CENTER)
    ray_start_i = int(_player_distance / properties.SENSOR_RAY_PIXEL_SKIP) + properties.SENSOR_RAY_PLAYER_MARGIN
    for ray in range(properties.SENSOR_RAY_AMOUNT):
        position = center
        wall = False
        for i in range(ray_start_i, properties.SENSOR_RAY_MAX_ITERATION):
            position = center + np.int_(
                np.array(
                    [
                        i * properties.SENSOR_RAY_PIXEL_SKIP * np.cos(ray * 2 * np.pi / properties.SENSOR_RAY_AMOUNT),
                        -i * properties.SENSOR_RAY_PIXEL_SKIP * np.sin(ray * 2 * np.pi / properties.SENSOR_RAY_AMOUNT),
                    ]
                )
            )

            if _mask.shape[0] <= position[0] or _mask.shape[1] <= position[1]:
                break

            if _mask[position[0], position[1]] == 255:
                if i == ray_start_i:
                    wall = True
                break

        if wall:
            distances.append(properties.SENSOR_IMPOSSIBLE_WALL)
        else:
            distances.append(int(np.linalg.norm(position - center)))

    if properties.SENSOR_APPLY_BLUR:
        padding = len(CONVOLUTION_MATRIX) - 1
        distances_for_blur = [d if d != -1 else ray_start_i * properties.SENSOR_RAY_PIXEL_SKIP for d in distances]
        array_with_padding = np.array(distances_for_blur[-padding:] + distances_for_blur + distances_for_blur[:padding])
        convolve = np.convolve(array_with_padding, CONVOLUTION_MATRIX, "same")
        distances = [d if distances[i] != -1 else -1 for i, d in enumerate(list(np.int_(convolve))[padding:-padding])]

    img_logger.edit(img_edit.draw_rays(center, ray_start_i, distances))

    return distances


def apply_mask():
    global _image
    global _mask
    image = np.array(_image)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    _mask = cv2.inRange(hsv, color_boundary.lower_bound, color_boundary.upper_bound)
