# utils/concatenation/basic.py - Basic Audio Concatenation Functions

import logging
import time
import random
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def concatenate_audio_files(file_paths: List[Path], output_path: Path, 
                          normalize_levels: bool = True, crossfade_ms: int = 0,
                          pause_duration_ms: int = 600, pause_variation_ms: int = 200) -> Dict[str, Any]:
    """
    Concatenate multiple audio files into a single file with natural pauses
    
    Args:
        file_paths: List of paths to audio files to concatenate
        output_path: Output file path
        normalize_levels: Whether to normalize audio levels
        crossfade_ms: Crossfade duration in milliseconds
        pause_duration_ms: Base pause duration between clips in milliseconds
        pause_variation_ms: Random variation in pause duration (v) in milliseconds
    
    Returns:
        Dictionary with concatenation metadata
    """
    try:
        from pydub import AudioSegment
        import librosa
        import soundfile as sf
        # random is already imported at module level
    except ImportError as e:
        raise ImportError(f"Required audio library not available: {e}")
    
    from ..audio.analysis import normalize_audio_format
    
    start_time = time.time()
    combined_audio = None
    total_duration = 0
    processed_files = []
    total_pause_duration = 0
    
    logger.info(f"Starting concatenation of {len(file_paths)} files with natural pauses")
    logger.info(f"Pause parameters: duration={pause_duration_ms}ms, variation=+/-{pause_variation_ms}ms")
    
    for i, file_path in enumerate(file_paths):
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        logger.info(f"Processing file {i+1}/{len(file_paths)}: {file_path.name}")
        
        try:
            # Load audio file using pydub for format flexibility
            audio_segment = AudioSegment.from_file(str(file_path))
            
            # Handle unusual audio formats (e.g., 64-bit from speed_factor processing)
            audio_segment = normalize_audio_format(audio_segment, file_path)
            
            # Normalize levels if requested
            if normalize_levels:
                # Normalize to -20dB to prevent clipping
                target_dBFS = -20.0
                change_in_dBFS = target_dBFS - audio_segment.dBFS
                audio_segment = audio_segment.apply_gain(change_in_dBFS)
            
            # Add to combined audio
            if combined_audio is None:
                # First file - no pause before it
                combined_audio = audio_segment
            else:
                # Calculate natural pause duration with variation
                if pause_duration_ms > 0:
                    # Generate random variation within bounds
                    min_pause = max(100, pause_duration_ms - pause_variation_ms)  # Minimum 100ms
                    max_pause = min(3000, pause_duration_ms + pause_variation_ms)  # Maximum 3000ms
                    actual_pause_ms = random.randint(min_pause, max_pause)
                    
                    # Create silence segment
                    pause_segment = AudioSegment.silent(duration=actual_pause_ms)
                    total_pause_duration += actual_pause_ms
                    
                    logger.info(f"Adding {actual_pause_ms}ms natural pause between clips")
                    
                    if crossfade_ms > 0:
                        # Apply crossfade with pause: 
                        # We want: previous_audio -> crossfade with new_audio -> pause -> ready for next
                        # So: crossfade first, then add pause for next iteration
                        combined_audio = combined_audio.append(audio_segment, crossfade=crossfade_ms)
                        combined_audio = combined_audio + pause_segment
                    else:
                        # Simple concatenation with pause: previous_audio + pause + new_audio
                        combined_audio = combined_audio + pause_segment + audio_segment
                else:
                    # No pause requested, use original behavior
                    if crossfade_ms > 0:
                        combined_audio = combined_audio.append(audio_segment, crossfade=crossfade_ms)
                    else:
                        combined_audio = combined_audio + audio_segment
            
            duration_seconds = len(audio_segment) / 1000.0
            total_duration += duration_seconds
            processed_files.append({
                "filename": file_path.name,
                "duration_seconds": duration_seconds,
                "size_bytes": file_path.stat().st_size
            })
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise RuntimeError(f"Failed to process audio file {file_path.name}: {e}")
    
    if combined_audio is None:
        raise RuntimeError("No audio content to concatenate")
    
    # Export the combined audio
    logger.info(f"Exporting concatenated audio to: {output_path}")
    
    # Determine format from extension
    file_extension = output_path.suffix.lower()
    
    if file_extension == '.wav':
        combined_audio.export(str(output_path), format="wav")
    elif file_extension == '.mp3':
        combined_audio.export(str(output_path), format="mp3", bitrate="192k")
    elif file_extension == '.flac':
        combined_audio.export(str(output_path), format="flac")
    else:
        # Default to WAV
        combined_audio.export(str(output_path), format="wav")
    
    processing_time = time.time() - start_time
    
    # Calculate final file info
    final_duration = len(combined_audio) / 1000.0
    final_size = output_path.stat().st_size if output_path.exists() else 0
    
    logger.info(f"Concatenation completed in {processing_time:.2f}s")
    logger.info(f"Final audio: {final_duration:.2f}s, {final_size} bytes")
    logger.info(f"Total pause duration: {total_pause_duration/1000:.2f}s")
    
    return {
        "total_duration_seconds": final_duration,
        "file_count": len(file_paths),
        "processing_time_seconds": processing_time,
        "processed_files": processed_files,
        "output_size_bytes": final_size,
        "crossfade_ms": crossfade_ms,
        "normalized": normalize_levels,
        "pause_duration_ms": pause_duration_ms,
        "pause_variation_ms": pause_variation_ms,
        "total_pause_duration_ms": total_pause_duration
    }
