import sys

from loguru import logger

logger.add(
    "logs/debug.log",
    format="[{time:YYYY-MM-DD HH:mm:ss}] {level} | {message}",
    level="DEBUG",
    rotation="1 MB",
    colorize=False,
)
logger.add(sys.__stdout__, level="INFO", colorize=True)
