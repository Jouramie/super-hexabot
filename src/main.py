import logging
import time
from pathlib import Path

import properties
from core import sensor, brain, motor
from core.sensor import NoPlayerFoundException
from util.profiling import timeit

_detections_without_finding_player = 0


@timeit(name="loop", print_each_call=True)
def loop():
    """
    1. Find player
    2. Find distance from obstacles in all directions based
    3. Send rotation to motor
    :return:
    """
    global _detections_without_finding_player

    sensor.capture()
    try:
        position = sensor.detect_player()
        _detections_without_finding_player = 0
    except NoPlayerFoundException as e:
        logger.warning("I don't see the cursor !")
        _detections_without_finding_player += 1
        if _detections_without_finding_player > 3:
            raise e
        return
    available_distances = sensor.detect_available_distances()
    direction = brain.choose_direction(position, available_distances)
    motor.turn(direction)


if __name__ == "__main__":
    logs_folder = Path("logs")
    if not logs_folder.exists():
        logs_folder.mkdir()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=[logging.FileHandler("logs/super-hexabot.log", mode="w")])
    logger = logging.getLogger(__name__)

    sensor.calibrate()

    print("Starting the bot in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("Start !")
    try:
        motor.start()

        time.sleep(1)
        sensor.calculate_speed()
        while properties.MOVEMENT_ENABLED:
            loop()
    finally:
        sensor.stop()
        motor.stop()
