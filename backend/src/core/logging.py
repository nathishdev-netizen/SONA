"""
Logging Configuration
Structured logging for SONA AI
"""

import logging
import sys
from src.core.config import settings


def setup_logging():
    """Configure application logging"""
    
    # Create logger
    logger = logging.getLogger("sona")
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance
logger = setup_logging()
