# monitoring/metrics.py - Basic performance metrics collection

import time
import psutil
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

from config import config_manager

class SystemMetrics:
    """Collect basic system-level metrics"""
    
    def __init__(self):
        self.process = psutil.Process()
        
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        return self.process.cpu_percent()
        
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information"""
        memory_info = self.process.memory_info()
        memory_percent = self.process.memory_percent()
        
        return {
            'rss_mb': memory_info.rss / (1024 * 1024),
            'vms_mb': memory_info.vms / (1024 * 1024),
            'percent': memory_percent
        }
        
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage for output directories"""
        output_dir = Path(config_manager.get("paths.output_dir", "outputs"))
        if output_dir.exists():
            disk_usage = psutil.disk_usage(str(output_dir))
            return {
                'free_gb': disk_usage.free / (1024**3),
                'usage_percent': (disk_usage.used / disk_usage.total) * 100
            }
        return {'free_gb': 0, 'usage_percent': 0}
        
    def get_file_counts(self) -> Dict[str, int]:
        """Get file counts in various directories"""
        counts = {}
        directories = {
            'outputs': config_manager.get("paths.output_dir", "outputs"),
            'temp': config_manager.get("paths.temp_dir", "temp")
        }
        
        for name, path_str in directories.items():
            path = Path(path_str)
            counts[name] = len(list(path.rglob('*'))) if path.exists() else 0
                
        return counts

class PerformanceTracker:
    """Track basic performance metrics over time"""
    
    def __init__(self, max_history: int = 500):
        self.max_history = max_history
        self.processing_times = deque(maxlen=max_history)
        self.response_times = deque(maxlen=max_history)
        self._lock = threading.Lock()
        
    def record_processing_time(self, duration_ms: float, operation_type: str = 'unknown'):
        """Record processing time for an operation"""
        with self._lock:
            self.processing_times.append({
                'timestamp': datetime.now(),
                'duration_ms': duration_ms,
                'operation_type': operation_type
            })
            
    def record_response_time(self, duration_ms: float, endpoint: str):
        """Record API response time"""
        with self._lock:
            self.response_times.append({
                'timestamp': datetime.now(),
                'duration_ms': duration_ms,
                'endpoint': endpoint
            })
            
    def get_statistics(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get basic performance statistics for a time window"""
        with self._lock:
            cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
            
            # Filter data by time window
            recent_processing = [p for p in self.processing_times if p['timestamp'] > cutoff_time]
            recent_responses = [r for r in self.response_times if r['timestamp'] > cutoff_time]
            
            return {
                'time_window_minutes': time_window_minutes,
                'processing_times': self._analyze_durations(recent_processing),
                'response_times': self._analyze_durations(recent_responses),
                'sample_count': {
                    'processing_times': len(recent_processing),
                    'response_times': len(recent_responses)
                }
            }
            
    def _analyze_durations(self, duration_data: List[Dict]) -> Dict[str, Any]:
        """Analyze duration data"""
        if not duration_data:
            return {'min_ms': 0, 'max_ms': 0, 'avg_ms': 0, 'count': 0}
            
        durations = [d['duration_ms'] for d in duration_data]
        return {
            'min_ms': min(durations),
            'max_ms': max(durations),
            'avg_ms': sum(durations) / len(durations),
            'count': len(durations)
        }

class MetricsManager:
    """Central metrics management"""
    
    def __init__(self):
        self.system_metrics = SystemMetrics()
        self.performance_tracker = PerformanceTracker()
        
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get all metrics in one call"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': self.system_metrics.get_cpu_usage(),
                'memory': self.system_metrics.get_memory_usage(),
                'disk': self.system_metrics.get_disk_usage(),
                'file_counts': self.system_metrics.get_file_counts()
            },
            'performance': self.performance_tracker.get_statistics()
        }
        
    def record_operation(self, duration_ms: float, operation_type: str):
        """Record an operation duration"""
        self.performance_tracker.record_processing_time(duration_ms, operation_type)
        
    def record_api_call(self, duration_ms: float, endpoint: str):
        """Record an API call duration"""
        self.performance_tracker.record_response_time(duration_ms, endpoint)

# Global metrics manager instance
metrics_manager = MetricsManager()

def get_system_metrics() -> Dict[str, Any]:
    """Get current system metrics"""
    return metrics_manager.get_comprehensive_metrics()

def record_operation_time(duration_ms: float, operation_type: str):
    """Record operation timing"""
    metrics_manager.record_operation(duration_ms, operation_type)

def record_api_time(duration_ms: float, endpoint: str):
    """Record API call timing"""
    metrics_manager.record_api_call(duration_ms, endpoint)

# Export commonly used functions
__all__ = [
    'SystemMetrics',
    'PerformanceTracker', 
    'MetricsManager',
    'metrics_manager',
    'get_system_metrics',
    'record_operation_time',
    'record_api_time'
]
