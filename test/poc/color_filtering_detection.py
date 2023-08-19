import os
from dataclasses import dataclass

import cv2
import numpy as np

import properties

for filename in os.listdir("../../target"):
    file_path = f"target/{filename}"
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
    except Exception as e:
        print("Failed to delete %s. Reason: %s" % (file_path, e))

top_left_corner = (56, 10)
bottom_right_corner = (535, 777)

images_directory = "hexagon"


@dataclass(frozen=True)
class ColorBoundary:
    color: str
    lower_bound: np.array
    upper_bound: np.array


color_boundary = ColorBoundary("red", np.array([0, 150, 160]), np.array([255, 255, 255]))


def searching_obstacles(__image_name: str, verbose=False):
    print(f"Searching obstacles in {__image_name}.")

    # Load image, grayscale, median blur, sharpen image
    image = cv2.imread(f"../resources/{images_directory}/{__image_name}")[
        top_left_corner[0] : bottom_right_corner[0], top_left_corner[1] : bottom_right_corner[1]
    ]

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color_boundary.lower_bound, color_boundary.upper_bound)

    mark_player_cut = mask[
        properties.EXPECTED_PLAYER_AREA[0] : properties.EXPECTED_PLAYER_AREA[2], properties.EXPECTED_PLAYER_AREA[1] : properties.EXPECTED_PLAYER_AREA[3]
    ]
    if verbose:
        print(cv2.imwrite(f"../../target/mask.png", mask))

    cnts = cv2.findContours(mark_player_cut, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    image_number = 0
    for c in cnts:
        approx = cv2.approxPolyDP(c, 0.07 * cv2.arcLength(c, True), True)
        area = cv2.contourArea(c)
        if len(approx) == 3 and properties.PLAYER_MIN_SIZE < area < properties.PLAYER_MAX_SIZE:
            cv2.drawContours(image, [c + [properties.EXPECTED_PLAYER_AREA[1], properties.EXPECTED_PLAYER_AREA[0]]], 0, (255, 0, 255), 1)
            image_number += 1

    center = np.array(properties.EXPECTED_CENTER)
    for ray in range(properties.SENSOR_RAY_AMOUNT):
        position = center
        for i in range(properties.SENSOR_RAY_START_ITERATION, properties.SENSOR_RAY_MAX_ITERATION):
            position = center + np.int_(
                np.array(
                    [
                        i * properties.SENSOR_RAY_PIXEL_SKIP * np.cos(np.deg2rad(ray / properties.SENSOR_RAY_AMOUNT * 360)),
                        -i * properties.SENSOR_RAY_PIXEL_SKIP * np.sin(np.deg2rad(ray / properties.SENSOR_RAY_AMOUNT * 360)),
                    ]
                )
            )

            if mask.shape[0] < position[0] or mask.shape[1] < position[1]:
                break

            if mask[position[0], position[1]] == 255:
                break

        cv2.line(image, np.flip(center), np.flip(position), (255, 0, 255))

        if ray == 16:
            break

    print(f"Found {image_number}")
    cv2.imwrite(f"../../target/{images_directory}/{__image_name}", image)


os.makedirs(f"../../target/{images_directory}", exist_ok=True)

searching_obstacles("Image-221.png", True)

# for __image_name in os.listdir(f"../resources/{images_directory}"):
#    searching_obstacles(__image_name)
