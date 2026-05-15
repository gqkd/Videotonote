import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(log_dir: str = "./logs") -> logging.Logger:
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, "app.log")
    logger = logging.getLogger("videotonotes")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str = "videotonotes") -> logging.Logger:
    return logging.getLogger(name)
