# management/__init__.py - Management module initialization

"""
Resource management and cleanup functionality for Chatterbox TTS Extended Plus.

This module provides:
- ResourceManager: Disk usage monitoring and cleanup policies
- CleanupScheduler: Automated cleanup scheduling
"""

from .resource_manager import resource_manager, ResourceManager
from .cleanup_scheduler import cleanup_scheduler, CleanupScheduler

__all__ = ['resource_manager', 'ResourceManager', 'cleanup_scheduler', 'CleanupScheduler']
