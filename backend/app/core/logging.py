"""
Logging configuration using loguru.

Provides structured logging with colored console output and file rotation.
"""
import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings


def setup_logging():
    """
    Configure application logging.
    
    Sets up:
    - Colored console logging for development
    - File logging with rotation for production
    - Different log levels based on environment
    """
    # Remove default handler
    logger.remove()
    
    # Console logging with colors (for development)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )
    
    # File logging (for production)
    # Ensure log directory exists
    log_file_path = Path(settings.LOG_FILE)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        settings.LOG_FILE,
        rotation="500 MB",  # Rotate when file reaches 500MB
        retention="10 days",  # Keep logs for 10 days
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
               "{name}:{function}:{line} - {message}",
        compression="zip",  # Compress rotated logs
    )
    
    logger.info(f"Logging initialized - Level: {settings.LOG_LEVEL}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    return logger


# Initialize logging on module import
app_logger = setup_logging()
