import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s", handlers=[logging.FileHandler("logs/hanabot.log", mode="w")])
    logging.getLogger("console").setLevel(logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("bye bye")
