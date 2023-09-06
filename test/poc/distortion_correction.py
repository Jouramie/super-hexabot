import os

import cv2
import numpy as np
from PIL import Image

import properties
from core import sensor

properties.SCREENSHOT_LOGGER_ENABLED = False
from util import img_logger, img_edit

images_folder = "test/resources/hexagoner"
test_images = [(img, np.array(Image.open(images_folder + "/" + img))) for img in os.listdir(images_folder)]


def run_distortion_correction():
    """
    Instead of calculating the approximation of the hexagon, another idea could be to follow the pattern of the
    pixelated sides of the hexagon to find the 6 lines best representing the hexagon. Finding the intersection of those
    lines will then give the 6 corners of the hexagon, from which we can calculate the distortion matrix.
    """
    for name, img in test_images:
        sensor._image = img
        sensor.apply_mask()
        mask = sensor._mask
        img_logger.log_now(mask, "mask" + name)
        cnts, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        log = img
        hole = None
        for i, c in enumerate(cnts):
            area = cv2.contourArea(c)
            if hierarchy[0][i][3] != -1 and area > 100:
                hole = c
                break

        if hole is None:
            print(f"Found no hole in {name}...")
            continue

        centroid = sensor.compute_centroid(hole)
        approx = cv2.approxPolyDP(hole, 0.04 * cv2.arcLength(hole, True), True)
        scaled = approx * 2

        log = img_edit.draw_contours([hole], (255, 0, 0))(log)
        print(f"Found center of {name} at {centroid}")

        img_logger.log_now(log, name)


if __name__ == "__main__":
    run_distortion_correction()
