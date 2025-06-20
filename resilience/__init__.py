# resilience/__init__.py - Resilience module initialization

"""
Resilience module for error handling and recovery mechanisms.

This module provides:
- Enhanced error tracking and categorization
- Download retry logic with exponential backoff
- Advanced retry mechanisms for critical operations
- Error statistics and analysis
"""

from .error_tracker import (
    ErrorTracker, ErrorRecord, ErrorCategory, ErrorSeverity, error_tracker
)
from .retry_handler import (
    retry_download, RetryConfig, AdvancedRetryHandler, advanced_retry_handler
)

__all__ = [
    'ErrorTracker', 'ErrorRecord', 'ErrorCategory', 'ErrorSeverity', 'error_tracker',
    'retry_download', 'RetryConfig', 'AdvancedRetryHandler', 'advanced_retry_handler'
]
