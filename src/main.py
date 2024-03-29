import logging
import time
from pathlib import Path

import properties
from core import sensor, brain, motor
from core.sensor import NoPlayerFoundException
from util import img_logger, img_edit
from util.log_formatter import ElapsedFormatter
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
        position, distance = sensor.detect_player()
        _detections_without_finding_player = 0
    except NoPlayerFoundException as e:
        logger.warning("I don't see the cursor !")
        sensor.clear()
        _detections_without_finding_player += 1
        if _detections_without_finding_player > properties.MAX_PLAYER_LOST:
            raise e
        motor.unstuck()
        sensor.clear()
        return
    available_distances = sensor.detect_available_distances()
    unsafe, direction = brain.choose_direction(position, distance, available_distances)
    motor.turn(unsafe, direction)

    img_logger.edit(img_edit.draw_player_rotation(position, direction, unsafe))
    img_logger.edit(img_edit.draw_safe_area(distance))
    img_logger.edit(img_edit.draw_unsafe_area(distance))

    sensor.clear()


if __name__ == "__main__":
    logs_folder = Path("logs")
    if not logs_folder.exists():
        logs_folder.mkdir()

    handler = logging.FileHandler("logs/super-hexabot.log", mode="w")
    formatter = ElapsedFormatter()
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=[handler])
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
        img_logger.start()
        motor.start()
        formatter.start()

        time.sleep(0.2)
        while properties.MOVEMENT_ENABLED:
            loop()
    finally:
        sensor.stop()
        motor.stop()
        img_logger.finalize()
