"""
Centralized logging - Windows cp1252 safe (no Unicode arrows/emoji in log messages).
"""

import logging
import os
import sys
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

_configured = False


def setup_logger(name: str) -> logging.Logger:
    global _configured
    logger = logging.getLogger(name)

    if not _configured:
        log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
        fmt = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

        # Console handler - UTF-8 forced to prevent Windows cp1252 crash
        console_handler = logging.StreamHandler(
            stream=open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1, closefd=False)
        )
        console_handler.setFormatter(logging.Formatter(fmt))
        console_handler.setLevel(log_level)

        # File handler - always UTF-8
        file_handler = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(fmt))
        file_handler.setLevel(log_level)

        root = logging.getLogger()
        root.setLevel(log_level)
        root.addHandler(console_handler)
        root.addHandler(file_handler)
        _configured = True

    return logger