import pyautogui
import win32com.client as comclt

import properties
from util.profiling import timeit

_last_direction: None | str = None

wsh = comclt.Dispatch("WScript.Shell")


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
            pyautogui.keyUp(_last_direction)

        if new_direction is not None:
            pyautogui.keyDown(new_direction)

    _last_direction = new_direction


@timeit(name="press", print_each_call=True)
def press():

    wsh.AppActivate(properties.GAME_WINDOW_TITLE)  # select another application
    wsh.SendKeys("{LEFT}")  # send the keys you want


# press()
