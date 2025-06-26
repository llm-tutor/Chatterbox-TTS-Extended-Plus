# utils/audio/trimming.py - Audio Trimming Functions

import logging
import time
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Union

logger = logging.getLogger(__name__)


def apply_audio_trimming(audio_segment, filename: str, trim_threshold_ms: int) -> Dict:
    """
    Apply trimming to an AudioSegment object using temporary file analysis
    
    Args:
        audio_segment: AudioSegment to trim
        filename: Original filename for logging
        trim_threshold_ms: Silence threshold for trimming
        
    Returns:
        Dict with trimmed AudioSegment and metadata
    """
    import tempfile
    from .analysis import detect_silence_boundaries
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        temp_path = Path(temp_file.name)
    
    try:
        # Export current audio segment to temp file for analysis
        audio_segment.export(str(temp_path), format="wav")
        
        # Use existing trim logic
        trim_start_ms, trim_end_ms = detect_silence_boundaries(
            temp_path, trim_threshold_ms, -40.0
        )
        
        if trim_start_ms > 0 or trim_end_ms > 0:
            # Apply trimming to the AudioSegment
            original_duration_ms = len(audio_segment)
            start_pos = trim_start_ms
            end_pos = original_duration_ms - trim_end_ms
            
            if start_pos < end_pos:
                trimmed_segment = audio_segment[start_pos:end_pos]
                
                return {
                    "audio_segment": trimmed_segment,
                    "trimmed": True,
                    "original_duration_ms": original_duration_ms,
                    "trimmed_duration_ms": len(trimmed_segment),
                    "leading_silence_removed_ms": trim_start_ms,
                    "trailing_silence_removed_ms": trim_end_ms
                }
            else:
                logger.warning(f"Invalid trim bounds for {filename}, skipping trim")
        
        # No trimming needed or invalid bounds
        return {
            "audio_segment": audio_segment,
            "trimmed": False,
            "original_duration_ms": len(audio_segment),
            "trimmed_duration_ms": len(audio_segment),
            "leading_silence_removed_ms": 0,
            "trailing_silence_removed_ms": 0
        }
    
    finally:
        # Cleanup temp file
        if temp_path.exists():
            temp_path.unlink()


def trim_audio_file(input_path: Path, output_path: Path, 
                   threshold_ms: int = 200, silence_thresh_db: float = -40.0) -> Dict:
    """
    Trim extraneous silence from audio file
    
    Args:
        input_path: Input audio file path
        output_path: Output audio file path
        threshold_ms: Minimum silence duration to consider for trimming
        silence_thresh_db: dB threshold for silence detection
    
    Returns:
        Metadata about the trimming operation
    """
    from .analysis import detect_silence_boundaries, normalize_audio_format
    from .processing import get_audio_duration_ms
    
    logger.info(f"Trimming audio file: {input_path.name}")
    start_time = time.time()
    
    # Detect silence boundaries
    trim_start_ms, trim_end_ms = detect_silence_boundaries(
        input_path, threshold_ms, silence_thresh_db
    )
    
    original_duration_ms = get_audio_duration_ms(input_path)
    
    if trim_start_ms == 0 and trim_end_ms == 0:
        # No trimming needed, copy file
        logger.info(f"No trimming needed for {input_path.name}")
        if input_path != output_path:
            shutil.copy2(input_path, output_path)
        
        return {
            "trimmed": False,
            "original_duration_ms": original_duration_ms,
            "trimmed_duration_ms": original_duration_ms,
            "leading_silence_removed_ms": 0,
            "trailing_silence_removed_ms": 0,
            "processing_time_seconds": time.time() - start_time,
            "threshold_ms": threshold_ms,
            "silence_thresh_db": silence_thresh_db
        }
    
    # Load and trim audio
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(str(input_path))
    except Exception as load_error:
        logger.error(f"Could not load audio file {input_path}: {load_error}")
        raise
    
    # Handle unusual audio formats by converting if needed
    audio = normalize_audio_format(audio, input_path)
    
    # Apply trimming (pydub uses milliseconds)
    start_trim_ms = int(trim_start_ms)
    end_trim_ms = int(len(audio) - trim_end_ms)
    
    # Ensure we don't trim beyond the audio bounds
    start_trim_ms = max(0, start_trim_ms)
    end_trim_ms = min(len(audio), max(start_trim_ms + 100, end_trim_ms))  # Ensure at least 100ms remains
    
    trimmed_audio = audio[start_trim_ms:end_trim_ms]
    
    # Export trimmed audio
    try:
        trimmed_audio.export(str(output_path), format="wav")
    except Exception as export_error:
        logger.error(f"Could not export trimmed audio: {export_error}")
        raise
    
    processing_time = time.time() - start_time
    
    logger.info(f"Trimmed {input_path.name}: {original_duration_ms:.0f}ms → {len(trimmed_audio):.0f}ms "
                f"(removed {trim_start_ms:.1f}ms + {trim_end_ms:.1f}ms)")
    
    return {
        "trimmed": True,
        "original_duration_ms": len(audio),
        "trimmed_duration_ms": len(trimmed_audio),
        "leading_silence_removed_ms": trim_start_ms,
        "trailing_silence_removed_ms": trim_end_ms,
        "processing_time_seconds": processing_time,
        "threshold_ms": threshold_ms,
        "silence_thresh_db": silence_thresh_db
    }
