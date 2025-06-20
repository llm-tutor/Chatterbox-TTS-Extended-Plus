# management/cleanup_scheduler.py - Automated cleanup scheduling

import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Optional

from config import config_manager
from management.resource_manager import resource_manager

logger = logging.getLogger(__name__)

class CleanupScheduler:
    """Schedules and manages automated cleanup operations"""
    
    def __init__(self):
        self.config = config_manager.get("resource_management.cleanup", {})
        self.cleanup_on_startup = self.config.get("cleanup_on_startup", True)
        self.cleanup_interval_hours = self.config.get("cleanup_interval_hours", 5)
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.last_cleanup_time: Optional[datetime] = None
        self.cleanup_history = []
        
        logger.info(f"CleanupScheduler initialized: startup_cleanup={self.cleanup_on_startup}, "
                   f"interval={self.cleanup_interval_hours}h")
    
    def start(self):
        """Start the cleanup scheduler"""
        if self._running:
            logger.warning("CleanupScheduler is already running")
            return
        
        self._running = True
        self._stop_event.clear()
        
        # Perform startup cleanup if enabled
        if self.cleanup_on_startup:
            logger.info("Performing startup cleanup")
            self._perform_cleanup()
        
        # Start background thread for periodic cleanup
        if self.cleanup_interval_hours > 0:
            self._thread = threading.Thread(target=self._cleanup_worker, daemon=True)
            self._thread.start()
            logger.info(f"Started cleanup scheduler with {self.cleanup_interval_hours}h interval")
        else:
            logger.info("Periodic cleanup disabled (interval = 0)")
    
    def stop(self):
        """Stop the cleanup scheduler"""
        if not self._running:
            return
        
        logger.info("Stopping cleanup scheduler")
        self._running = False
        self._stop_event.set()
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
            if self._thread.is_alive():
                logger.warning("Cleanup thread did not stop gracefully")
        
        logger.info("Cleanup scheduler stopped")
    
    def _cleanup_worker(self):
        """Background worker thread for periodic cleanup"""
        logger.debug("Cleanup worker thread started")
        
        interval_seconds = self.cleanup_interval_hours * 3600
        
        while self._running and not self._stop_event.is_set():
            # Wait for next cleanup time
            if self._stop_event.wait(timeout=interval_seconds):
                # Stop event was set, exit
                break
            
            if self._running:
                logger.info("Performing scheduled cleanup")
                self._perform_cleanup()
        
        logger.debug("Cleanup worker thread exiting")
    
    def _perform_cleanup(self):
        """Perform cleanup and track results"""
        try:
            start_time = datetime.now()
            cleanup_summary = resource_manager.perform_cleanup()
            end_time = datetime.now()
            
            cleanup_summary["start_time"] = start_time.isoformat()
            cleanup_summary["end_time"] = end_time.isoformat()
            cleanup_summary["duration_seconds"] = (end_time - start_time).total_seconds()
            
            self.last_cleanup_time = start_time
            self.cleanup_history.append(cleanup_summary)
            
            # Keep only last 10 cleanup records
            if len(self.cleanup_history) > 10:
                self.cleanup_history = self.cleanup_history[-10:]
            
            total_mb_freed = cleanup_summary["total_bytes_freed"] / 1024 / 1024
            logger.info(f"Cleanup completed in {cleanup_summary['duration_seconds']:.1f}s: "
                       f"{cleanup_summary['total_files_removed']} files, {total_mb_freed:.1f}MB freed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
            # Add error record to history
            error_record = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "total_files_removed": 0,
                "total_bytes_freed": 0
            }
            self.cleanup_history.append(error_record)
            if len(self.cleanup_history) > 10:
                self.cleanup_history = self.cleanup_history[-10:]
    
    def force_cleanup(self) -> dict:
        """Force immediate cleanup and return results"""
        logger.info("Force cleanup requested")
        start_time = datetime.now()
        
        try:
            cleanup_summary = resource_manager.perform_cleanup()
            end_time = datetime.now()
            
            cleanup_summary["start_time"] = start_time.isoformat()
            cleanup_summary["end_time"] = end_time.isoformat()
            cleanup_summary["duration_seconds"] = (end_time - start_time).total_seconds()
            cleanup_summary["forced"] = True
            
            self.last_cleanup_time = start_time
            self.cleanup_history.append(cleanup_summary)
            
            if len(self.cleanup_history) > 10:
                self.cleanup_history = self.cleanup_history[-10:]
            
            total_mb_freed = cleanup_summary["total_bytes_freed"] / 1024 / 1024
            logger.info(f"Force cleanup completed in {cleanup_summary['duration_seconds']:.1f}s: "
                       f"{cleanup_summary['total_files_removed']} files, {total_mb_freed:.1f}MB freed")
            
            return cleanup_summary
            
        except Exception as e:
            logger.error(f"Error during force cleanup: {e}", exc_info=True)
            error_summary = {
                "timestamp": datetime.now().isoformat(),
                "forced": True,
                "error": str(e),
                "total_files_removed": 0,
                "total_bytes_freed": 0,
                "duration_seconds": (datetime.now() - start_time).total_seconds()
            }
            return error_summary
    
    def get_status(self) -> dict:
        """Get scheduler status and history"""
        status = {
            "running": self._running,
            "cleanup_on_startup": self.cleanup_on_startup,
            "cleanup_interval_hours": self.cleanup_interval_hours,
            "last_cleanup_time": self.last_cleanup_time.isoformat() if self.last_cleanup_time else None,
            "cleanup_count": len(self.cleanup_history),
            "next_cleanup_time": None
        }
        
        # Calculate next cleanup time
        if (self._running and self.cleanup_interval_hours > 0 and 
            self.last_cleanup_time and self.last_cleanup_time):
            next_cleanup = self.last_cleanup_time + timedelta(hours=self.cleanup_interval_hours)
            status["next_cleanup_time"] = next_cleanup.isoformat()
        
        return status
    
    def get_history(self, limit: int = 5) -> list:
        """Get recent cleanup history"""
        return self.cleanup_history[-limit:] if self.cleanup_history else []


# Global cleanup scheduler instance
cleanup_scheduler = CleanupScheduler()
