from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from typing import Callable, Any
from services.observability import observability_service

class RetryableError(Exception):
    """Exception that should trigger a retry"""
    pass

def with_retry(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10
):
    """
    Decorator for retrying functions with exponential backoff
    
    Usage:
        @with_retry(max_attempts=3)
        async def my_function():
            ...
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(RetryableError),
        before_sleep=lambda retry_state: observability_service.log_warning(
            f"Retrying {retry_state.fn.__name__} after {retry_state.outcome.exception()}"
        )
    )

async def handle_node_error(node_name: str, error: Exception, state: dict) -> dict:
    """
    Handle errors in workflow nodes
    
    Args:
        node_name: Name of the node that failed
        error: Exception that occurred
        state: Current workflow state
        
    Returns:
        Updated state with error information
    """
    error_message = f"{node_name}: {str(error)}"
    
    observability_service.log_error(error_message)
    
    if 'errors' not in state:
        state['errors'] = []
    
    state['errors'].append(error_message)
    state['retry_count'] = state.get('retry_count', 0) + 1
    
    # Determine if we should retry
    if state['retry_count'] < 3:
        # Allow retry
        state['status'] = 'retrying'
    else:
        # Max retries exceeded
        state['status'] = 'failed'
        observability_service.log_error(f"Max retries exceeded for {node_name}")
    
    return state
