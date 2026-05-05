"""
logger.py
---------
Centralised logging configuration for the agent system.
"""

import logging
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "agent.log"


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger for the given module name.

    Logs to both the console (INFO+) and a rotating file (DEBUG+).
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.DEBUG)

    # Console handler — INFO and above
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(
        logging.Formatter("%(levelname)-8s | %(name)s | %(message)s")
    )

    # File handler — DEBUG and above
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    )

    logger.addHandler(console)
    logger.addHandler(file_handler)

    return logger
