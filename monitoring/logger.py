# monitoring/logger.py - Enhanced logging system with request tracing

import logging
import json
import time
import uuid
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime, timezone
from contextlib import contextmanager
import sys
import traceback

from config import config_manager

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add request ID if available
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        # Add user ID if available
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
            
        # Add operation type if available
        if hasattr(record, 'operation'):
            log_entry['operation'] = record.operation
            
        # Add duration if available
        if hasattr(record, 'duration'):
            log_entry['duration_ms'] = record.duration
            
        # Add extra data if available
        if hasattr(record, 'extra_data'):
            log_entry['data'] = record.extra_data
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
            
        return json.dumps(log_entry, ensure_ascii=False)

class RequestContextFilter(logging.Filter):
    """Filter to add request context to log records"""
    
    def filter(self, record):
        # Get request context from thread local storage
        context = getattr(_request_context, 'context', {})
        
        for key, value in context.items():
            setattr(record, key, value)
            
        return True

class MetricsCollector:
    """Collect and track various metrics"""
    
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_error': 0,
            'tts_generations': 0,
            'vc_generations': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0,
            'model_loads': 0,
            'errors_by_type': {},
            'requests_by_endpoint': {},
            'processing_times': []
        }
        self._lock = threading.Lock()
        
    def increment_counter(self, metric_name: str, value: int = 1):
        """Increment a counter metric"""
        with self._lock:
            self.metrics[metric_name] = self.metrics.get(metric_name, 0) + value
            
    def record_processing_time(self, duration_ms: float):
        """Record processing time"""
        with self._lock:
            self.metrics['total_processing_time'] += duration_ms
            self.metrics['processing_times'].append(duration_ms)
            
            # Keep only last 1000 processing times
            if len(self.metrics['processing_times']) > 1000:
                self.metrics['processing_times'] = self.metrics['processing_times'][-1000:]
                
            # Update average
            if self.metrics['processing_times']:
                self.metrics['average_processing_time'] = sum(self.metrics['processing_times']) / len(self.metrics['processing_times'])
                
    def record_error(self, error_type: str):
        """Record error by type"""
        with self._lock:
            self.metrics['errors_by_type'][error_type] = self.metrics['errors_by_type'].get(error_type, 0) + 1
            
    def record_endpoint_request(self, endpoint: str):
        """Record request by endpoint"""
        with self._lock:
            self.metrics['requests_by_endpoint'][endpoint] = self.metrics['requests_by_endpoint'].get(endpoint, 0) + 1
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        with self._lock:
            # Calculate additional metrics
            metrics_copy = self.metrics.copy()
            
            if self.metrics['requests_total'] > 0:
                metrics_copy['success_rate'] = self.metrics['requests_success'] / self.metrics['requests_total']
                metrics_copy['error_rate'] = self.metrics['requests_error'] / self.metrics['requests_total']
            else:
                metrics_copy['success_rate'] = 0.0
                metrics_copy['error_rate'] = 0.0
                
            return metrics_copy

# Thread-local storage for request context
_request_context = threading.local()

# Global metrics collector
metrics_collector = MetricsCollector()

class EnhancedLogger:
    """Enhanced logger with request tracing and metrics collection"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_logger()
        
    def _setup_logger(self):
        """Setup logger with enhanced formatting"""
        if not self.logger.handlers:
            # Console handler with JSON formatting
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(JSONFormatter())
            console_handler.addFilter(RequestContextFilter())
            self.logger.addHandler(console_handler)
            
            # File handler if configured
            log_file = config_manager.get("server.log_file_path")
            if log_file:
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                file_handler = logging.FileHandler(log_path, encoding='utf-8')
                file_handler.setFormatter(JSONFormatter())
                file_handler.addFilter(RequestContextFilter())
                self.logger.addHandler(file_handler)
                
            # Set level
            log_level = config_manager.get("server.log_level", "INFO").upper()
            self.logger.setLevel(getattr(logging, log_level))
            
    def set_request_context(self, request_id: str, operation: str = None, user_id: str = None, **kwargs):
        """Set request context for current thread"""
        context = {
            'request_id': request_id,
        }
        if operation:
            context['operation'] = operation
        if user_id:
            context['user_id'] = user_id
        context.update(kwargs)
        
        _request_context.context = context
        
    def clear_request_context(self):
        """Clear request context for current thread"""
        _request_context.context = {}
        
    @contextmanager
    def request_context(self, request_id: str = None, operation: str = None, user_id: str = None, **kwargs):
        """Context manager for request tracing"""
        if request_id is None:
            request_id = str(uuid.uuid4())
            
        original_context = getattr(_request_context, 'context', {})
        
        try:
            self.set_request_context(request_id, operation, user_id, **kwargs)
            yield request_id
        finally:
            _request_context.context = original_context
            
    @contextmanager
    def operation_timer(self, operation: str, record_metrics: bool = True):
        """Context manager for timing operations"""
        start_time = time.time()
        request_id = getattr(_request_context, 'context', {}).get('request_id', str(uuid.uuid4()))
        
        self.info(f"Starting operation: {operation}", extra_data={'operation': operation})
        
        try:
            yield
            duration_ms = (time.time() - start_time) * 1000
            
            if record_metrics:
                metrics_collector.record_processing_time(duration_ms)
                
            self.info(f"Completed operation: {operation}", 
                     extra_data={'operation': operation, 'duration_ms': duration_ms})
                     
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            if record_metrics:
                metrics_collector.record_error(type(e).__name__)
                
            self.error(f"Failed operation: {operation}", 
                      extra_data={'operation': operation, 'duration_ms': duration_ms},
                      exc_info=True)
            raise
            
    def debug(self, message: str, extra_data: Dict = None, **kwargs):
        """Debug level logging"""
        self._log(logging.DEBUG, message, extra_data, **kwargs)
        
    def info(self, message: str, extra_data: Dict = None, **kwargs):
        """Info level logging"""
        self._log(logging.INFO, message, extra_data, **kwargs)
        
    def warning(self, message: str, extra_data: Dict = None, **kwargs):
        """Warning level logging"""
        self._log(logging.WARNING, message, extra_data, **kwargs)
        
    def error(self, message: str, extra_data: Dict = None, exc_info: bool = False, **kwargs):
        """Error level logging"""
        self._log(logging.ERROR, message, extra_data, exc_info=exc_info, **kwargs)
        
    def critical(self, message: str, extra_data: Dict = None, exc_info: bool = False, **kwargs):
        """Critical level logging"""
        self._log(logging.CRITICAL, message, extra_data, exc_info=exc_info, **kwargs)
        
    def _log(self, level: int, message: str, extra_data: Dict = None, **kwargs):
        """Internal logging method"""
        extra = {}
        if extra_data:
            extra['extra_data'] = extra_data
            
        for key, value in kwargs.items():
            extra[key] = value
            
        self.logger.log(level, message, extra=extra)

def get_logger(name: str) -> EnhancedLogger:
    """Get enhanced logger instance"""
    return EnhancedLogger(name)

def get_metrics() -> Dict[str, Any]:
    """Get current metrics"""
    return metrics_collector.get_metrics()

# Export commonly used functions
__all__ = [
    'EnhancedLogger',
    'get_logger', 
    'get_metrics',
    'metrics_collector'
]
