from loguru import logger
import os
import sys


def setup_logger():
    level = os.getenv("LOG_LEVEL", "INFO")

    logger.remove()
    logger.add(
        sys.stdout,
        level=level,
        backtrace=False,
        diagnose=False,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    return logger


logger = setup_logger()
