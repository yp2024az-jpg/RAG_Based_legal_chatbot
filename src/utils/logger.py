"""
Core Utilities - Logging and exceptions
"""
import logging
from typing import Optional

class CustomException(Exception):
    """Base custom exception"""
    pass

class InvalidQueryException(CustomException):
    """Raised when query is invalid"""
    pass

class RetrievalException(CustomException):
    """Raised when retrieval fails"""
    pass

class LLMException(CustomException):
    """Raised when LLM operation fails"""
    pass

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Setup logger for application
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Console handler
    handler = logging.StreamHandler()
    handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger
