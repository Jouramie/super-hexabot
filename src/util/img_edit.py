import cv2
import numpy as np

import properties


def draw_player_area():
    def edit(image: np.ndarray):
        cv2.circle(
            image,
            properties.EXPECTED_CENTER[::-1],
            properties.EXPECTED_PLAYER_AREA_RADIUS,
            properties.SCREENSHOT_EDIT_RAYS_COLOR,
            1,
        )
        return image

    return edit


def draw_safe_area(distance):
    def edit(image: np.ndarray):
        cv2.circle(
            image,
            properties.EXPECTED_CENTER[::-1],
            distance + properties.BRAIN_MINIMAL_SPACE_OFFSET,
            properties.SCREENSHOT_EDIT_PLAYER_COLOR,
            1,
        )
        return image

    return edit


def draw_unsafe_area(distance):
    def edit(image: np.ndarray):
        cv2.circle(
            image,
            properties.EXPECTED_CENTER[::-1],
            distance + properties.BRAIN_UNSAFE_SPACE_OFFSET,
            properties.SCREENSHOT_EDIT_UNSAFE_COLOR,
            1,
        )
        cv2.circle(
            image,
            properties.EXPECTED_CENTER[::-1],
            distance + properties.BRAIN_UNSAFE_SPACE_OFFSET + properties.BRAIN_SAFE_MARGIN,
            properties.SCREENSHOT_EDIT_UNSAFE_COLOR,
            1,
        )
        return image

    return edit


def draw_player(contour):
    return draw_contours(
        [contour + [properties.EXPECTED_PLAYER_AREA[1], properties.EXPECTED_PLAYER_AREA[0]]],
        properties.SCREENSHOT_EDIT_PLAYER_COLOR,
    )


def draw_contours(contours, color):
    def edit(image: np.ndarray):
        cv2.drawContours(
            image,
            contours,
            0,
            color,
            1,
        )
        return image

    return edit


def draw_rays(center, ray_start_i, distances):
    def edit(image: np.ndarray):
        for ray, d in enumerate(distances):
            ray_start = center + np.int_(
                np.array(
                    [
                        ray_start_i
                        * properties.SENSOR_RAY_PIXEL_SKIP
                        * np.cos(ray * 2 * np.pi / properties.SENSOR_RAY_AMOUNT),
                        -ray_start_i
                        * properties.SENSOR_RAY_PIXEL_SKIP
                        * np.sin(ray * 2 * np.pi / properties.SENSOR_RAY_AMOUNT),
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


def draw_player_rotation(position, direction, unsafe):
    def edit(image: np.ndarray):

        position_from_x_axis = (position + 1.5) % 2
        cv2.ellipse(
            image,
            properties.EXPECTED_CENTER[::-1],
            (properties.EXPECTED_PLAYER_AREA_RADIUS - 2, properties.EXPECTED_PLAYER_AREA_RADIUS - 2),
            0,
            position_from_x_axis * 180,
            (position_from_x_axis + direction) * 180,
            properties.SCREENSHOT_EDIT_PLAYER_COLOR if not unsafe else properties.SCREENSHOT_EDIT_UNSAFE_COLOR,
            1,
        )
        return image

    return edit
