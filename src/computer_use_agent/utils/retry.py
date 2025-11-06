"""Retry utilities with exponential backoff."""

import time
import logging
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


def retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 2.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """Decorator for retrying a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay

            for retry in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if retry == max_retries - 1:
                        # Last retry failed, re-raise
                        raise

                    logger.warning(
                        f"Attempt {retry + 1}/{max_retries} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    delay *= backoff_factor

            # Should never reach here, but just in case
            return func(*args, **kwargs)

        return wrapper

    return decorator


class RetryableAPICall:
    """Context manager for retryable API calls with specific error handling."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 2.0,
        on_503_callback: Optional[Callable] = None,
        on_429_callback: Optional[Callable] = None,
    ):
        """Initialize retryable API call context.

        Args:
            max_retries: Maximum retry attempts
            initial_delay: Initial delay between retries
            on_503_callback: Callback for 503 errors
            on_429_callback: Callback for 429 rate limit errors
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.on_503_callback = on_503_callback
        self.on_429_callback = on_429_callback
        self.retry_count = 0
        self.delay = initial_delay

    def should_retry(self, error: Exception) -> bool:
        """Determine if error should trigger a retry.

        Args:
            error: Exception that occurred

        Returns:
            True if should retry
        """
        error_msg = str(error)

        # Check for 503/UNAVAILABLE/Deadline errors
        if any(
            x in error_msg for x in ["503", "UNAVAILABLE", "Deadline", "unavailable"]
        ):
            if self.on_503_callback:
                self.on_503_callback(self.retry_count, self.delay)
            return True

        # Check for rate limit errors
        if any(x in error_msg for x in ["429", "RATE_LIMIT", "rate_limit"]):
            if self.on_429_callback:
                self.on_429_callback()
            time.sleep(30)  # Wait longer for rate limits
            return True

        return False

    def wait_and_retry(self):
        """Wait before retry with exponential backoff."""
        time.sleep(self.delay)
        self.delay *= 2  # Exponential backoff
