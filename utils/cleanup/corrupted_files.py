# utils/cleanup/corrupted_files.py - Cleanup Corrupted/Empty Files

import logging
from pathlib import Path
from typing import List, Dict, Union
from datetime import datetime

from config import config_manager

logger = logging.getLogger(__name__)


def scan_corrupted_files(directory: Union[str, Path], recursive: bool = True) -> List[Dict[str, str]]:
    """
    Scan directory for corrupted/empty audio files
    
    Args:
        directory: Directory to scan
        recursive: Whether to scan subdirectories
        
    Returns:
        List of corrupted file information
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
    
    corrupted_files = []
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    
    # Get all audio files
    if recursive:
        audio_files = [f for f in dir_path.rglob("*") if f.is_file() and f.suffix.lower() in audio_extensions]
    else:
        audio_files = [f for f in dir_path.iterdir() if f.is_file() and f.suffix.lower() in audio_extensions]
    
    for audio_file in audio_files:
        try:
            file_size = audio_file.stat().st_size
            if file_size == 0:
                corrupted_files.append({
                    'path': str(audio_file),
                    'relative_path': str(audio_file.relative_to(dir_path)),
                    'size_bytes': file_size,
                    'reason': 'empty_file'
                })
        except Exception as e:
            logger.warning(f"Could not check file {audio_file}: {e}")
    
    return corrupted_files


def cleanup_corrupted_files(directories: List[str] = None, dry_run: bool = False) -> Dict[str, List[str]]:
    """
    Clean up corrupted files from audio directories
    
    Args:
        directories: List of directories to clean. If None, uses default audio directories
        dry_run: If True, only report what would be deleted without actually deleting
        
    Returns:
        Dictionary with cleanup results per directory
    """
    if directories is None:
        directories = [
            config_manager.get("paths.output_dir", "outputs"),
            config_manager.get("paths.reference_audio_dir", "reference_audio"), 
            config_manager.get("paths.vc_input_dir", "vc_inputs")
        ]
    
    cleanup_results = {}
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            logger.info(f"Directory does not exist: {directory}")
            continue
            
        logger.info(f"Scanning for corrupted files in: {directory}")
        corrupted_files = scan_corrupted_files(dir_path, recursive=True)
        
        deleted_files = []
        deletion_errors = []
        
        for file_info in corrupted_files:
            file_path = Path(file_info['path'])
            
            try:
                if dry_run:
                    logger.info(f"[DRY RUN] Would delete corrupted file: {file_info['relative_path']}")
                    deleted_files.append(file_info['relative_path'])
                else:
                    # Delete the corrupted audio file
                    file_path.unlink()
                    logger.info(f"Deleted corrupted file: {file_info['relative_path']}")
                    deleted_files.append(file_info['relative_path'])
                    
                    # Also delete companion JSON metadata file if it exists
                    json_file = file_path.with_suffix(file_path.suffix + '.json')
                    if json_file.exists():
                        if dry_run:
                            logger.info(f"[DRY RUN] Would delete metadata file: {json_file.name}")
                        else:
                            json_file.unlink()
                            logger.info(f"Deleted metadata file: {json_file.name}")
                            
            except Exception as e:
                error_msg = f"Failed to delete {file_info['relative_path']}: {e}"
                logger.error(error_msg)
                deletion_errors.append(error_msg)
        
        cleanup_results[directory] = {
            'deleted_files': deleted_files,
            'errors': deletion_errors,
            'total_scanned': len(corrupted_files)
        }
        
        if deleted_files:
            logger.info(f"Cleanup complete for {directory}: {len(deleted_files)} files processed")
        else:
            logger.info(f"No corrupted files found in {directory}")
    
    return cleanup_results


def log_cleanup_summary(cleanup_results: Dict[str, List[str]], dry_run: bool = False):
    """
    Log a summary of cleanup operations
    
    Args:
        cleanup_results: Results from cleanup_corrupted_files()
        dry_run: Whether this was a dry run
    """
    total_files = sum(len(result['deleted_files']) for result in cleanup_results.values())
    total_errors = sum(len(result['errors']) for result in cleanup_results.values())
    
    action = "would be deleted" if dry_run else "deleted"
    
    if total_files > 0:
        logger.info(f"Cleanup summary: {total_files} corrupted files {action}")
        if total_errors > 0:
            logger.warning(f"Cleanup errors: {total_errors} files could not be processed")
    else:
        logger.info("Cleanup summary: No corrupted files found")
