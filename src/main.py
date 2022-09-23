import logging
from pathlib import Path

from core import sensor
from util.profiling import timeit


@timeit(name="loop", print_each_call=True)
def loop():
    """
    1. Find player
    2. Find distance from obstacles in all directions based
    3. Send rotation to motor
    :return:
    """

    sensor.capture()


if __name__ == "__main__":
    logs_folder = Path("logs")
    if not logs_folder.exists():
        logs_folder.mkdir()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=[logging.FileHandler("logs/super-hexabot.log", mode="w")])
    logger = logging.getLogger(__name__)

    sensor.calibrate()

    while True:
        loop()
