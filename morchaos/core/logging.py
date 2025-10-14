"""Centralized logging configuration for pyutils."""

import logging
import sys
from typing import Optional

_logger: Optional[logging.Logger] = None

def get_logger(name: str = "pyutils") -> logging.Logger:
    """Get or create the package-wide logger instance."""
    global _logger
    if _logger is None:
        _logger = logging.getLogger(name)
        _logger.setLevel(logging.INFO)
        
        if not _logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            _logger.addHandler(handler)
    
    return _logger

def set_log_level(level: str) -> None:
    """Set the log level for the package logger."""
    logger = get_logger()
    logger.setLevel(getattr(logging, level.upper()))