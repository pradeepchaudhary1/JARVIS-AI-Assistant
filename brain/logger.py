"""
JARVIS Production Logger
"""

from __future__ import annotations

from datetime import datetime
import logging
import os

LOG_FOLDER = "logs"
LOG_FILE = os.path.join(LOG_FOLDER, "jarvis.log")

os.makedirs(LOG_FOLDER, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


class JarvisLogger:

    @staticmethod
    def info(message: str):

        logging.info(message)

    @staticmethod
    def warning(message: str):

        logging.warning(message)

    @staticmethod
    def error(message: str):

        logging.error(message)

    @staticmethod
    def critical(message: str):

        logging.critical(message)