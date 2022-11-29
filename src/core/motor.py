import pyautogui

import properties


def turn(rotation: float):
    """
    Just press right or left if the number is positive or negative, amount does not really matter.

    positive is right, negative is left
    """

    pyautogui.keyUp("left")
    pyautogui.keyUp("right")

    if rotation < -properties.MOTOR_MIN_ROTATION:
        pyautogui.keyDown("left")

    if rotation > properties.MOTOR_MIN_ROTATION:
        pyautogui.keyDown("right")
