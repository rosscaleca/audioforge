"""Entry point for `python -m audioforge`."""

import argparse
import logging

from audioforge.logging_config import setup_logging


def main():
    parser = argparse.ArgumentParser(description="AudioForge — Audio Converter")
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Set the logging level (default: info)",
    )
    args = parser.parse_args()

    setup_logging(level=getattr(logging, args.log_level.upper()))

    logger = logging.getLogger(__name__)
    logger.info("Starting AudioForge")

    from audioforge.app import AudioForgeApp

    app = AudioForgeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
