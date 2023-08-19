import logging
import multiprocessing as mp
import time

import keyboard

import properties
from main import ElapsedFormatter

logger = logging.getLogger(__name__)

_lock = mp.Lock()
_process: None | mp.Process = None
_running = mp.Value("i", 1)

_unsafe = mp.Value("i", 0)
_destination: mp.Value = mp.Value("d", 0)
_destination_timestamp = mp.Value("i", 0)

_last_direction: None | str = None


def turn(unsafe: bool, rotation: float):
    """
    positive is right, negative is left
    """
    global _destination
    global _destination_timestamp
    with _lock:
        logger.info(f"Setting rotation to {rotation}")
        _destination.value = rotation
        _unsafe.value = int(unsafe)
        _destination_timestamp.value = time.perf_counter_ns()


def unstuck():
    global _destination
    global _destination_timestamp
    logger.warning(f"Trying to unstuck cursor from wall!!!")
    if _destination.value < 0:
        turn(False, properties.MOTOR_MIN_ROTATION)
    else:
        turn(False, -properties.MOTOR_MIN_ROTATION)


def start():
    global _process
    keyboard.press("space")
    time.sleep(0.15)
    keyboard.release("space")

    _process = mp.Process(target=run, daemon=True, args=(_destination, _destination_timestamp, _running))
    _process.start()


def run(destination, destination_timestamp, running):
    global _destination, _destination_timestamp, _running, logger
    _destination, _destination_timestamp, _running = destination, destination_timestamp, running

    handler = logging.FileHandler("logs/super-hexabot-motor.log", mode="w")
    handler.setFormatter(ElapsedFormatter())
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=[handler])
    logger = logging.getLogger(__name__)

    while _running.value:
        loop()


def stop():
    global _running
    _running.value = False


def loop():
    """
    Just press right or left if the number is positive or negative, amount does not really matter.

    positive is right, negative is left
    """
    global _last_direction
    global _destination
    global _destination_timestamp
    rotation = _destination.value
    unsafe = _unsafe.value
    current_destination_timestamp = _destination_timestamp.value

    new_direction = None
    if rotation <= -properties.MOTOR_MIN_ROTATION:
        new_direction = "left"

    if rotation >= properties.MOTOR_MIN_ROTATION:
        new_direction = "right"

    keyboard.release("left")
    keyboard.release("right")

    if new_direction is None:
        ts = time.perf_counter_ns()
        time.sleep(properties.MOTOR_SMALL_SLEEP)
        te = time.perf_counter_ns()
        time_slept = (te - ts) / 1e9
        logger.info(f"  Not turning, slept for {time_slept}. Expected {properties.MOTOR_SMALL_SLEEP}.")
        return

    keyboard.press(new_direction)
    _last_direction = new_direction

    time_to_sleep = abs(rotation) / properties.MOTOR_SPEED
    logger.info(f"  Turning {new_direction} for {rotation} during {time_to_sleep}.")
    if abs(rotation) > properties.MOTOR_LARGE_ROTATION:
        time_to_sleep = properties.MOTOR_LONG_SLEEP
    elif unsafe and time_to_sleep > properties.MOTOR_SMALL_SLEEP * 2:
        time_to_sleep = properties.MOTOR_SMALL_SLEEP * 2
    elif time_to_sleep > properties.MOTOR_SMALL_SLEEP or time_to_sleep == 0:
        time_to_sleep = properties.MOTOR_SMALL_SLEEP

    ts = time.perf_counter_ns()
    time.sleep(time_to_sleep)

    te = time.perf_counter_ns()
    time_slept = (te - ts) / 1e9
    delta = time_slept * properties.MOTOR_SPEED
    if new_direction == "left":
        delta = -delta

    logger.info(f"  Actually turned of {delta} during {time_slept}. Expected {time_to_sleep}.")
    if current_destination_timestamp == _destination_timestamp.value:
        with _lock:
            logger.info(f"Continue same rotation.")
            _destination.value = rotation - delta
