import threading
import time

import keyboard

import properties

_lock = threading.Lock()
_thread: None | threading.Thread = None
_running = True

_destination = 0
_last_direction: None | str = None


def turn(rotation: float):
    """
    positive is right, negative is left
    """
    global _destination
    with _lock:
        _destination = rotation


def start():
    global _thread

    def run():
        global _running
        while _running:
            loop()

    _thread = threading.Thread(target=run)
    _thread.start()


def stop():
    global _running
    _running = False


def loop():
    """
    Just press right or left if the number is positive or negative, amount does not really matter.

    positive is right, negative is left
    """
    global _last_direction
    global _destination
    rotation = _destination

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

    time_to_sleep = abs(rotation) / properties.MOTOR_SPEED
    if time_to_sleep > properties.MOTOR_MAX_SLEEP or time_to_sleep == 0:
        time_to_sleep = properties.MOTOR_MAX_SLEEP

    ts = time.time_ns()
    time.sleep(time_to_sleep)
    te = time.time_ns()
    delta = (te - ts) / 1e9
    if new_direction == "left":
        delta = -delta

    turn(rotation - delta * properties.MOTOR_SPEED)

    _last_direction = new_direction
