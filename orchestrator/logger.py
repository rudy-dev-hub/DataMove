import structlog
import logging
import sys
from pathlib import Path

def setup_logger(config):
    """Configure structured logging for the pipeline."""
    
    # Create logs directory if it doesn't exist
    log_path = Path(config['logging']['output_file'])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Set up file handler
    file_handler = logging.FileHandler(config['logging']['output_file'])
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    
    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(config['logging']['level'])
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return structlog.get_logger()

def get_logger():
    """Get the configured logger instance."""
    return structlog.get_logger() 