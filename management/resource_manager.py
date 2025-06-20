# management/resource_manager.py - Resource management and monitoring

import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from config import config_manager

logger = logging.getLogger(__name__)

class ResourceManager:
    """Manages system resources, disk usage, and cleanup policies"""
    
    def __init__(self):
        self.config = config_manager.get("resource_management.cleanup", {})
        
        # Resource limits (converted to bytes for internal use)
        self.output_dir_max_bytes = int(self.config.get("output_dir_max_size_gb", 5.0) * 1024 * 1024 * 1024)
        self.vc_inputs_max_bytes = int(self.config.get("vc_inputs_max_size_gb", 2.0) * 1024 * 1024 * 1024)
        self.temp_dir_max_files = self.config.get("temp_dir_max_files", 200)
        self.temp_dir_max_age_days = self.config.get("temp_dir_max_age_days", 7)
        
        # Warning threshold
        self.warning_threshold = self.config.get("warning_threshold_percent", 80) / 100.0
        
        # Directories
        self.output_dir = Path(config_manager.get("paths.output_dir", "outputs"))
        self.temp_dir = Path(config_manager.get("paths.temp_dir", "temp"))
        self.vc_inputs_dir = Path(config_manager.get("paths.vc_input_dir", "vc_inputs"))
        
        logger.info(f"ResourceManager initialized with limits: "
                   f"output={self.output_dir_max_bytes/1024/1024/1024:.1f}GB, "
                   f"vc_inputs={self.vc_inputs_max_bytes/1024/1024/1024:.1f}GB, "
                   f"temp_files={self.temp_dir_max_files}, "
                   f"temp_age={self.temp_dir_max_age_days}days")
    
    def get_directory_size(self, directory: Path) -> int:
        """Get total size of directory in bytes"""
        if not directory.exists():
            return 0
        
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    try:
                        file_path = Path(dirpath) / filename
                        total_size += file_path.stat().st_size
                    except (OSError, FileNotFoundError):
                        # Skip files that can't be accessed
                        continue
        except Exception as e:
            logger.warning(f"Error calculating directory size for {directory}: {e}")
        
        return total_size
    
    def get_directory_file_count(self, directory: Path) -> int:
        """Get total number of files in directory"""
        if not directory.exists():
            return 0
        
        count = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                count += len(filenames)
        except Exception as e:
            logger.warning(f"Error counting files in {directory}: {e}")
        
        return count
    
    def get_old_files(self, directory: Path, max_age_days: int) -> List[Path]:
        """Get list of files older than max_age_days"""
        if not directory.exists():
            return []
        
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        old_files = []
        
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    try:
                        file_path = Path(dirpath) / filename
                        if file_path.stat().st_mtime < cutoff_time:
                            old_files.append(file_path)
                    except (OSError, FileNotFoundError):
                        continue
        except Exception as e:
            logger.warning(f"Error finding old files in {directory}: {e}")
        
        return old_files
    
    def get_oldest_files(self, directory: Path, limit: int) -> List[Path]:
        """Get list of oldest files beyond the limit"""
        if not directory.exists():
            return []
        
        files_with_time = []
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    try:
                        file_path = Path(dirpath) / filename
                        mtime = file_path.stat().st_mtime
                        files_with_time.append((file_path, mtime))
                    except (OSError, FileNotFoundError):
                        continue
        except Exception as e:
            logger.warning(f"Error getting oldest files in {directory}: {e}")
            return []
        
        # Sort by modification time (oldest first) and return excess files
        files_with_time.sort(key=lambda x: x[1])
        if len(files_with_time) > limit:
            return [file_path for file_path, _ in files_with_time[:-limit]]
        
        return []
    
    def cleanup_old_files(self, directory: Path, max_age_days: int) -> Tuple[int, int]:
        """Remove files older than max_age_days. Returns (files_removed, bytes_freed)"""
        old_files = self.get_old_files(directory, max_age_days)
        
        files_removed = 0
        bytes_freed = 0
        
        for file_path in old_files:
            try:
                file_size = file_path.stat().st_size
                file_path.unlink()
                files_removed += 1
                bytes_freed += file_size
                logger.debug(f"Removed old file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove old file {file_path}: {e}")
        
        if files_removed > 0:
            logger.info(f"Cleaned up {files_removed} old files from {directory}, "
                       f"freed {bytes_freed/1024/1024:.1f}MB")
        
        return files_removed, bytes_freed
    
    def cleanup_excess_files(self, directory: Path, max_files: int) -> Tuple[int, int]:
        """Remove oldest files if count exceeds max_files. Returns (files_removed, bytes_freed)"""
        excess_files = self.get_oldest_files(directory, max_files)
        
        files_removed = 0
        bytes_freed = 0
        
        for file_path in excess_files:
            try:
                file_size = file_path.stat().st_size
                file_path.unlink()
                files_removed += 1
                bytes_freed += file_size
                logger.debug(f"Removed excess file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove excess file {file_path}: {e}")
        
        if files_removed > 0:
            logger.info(f"Cleaned up {files_removed} excess files from {directory}, "
                       f"freed {bytes_freed/1024/1024:.1f}MB")
        
        return files_removed, bytes_freed
    
    def cleanup_directory_by_size(self, directory: Path, max_bytes: int) -> Tuple[int, int]:
        """Remove oldest files if directory size exceeds max_bytes. Returns (files_removed, bytes_freed)"""
        current_size = self.get_directory_size(directory)
        if current_size <= max_bytes:
            return 0, 0
        
        # Get all files sorted by modification time (oldest first)
        files_with_time = []
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    try:
                        file_path = Path(dirpath) / filename
                        stat = file_path.stat()
                        files_with_time.append((file_path, stat.st_mtime, stat.st_size))
                    except (OSError, FileNotFoundError):
                        continue
        except Exception as e:
            logger.warning(f"Error getting files for size cleanup in {directory}: {e}")
            return 0, 0
        
        files_with_time.sort(key=lambda x: x[1])  # Sort by modification time
        
        files_removed = 0
        bytes_freed = 0
        
        for file_path, mtime, file_size in files_with_time:
            if current_size - bytes_freed <= max_bytes:
                break
            
            try:
                file_path.unlink()
                files_removed += 1
                bytes_freed += file_size
                logger.debug(f"Removed file for size limit: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove file {file_path}: {e}")
        
        if files_removed > 0:
            logger.info(f"Cleaned up {files_removed} files from {directory} for size limit, "
                       f"freed {bytes_freed/1024/1024:.1f}MB")
        
        return files_removed, bytes_freed
    
    def perform_cleanup(self) -> Dict[str, any]:
        """Perform all cleanup operations. Returns summary of actions taken"""
        logger.info("Starting resource cleanup")
        
        cleanup_summary = {
            "timestamp": datetime.now().isoformat(),
            "actions": {},
            "total_files_removed": 0,
            "total_bytes_freed": 0
        }
        
        # Cleanup temp directory by age
        files_removed, bytes_freed = self.cleanup_old_files(self.temp_dir, self.temp_dir_max_age_days)
        cleanup_summary["actions"]["temp_age_cleanup"] = {
            "files_removed": files_removed,
            "bytes_freed": bytes_freed
        }
        cleanup_summary["total_files_removed"] += files_removed
        cleanup_summary["total_bytes_freed"] += bytes_freed
        
        # Cleanup temp directory by file count
        files_removed, bytes_freed = self.cleanup_excess_files(self.temp_dir, self.temp_dir_max_files)
        cleanup_summary["actions"]["temp_count_cleanup"] = {
            "files_removed": files_removed,
            "bytes_freed": bytes_freed
        }
        cleanup_summary["total_files_removed"] += files_removed
        cleanup_summary["total_bytes_freed"] += bytes_freed
        
        # Cleanup output directory by size
        files_removed, bytes_freed = self.cleanup_directory_by_size(self.output_dir, self.output_dir_max_bytes)
        cleanup_summary["actions"]["output_size_cleanup"] = {
            "files_removed": files_removed,
            "bytes_freed": bytes_freed
        }
        cleanup_summary["total_files_removed"] += files_removed
        cleanup_summary["total_bytes_freed"] += bytes_freed
        
        # Cleanup vc_inputs directory by size
        files_removed, bytes_freed = self.cleanup_directory_by_size(self.vc_inputs_dir, self.vc_inputs_max_bytes)
        cleanup_summary["actions"]["vc_inputs_size_cleanup"] = {
            "files_removed": files_removed,
            "bytes_freed": bytes_freed
        }
        cleanup_summary["total_files_removed"] += files_removed
        cleanup_summary["total_bytes_freed"] += bytes_freed
        
        total_mb_freed = cleanup_summary["total_bytes_freed"] / 1024 / 1024
        logger.info(f"Cleanup completed: {cleanup_summary['total_files_removed']} files removed, "
                   f"{total_mb_freed:.1f}MB freed")
        
        return cleanup_summary
    
    def get_resource_status(self) -> Dict[str, any]:
        """Get current resource usage status with warnings"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "directories": {},
            "warnings": []
        }
        
        # Output directory status
        output_size = self.get_directory_size(self.output_dir)
        output_usage_pct = (output_size / self.output_dir_max_bytes) * 100 if self.output_dir_max_bytes > 0 else 0
        status["directories"]["outputs"] = {
            "size_bytes": output_size,
            "size_mb": output_size / 1024 / 1024,
            "max_size_mb": self.output_dir_max_bytes / 1024 / 1024,
            "usage_percent": output_usage_pct,
            "file_count": self.get_directory_file_count(self.output_dir)
        }
        
        if output_usage_pct >= self.warning_threshold * 100:
            status["warnings"].append(f"Output directory using {output_usage_pct:.1f}% of available space")
        
        # Temp directory status
        temp_file_count = self.get_directory_file_count(self.temp_dir)
        temp_size = self.get_directory_size(self.temp_dir)
        temp_usage_pct = (temp_file_count / self.temp_dir_max_files) * 100 if self.temp_dir_max_files > 0 else 0
        status["directories"]["temp"] = {
            "size_bytes": temp_size,
            "size_mb": temp_size / 1024 / 1024,
            "file_count": temp_file_count,
            "max_files": self.temp_dir_max_files,
            "usage_percent": temp_usage_pct
        }
        
        if temp_usage_pct >= self.warning_threshold * 100:
            status["warnings"].append(f"Temp directory using {temp_usage_pct:.1f}% of file limit")
        
        # VC inputs directory status
        vc_inputs_size = self.get_directory_size(self.vc_inputs_dir)
        vc_inputs_usage_pct = (vc_inputs_size / self.vc_inputs_max_bytes) * 100 if self.vc_inputs_max_bytes > 0 else 0
        status["directories"]["vc_inputs"] = {
            "size_bytes": vc_inputs_size,
            "size_mb": vc_inputs_size / 1024 / 1024,
            "max_size_mb": self.vc_inputs_max_bytes / 1024 / 1024,
            "usage_percent": vc_inputs_usage_pct,
            "file_count": self.get_directory_file_count(self.vc_inputs_dir)
        }
        
        if vc_inputs_usage_pct >= self.warning_threshold * 100:
            status["warnings"].append(f"VC inputs directory using {vc_inputs_usage_pct:.1f}% of available space")
        
        return status


# Global resource manager instance
resource_manager = ResourceManager()
