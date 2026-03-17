"""Logging configuration with rotating file handler."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(level: int = logging.INFO) -> None:
    """Configure logging with a rotating file handler and console output."""
    log_dir = Path.home() / ".audioforge" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "audioforge.log"

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file handler: 5MB max, keep 3 backups
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # Configure root logger
    root_logger = logging.getLogger("audioforge")
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
