import logging
import time
from pathlib import Path

import properties
from core import sensor
from util import img_logger
from util.profiling import timeit


@timeit(name="loop", print_each_call=True)
def loop():

    sensor.capture()
    sensor.clear()
    time.sleep(0.5)


if __name__ == "__main__":
    logs_folder = Path("logs")
    if not logs_folder.exists():
        logs_folder.mkdir()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=[logging.FileHandler("logs/super-hexabot.log", mode="w")])
    logger = logging.getLogger(__name__)

    sensor.calibrate()

    print("Starting the capture in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("Start !")
    try:
        while properties.MOVEMENT_ENABLED:
            loop()
    finally:
        sensor.stop()
        img_logger.finalize()
