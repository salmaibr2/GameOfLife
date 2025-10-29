"""Main entry point for Game of Life application."""
import logging.handlers
import os
from pathlib import Path

import platformdirs

from gamelife.core.config import Config
from gamelife.gui.app import GameLifeApp

def setup_logging():
    """Configure application logging."""
    log_dir = Path(platformdirs.user_log_dir("GameOfLife"))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "gamelife.log"
    
    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=1048576,  # 1MB
        backupCount=5,
        encoding="utf-8",
    )
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

def main():
    """Initialize and run the application."""
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Game of Life Task Manager")
    
    try:
        app = GameLifeApp()
        app.run()
    except Exception as e:
        logger.exception("Application crashed: %s", e)
        raise

if __name__ == "__main__":
    main()