# resilience/error_tracker.py - Enhanced error tracking and categorization

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from monitoring import get_logger

logger = get_logger(__name__)

class ErrorCategory(Enum):
    """Error categories for better handling"""
    TRANSIENT = "transient"        # Likely to succeed on retry (network, timeouts)
    PERMANENT = "permanent"        # Unlikely to succeed on retry (validation, corruption)
    RESOURCE = "resource"          # Resource related (memory, disk space)
    CONFIGURATION = "configuration"  # Configuration issues

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"           # Minor issues, operation can continue
    MEDIUM = "medium"     # Notable issues, some functionality affected
    HIGH = "high"         # Major issues, core functionality affected
    CRITICAL = "critical" # Critical issues, application stability at risk

@dataclass
class ErrorRecord:
    """Structured error record"""
    timestamp: datetime
    operation: str
    error_type: str
    error_message: str
    category: ErrorCategory
    severity: ErrorSeverity
    context: Dict[str, Any]
    retry_count: int = 0
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None

class ErrorTracker:
    """Enhanced error tracking and analysis"""
    
    def __init__(self, max_errors: int = 1000):
        self.max_errors = max_errors
        self.errors: List[ErrorRecord] = []
        self.error_stats: Dict[str, int] = {}
        self.lock = threading.Lock()
        logger.info("Error tracker initialized", extra_data={'max_errors': max_errors})
    
    def record_error(self, operation: str, error: Exception, context: Dict[str, Any] = None,
                    category: ErrorCategory = ErrorCategory.PERMANENT,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    retry_count: int = 0) -> str:
        """Record an error with categorization"""
        
        with self.lock:
            error_record = ErrorRecord(
                timestamp=datetime.now(),
                operation=operation,
                error_type=type(error).__name__,
                error_message=str(error),
                category=category,
                severity=severity,
                context=context or {},
                retry_count=retry_count
            )
            
            self.errors.append(error_record)
            
            # Maintain max errors limit
            if len(self.errors) > self.max_errors:
                self.errors = self.errors[-self.max_errors:]
            
            # Update statistics
            error_key = f"{operation}:{error_record.error_type}"
            self.error_stats[error_key] = self.error_stats.get(error_key, 0) + 1
            
            # Log with appropriate level based on severity
            log_level = {
                ErrorSeverity.LOW: "debug",
                ErrorSeverity.MEDIUM: "warning", 
                ErrorSeverity.HIGH: "error",
                ErrorSeverity.CRITICAL: "critical"
            }.get(severity, "error")
            
            extra_data = {
                'operation': operation,
                'error_type': error_record.error_type,
                'category': category.value,
                'severity': severity.value,
                'retry_count': retry_count,
                'context': context
            }
            
            getattr(logger, log_level)(
                f"Error in {operation}: {error_record.error_message}",
                extra_data=extra_data
            )
            
            return f"error_{int(error_record.timestamp.timestamp())}"
    
    def mark_resolved(self, operation: str, error_type: str) -> None:
        """Mark errors as resolved for an operation"""
        with self.lock:
            current_time = datetime.now()
            for error in reversed(self.errors):  # Check recent errors first
                if (error.operation == operation and 
                    error.error_type == error_type and 
                    not error.resolved):
                    error.resolved = True
                    error.resolution_timestamp = current_time
                    logger.info(f"Marked error as resolved: {operation}:{error_type}")
                    break
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            recent_errors = [e for e in self.errors if e.timestamp >= cutoff_time]
            
            summary = {
                'total_errors': len(recent_errors),
                'by_category': {},
                'by_severity': {},
                'by_operation': {},
                'most_frequent': {},
                'unresolved_count': 0
            }
            
            for error in recent_errors:
                # By category
                cat = error.category.value
                summary['by_category'][cat] = summary['by_category'].get(cat, 0) + 1
                
                # By severity  
                sev = error.severity.value
                summary['by_severity'][sev] = summary['by_severity'].get(sev, 0) + 1
                
                # By operation
                op = error.operation
                summary['by_operation'][op] = summary['by_operation'].get(op, 0) + 1
                
                # Count unresolved
                if not error.resolved:
                    summary['unresolved_count'] += 1
            
            # Most frequent errors
            for error_key, count in self.error_stats.items():
                if count >= 3:  # Only show frequently occurring errors
                    summary['most_frequent'][error_key] = count
            
            return summary
    
    def get_recent_errors(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent errors for debugging"""
        with self.lock:
            recent = self.errors[-count:] if self.errors else []
            return [asdict(error) for error in reversed(recent)]
    
    def categorize_error(self, error: Exception, operation: str) -> ErrorCategory:
        """Automatically categorize errors based on type and context"""
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        # Network/timeout related - likely transient
        if any(keyword in error_msg for keyword in [
            'timeout', 'connection', 'network', 'unreachable', 
            'temporary failure', 'service unavailable'
        ]):
            return ErrorCategory.TRANSIENT
        
        # Resource related
        if any(keyword in error_msg for keyword in [
            'memory', 'disk', 'space', 'resource', 'limit'
        ]):
            return ErrorCategory.RESOURCE
        
        # Configuration related
        if any(keyword in error_msg for keyword in [
            'config', 'setting', 'path', 'not found', 'permission'
        ]):
            return ErrorCategory.CONFIGURATION
        
        # Download operations are more likely to be transient
        if 'download' in operation.lower():
            return ErrorCategory.TRANSIENT
        
        # Default to permanent for model/generation errors
        return ErrorCategory.PERMANENT
    
    def should_retry(self, error: Exception, operation: str, retry_count: int, max_retries: int) -> bool:
        """Determine if an operation should be retried"""
        if retry_count >= max_retries:
            return False
        
        category = self.categorize_error(error, operation)
        
        # Only retry transient errors
        if category == ErrorCategory.TRANSIENT:
            return True
        
        # Special case: first retry for resource errors (might clear up)
        if category == ErrorCategory.RESOURCE and retry_count == 0:
            return True
        
        return False

# Global error tracker instance
error_tracker = ErrorTracker()
