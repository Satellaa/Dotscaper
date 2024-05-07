import logging
from logging.handlers import RotatingFileHandler


def setup_logger(name, log_file, level=logging.DEBUG):
    formatter = logging.Formatter(
        "%(asctime)s - %(funcName)s - %(levelname)s - %(message)s")
    handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=3)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())

    return logger
