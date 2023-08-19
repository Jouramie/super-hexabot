import logging
import threading
import time

import keyboard

import properties

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_thread: None | threading.Thread = None
_running = True

_destination = 0
_destination_timestamp = 0

_progress = 0
_last_direction: None | str = None


def turn(rotation: float):
    """
    positive is right, negative is left
    """
    global _destination
    global _destination_timestamp
    with _lock:
        logger.info(f"Setting rotation to {rotation}")
        _destination = rotation
        _destination_timestamp = time.perf_counter_ns()


def start():
    global _thread

    def run():
        global _running

        keyboard.press("left")
        time.sleep(0.5)
        keyboard.release("left")
        keyboard.press("right")
        time.sleep(0.5)
        keyboard.release("right")
        time.sleep(0.2)

        while _running:
            loop()

    _thread = threading.Thread(target=run, daemon=True)

    keyboard.press("space")
    time.sleep(0.05)
    keyboard.release("space")
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
    global _destination_timestamp
    rotation = _destination
    current_destination_timestamp = _destination_timestamp

    new_direction = None
    if rotation < -properties.MOTOR_MIN_ROTATION:
        new_direction = "left"

    if rotation > properties.MOTOR_MIN_ROTATION:
        new_direction = "right"

    keyboard.release("left")
    keyboard.release("right")

    if new_direction is not None:
        keyboard.press(new_direction)
        keyboard.release(new_direction)
        keyboard.press(new_direction)
    _last_direction = new_direction

    time_to_sleep = abs(rotation) / properties.MOTOR_SPEED
    logger.info(f"Turning {new_direction} for {rotation} during {time_to_sleep}.")
    if time_to_sleep > properties.MOTOR_MAX_SLEEP or time_to_sleep == 0:
        time_to_sleep = properties.MOTOR_MAX_SLEEP

    ts = time.perf_counter_ns()
    time.sleep(time_to_sleep)

    if new_direction is None:
        return

    te = time.perf_counter_ns()
    delta = (te - ts) / 1e9 * properties.MOTOR_SPEED
    if new_direction == "left":
        delta = -delta

    logger.info(f"Actually turned of {delta}.")
    if current_destination_timestamp == _destination_timestamp:
        with _lock:
            _destination = rotation - delta
