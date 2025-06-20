# resilience/retry_handler.py - Retry mechanisms for download operations

import time
import random
from typing import Callable, Any, Optional, Dict
from functools import wraps

from monitoring import get_logger
from .error_tracker import error_tracker, ErrorCategory, ErrorSeverity

logger = get_logger(__name__)

class RetryConfig:
    """Configuration for retry behavior"""
    def __init__(self, max_retries: int = 2, base_delay: float = 2.0, 
                 max_delay: float = 30.0, backoff_factor: float = 2.0,
                 jitter: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay for retry attempt with exponential backoff"""
    delay = config.base_delay * (config.backoff_factor ** (attempt - 1))
    delay = min(delay, config.max_delay)
    
    if config.jitter:
        # Add random jitter to prevent thundering herd
        jitter_amount = delay * 0.1
        delay += random.uniform(-jitter_amount, jitter_amount)
    
    return max(delay, 0.1)  # Minimum 100ms delay

def retry_download(max_retries: int = 2, base_delay: float = 2.0, 
                  operation_name: Optional[str] = None):
    """
    Decorator for download operations with exponential backoff retry
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        operation_name: Name for logging (defaults to function name)
    """
    config = RetryConfig(max_retries=max_retries, base_delay=base_delay)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            op_name = operation_name or func.__name__
            last_exception = None
            
            for attempt in range(max_retries + 1):  # +1 for initial attempt
                try:
                    # Log attempt (but not for first attempt to reduce noise)
                    if attempt > 0:
                        logger.info(f"Retry attempt {attempt}/{max_retries} for {op_name}")
                    
                    # Call the function
                    result = func(*args, **kwargs)
                    
                    # Success! Log if this was a retry
                    if attempt > 0:
                        logger.info(f"Operation {op_name} succeeded on attempt {attempt + 1}")
                        error_tracker.mark_resolved(op_name, type(last_exception).__name__)
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Determine if we should retry
                    should_retry = error_tracker.should_retry(e, op_name, attempt, max_retries)
                    
                    # Record the error
                    category = error_tracker.categorize_error(e, op_name)
                    severity = ErrorSeverity.MEDIUM if should_retry else ErrorSeverity.HIGH
                    
                    error_tracker.record_error(
                        operation=op_name,
                        error=e,
                        context={
                            'attempt': attempt + 1,
                            'max_retries': max_retries,
                            'will_retry': should_retry and attempt < max_retries,
                            'args_count': len(args),
                            'kwargs_keys': list(kwargs.keys())
                        },
                        category=category,
                        severity=severity,
                        retry_count=attempt
                    )
                    
                    # If this is the last attempt or we shouldn't retry, raise the exception
                    if attempt >= max_retries or not should_retry:
                        logger.error(f"Operation {op_name} failed after {attempt + 1} attempts: {e}")
                        raise e
                    
                    # Calculate delay and wait
                    delay = calculate_delay(attempt + 1, config)
                    logger.info(f"Waiting {delay:.1f}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator

class AdvancedRetryHandler:
    """Advanced retry handler with more sophisticated logic"""
    
    def __init__(self):
        self.retry_counts: Dict[str, int] = {}
        self.success_counts: Dict[str, int] = {}
    
    def execute_with_retry(self, operation: Callable, operation_name: str,
                          config: RetryConfig = None, context: Dict[str, Any] = None) -> Any:
        """
        Execute operation with advanced retry logic
        
        Args:
            operation: Function to execute
            operation_name: Name for tracking
            config: Retry configuration
            context: Additional context for logging
        """
        if config is None:
            config = RetryConfig()
        
        context = context or {}
        last_exception = None
        
        for attempt in range(config.max_retries + 1):
            try:
                # Track attempt
                if attempt > 0:
                    logger.info(f"Advanced retry {attempt}/{config.max_retries} for {operation_name}",
                               extra_data={'context': context})
                
                # Execute operation
                with logger.operation_timer(f"{operation_name}_attempt_{attempt + 1}"):
                    result = operation()
                
                # Success!
                if attempt > 0:
                    logger.info(f"Advanced retry succeeded for {operation_name} on attempt {attempt + 1}")
                    error_tracker.mark_resolved(operation_name, type(last_exception).__name__)
                
                # Track success
                self.success_counts[operation_name] = self.success_counts.get(operation_name, 0) + 1
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Check if we should retry
                should_retry = error_tracker.should_retry(e, operation_name, attempt, config.max_retries)
                
                # Record error with enhanced context
                enhanced_context = {
                    **context,
                    'attempt': attempt + 1,
                    'max_retries': config.max_retries,
                    'will_retry': should_retry and attempt < config.max_retries,
                    'total_retries_for_operation': self.retry_counts.get(operation_name, 0),
                    'total_successes_for_operation': self.success_counts.get(operation_name, 0)
                }
                
                category = error_tracker.categorize_error(e, operation_name)
                severity = ErrorSeverity.MEDIUM if should_retry else ErrorSeverity.HIGH
                
                error_tracker.record_error(
                    operation=operation_name,
                    error=e,
                    context=enhanced_context,
                    category=category,
                    severity=severity,
                    retry_count=attempt
                )
                
                # Track retry
                self.retry_counts[operation_name] = self.retry_counts.get(operation_name, 0) + 1
                
                # Final attempt or shouldn't retry
                if attempt >= config.max_retries or not should_retry:
                    logger.error(f"Advanced retry failed for {operation_name} after {attempt + 1} attempts",
                                extra_data={'final_error': str(e), 'context': enhanced_context})
                    raise e
                
                # Wait before retry
                delay = calculate_delay(attempt + 1, config)
                logger.info(f"Waiting {delay:.1f}s before advanced retry {attempt + 1}/{config.max_retries}")
                time.sleep(delay)
        
        raise last_exception
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retry statistics"""
        return {
            'retry_counts': dict(self.retry_counts),
            'success_counts': dict(self.success_counts),
            'operations_tracked': len(set(list(self.retry_counts.keys()) + list(self.success_counts.keys())))
        }

# Global advanced retry handler
advanced_retry_handler = AdvancedRetryHandler()
