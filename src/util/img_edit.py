import cv2
import numpy as np

import properties


def draw_player_area():
    def edit(image: np.ndarray):
        cv2.circle(image, properties.EXPECTED_CENTER[::-1], properties.EXPECTED_PLAYER_AREA_RADIUS, properties.SCREENSHOT_EDIT_RAYS_COLOR, 1)
        return image

    return edit


def draw_safe_area():
    def edit(image: np.ndarray):
        cv2.circle(image, properties.EXPECTED_CENTER[::-1], properties.BRAIN_MINIMAL_SPACE, properties.SCREENSHOT_EDIT_PLAYER_COLOR, 1)
        return image

    return edit


def draw_player(contour):
    def edit(image: np.ndarray):
        cv2.drawContours(
            image, [contour + [properties.EXPECTED_PLAYER_AREA[1], properties.EXPECTED_PLAYER_AREA[0]]], 0, properties.SCREENSHOT_EDIT_PLAYER_COLOR, 1
        )
        return image

    return edit


def draw_rays(center, distances):
    def edit(image: np.ndarray):
        for ray, d in enumerate(distances):
            ray_start = center + np.int_(
                np.array(
                    [
                        properties.SENSOR_RAY_START_ITERATION * properties.SENSOR_RAY_PIXEL_SKIP * np.cos(ray * 2 * np.pi / properties.SENSOR_RAY_AMOUNT),
                        -properties.SENSOR_RAY_START_ITERATION * properties.SENSOR_RAY_PIXEL_SKIP * np.sin(ray * 2 * np.pi / properties.SENSOR_RAY_AMOUNT),
                    ]
                )
            )

            ray_end = center + np.int_(
                np.array(
                    [
                        d * np.cos(ray * 2 * np.pi / properties.SENSOR_RAY_AMOUNT),
                        -d * np.sin(ray * 2 * np.pi / properties.SENSOR_RAY_AMOUNT),
                    ]
                )
            )

            cv2.line(image, np.flip(ray_start), np.flip(ray_end), properties.SCREENSHOT_EDIT_RAYS_COLOR)
        return image

    return edit


def draw_player_rotation(position, direction):
    def edit(image: np.ndarray):

        position_from_x_axis = (position + 1.5) % 2
        cv2.ellipse(
            image,
            properties.EXPECTED_CENTER[::-1],
            (properties.EXPECTED_PLAYER_AREA_RADIUS - 2, properties.EXPECTED_PLAYER_AREA_RADIUS - 2),
            0,
            position_from_x_axis * 180,
            (position_from_x_axis + direction) * 180,
            properties.SCREENSHOT_EDIT_PLAYER_COLOR,
            1,
        )
        return image

    return edit
