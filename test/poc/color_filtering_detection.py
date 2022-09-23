import os
from dataclasses import dataclass

import cv2
import numpy as np

for filename in os.listdir("../../target"):
    file_path = f"target/{filename}"
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
    except Exception as e:
        print("Failed to delete %s. Reason: %s" % (file_path, e))

top_left_corner = (56, 10)
bottom_right_corner = (535, 777)

images_directory = "session-yellow-red"


@dataclass(frozen=True)
class ColorBoundary:
    color: str
    lower_bound: np.array
    upper_bound: np.array


color_boundary = ColorBoundary("red", np.array([0, 150, 160]), np.array([255, 255, 255]))


def searching_obstacles(__image_name: str):
    print(f"Searching obstacles in {__image_name}.")

    # Load image, grayscale, median blur, sharpen image
    image = cv2.imread(f"../resources/{images_directory}/{__image_name}")[
        top_left_corner[0] : bottom_right_corner[0], top_left_corner[1] : bottom_right_corner[1]
    ]

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, color_boundary.lower_bound, color_boundary.upper_bound)

    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    min_area = 20
    max_area = 80
    image_number = 0
    for c in cnts:
        area = cv2.contourArea(c)
        if min_area <= area < max_area:
            print(area)
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(mask, (x, y), (x + w, y + h), (127, 127, 127), 1)
            image_number += 1

    cv2.imwrite(f"../../target/{images_directory}/{__image_name}", mask)


os.makedirs(f"../../target/{images_directory}", exist_ok=True)

# searching_obstacles("Image-025.png")

for __image_name in os.listdir(f"../resources/{images_directory}"):
    searching_obstacles(__image_name)
