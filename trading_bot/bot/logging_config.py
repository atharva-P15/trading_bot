"""
Logging configuration.
Sets up a rotating file handler + a coloured console handler.
Call setup_logging() once at startup (in cli.py) before anything else.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

from bot.config import LOG_BACKUP_COUNT, LOG_DIR, LOG_FILE, LOG_MAX_BYTES

# ── Format strings ───────────────────────────────────────────────────────────
FILE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
CONSOLE_FORMAT = "%(levelname)-8s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: int = logging.DEBUG) -> None:
    """
    Configure root logger with:
    - RotatingFileHandler  → logs/trading_bot.log
    - StreamHandler        → stderr (INFO+ only, keeps stdout clean for Typer)
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid adding duplicate handlers if called more than once
    if root.handlers:
        return

    # ── Rotating file handler ────────────────────────────────────────────────
    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(FILE_FORMAT, datefmt=DATE_FORMAT))

    # ── Console handler (INFO+) ──────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(CONSOLE_FORMAT))

    root.addHandler(file_handler)
    root.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger (always child of root logger)."""
    return logging.getLogger(name)
