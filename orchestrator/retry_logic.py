from tenacity import retry, stop_after_attempt, wait_exponential
from functools import wraps
from .logger import get_logger

logger = get_logger()

def with_retry(config):
    """
    Decorator that implements retry logic with exponential backoff.
    
    Args:
        config (dict): Retry configuration containing:
            - max_attempts: Maximum number of retry attempts
            - initial_delay: Initial delay between retries in seconds
            - max_delay: Maximum delay between retries in seconds
            - exponential_base: Base for exponential backoff
    """
    def decorator(func):
        @wraps(func)
        @retry(
            stop=stop_after_attempt(config['retry']['max_attempts']),
            wait=wait_exponential(
                multiplier=config['retry']['initial_delay'],
                max=config['retry']['max_delay'],
                exp_base=config['retry']['exponential_base']
            ),
            reraise=True
        )
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    "operation_failed",
                    function=func.__name__,
                    error=str(e),
                    attempt=wrapper.retry.statistics.attempt_number
                )
                raise
        return wrapper
    return decorator 