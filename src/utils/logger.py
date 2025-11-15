"""
Logging utilities for the application.
Provides structured logging with different levels and formatters.
"""

import logging
import sys
from typing import Optional
from datetime import datetime
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        """Format log record with colors"""
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


class Logger:
    """
    Application logger with file and console outputs.
    Provides structured logging for different components.
    """
    
    def __init__(
        self,
        name: str,
        level: str = "INFO",
        log_to_file: bool = True,
        log_dir: str = "logs"
    ):
        """
        Initialize logger.
        
        Args:
            name: Logger name (usually module name)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Whether to log to file
            log_dir: Directory for log files
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_to_file:
            log_path = Path(log_dir)
            log_path.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(
                log_path / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """Log critical message"""
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)
    
    def log_api_call(
        self,
        endpoint: str,
        model: str,
        tokens_used: Optional[int] = None,
        duration: Optional[float] = None
    ):
        """
        Log API call with structured data.
        
        Args:
            endpoint: API endpoint called
            model: Model used
            tokens_used: Number of tokens consumed
            duration: Call duration in seconds
        """
        message = f"API Call: {endpoint} | Model: {model}"
        if tokens_used:
            message += f" | Tokens: {tokens_used}"
        if duration:
            message += f" | Duration: {duration:.2f}s"
        
        self.info(message)
    
    def log_complaint(
        self,
        complaint_id: str,
        product: str,
        issue: str,
        action_taken: str
    ):
        """
        Log complaint processing.
        
        Args:
            complaint_id: Unique complaint identifier
            product: Product category
            issue: Issue category
            action_taken: Action performed
        """
        self.info(
            f"Complaint Processed | ID: {complaint_id} | "
            f"Product: {product} | Issue: {issue} | "
            f"Action: {action_taken}"
        )


def get_logger(name: str, level: str = "INFO") -> Logger:
    """
    Factory function to get or create a logger.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Logger instance
    """
    return Logger(name, level)