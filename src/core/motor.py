import keyboard

import properties

_last_direction: None | str = None


def turn(rotation: float):
    """
    Just press right or left if the number is positive or negative, amount does not really matter.

    positive is right, negative is left
    """

    global _last_direction

    new_direction = None
    if rotation < -properties.MOTOR_MIN_ROTATION:
        new_direction = "left"

    if rotation > properties.MOTOR_MIN_ROTATION:
        new_direction = "right"

    if _last_direction != new_direction:
        if _last_direction is not None:
            keyboard.release(_last_direction)

        if new_direction is not None:
            keyboard.press(new_direction)

    _last_direction = new_direction
