# utils/audio/analysis.py - Audio Analysis and Format Normalization Functions

import logging
from pathlib import Path
from typing import Optional, Tuple, Union
import numpy as np

logger = logging.getLogger(__name__)


def normalize_audio_format(audio_segment, source_path: Path):
    """
    Normalize audio format to handle unusual bit depths (e.g., 64-bit from speed_factor processing)
    
    Args:
        audio_segment: AudioSegment to normalize
        source_path: Original file path (for temp file naming and logging)
    
    Returns:
        AudioSegment with normalized format (16-bit PCM)
    """
    from pydub import AudioSegment  # Import here to avoid circular imports
    
    if audio_segment.sample_width <= 4:  # <= 32-bit, already compatible
        return audio_segment
    
    logger.debug(f"Converting {audio_segment.sample_width*8}-bit audio to 16-bit for compatibility: {source_path.name}")
    
    try:
        import soundfile as sf
        import numpy as np
        
        # Load with soundfile and convert to standard format
        data, samplerate = sf.read(str(source_path))
        
        # Ensure data is in proper range for 16-bit
        if data.dtype != np.int16:
            # Normalize to [-1, 1] then convert to 16-bit
            if np.max(np.abs(data)) > 1.0:
                data = data / np.max(np.abs(data))
            data = (data * 32767).astype(np.int16)
        
        # Create temp file with standard format
        temp_converted = source_path.with_suffix('.temp_converted.wav')
        sf.write(str(temp_converted), data, samplerate, subtype='PCM_16')
        
        # Load the converted file with pydub
        normalized_audio = AudioSegment.from_file(str(temp_converted))
        
        # Clean up temp file
        temp_converted.unlink(missing_ok=True)
        
        logger.debug(f"Successfully converted to {normalized_audio.sample_width*8}-bit format")
        return normalized_audio
        
    except Exception as conv_error:
        logger.warning(f"Could not convert audio format for {source_path.name}: {conv_error}")
        # If conversion fails, return original and hope for the best
        return audio_segment

def detect_silence_boundaries(audio_path: Path, threshold_ms: int = 200, 
                            silence_thresh_db: float = -40.0) -> tuple:
    """
    Detect leading and trailing silence in audio file
    
    Args:
        audio_path: Path to audio file
        threshold_ms: Minimum silence duration to consider "extraneous"
        silence_thresh_db: dB threshold for silence detection
    
    Returns:
        (trim_start_ms, trim_end_ms) - amounts to trim from start/end
    """
    try:
        import librosa
        import numpy as np
    except ImportError as e:
        logger.warning(f"librosa not available for silence detection: {e}")
        return (0, 0)
    
    try:
        # Load audio with librosa for precise analysis
        y, sr = librosa.load(str(audio_path), sr=None)
        
        if len(y) == 0:
            logger.warning(f"Empty audio file: {audio_path}")
            return (0, 0)
        
        # Find non-silent regions using librosa's split function
        non_silent_intervals = librosa.effects.split(
            y, 
            top_db=-silence_thresh_db,
            frame_length=2048,
            hop_length=512
        )
        
        if len(non_silent_intervals) == 0:
            # Entire file is silence - don't trim to avoid empty file
            logger.warning(f"Entire file appears to be silence: {audio_path}")
            return (0, 0)
        
        # Calculate leading and trailing silence
        first_sound_sample = non_silent_intervals[0][0]
        last_sound_sample = non_silent_intervals[-1][1]
        
        # Convert samples to milliseconds
        leading_silence_ms = (first_sound_sample / sr) * 1000
        trailing_silence_ms = ((len(y) - last_sound_sample) / sr) * 1000
        
        # Only trim if silence exceeds threshold
        trim_start_ms = max(0, leading_silence_ms - 50) if leading_silence_ms > threshold_ms else 0
        trim_end_ms = max(0, trailing_silence_ms - 50) if trailing_silence_ms > threshold_ms else 0
        
        logger.debug(f"Silence analysis for {audio_path.name}: leading={leading_silence_ms:.1f}ms, trailing={trailing_silence_ms:.1f}ms")
        logger.debug(f"Trim recommendation: start={trim_start_ms:.1f}ms, end={trim_end_ms:.1f}ms")
        
        return (trim_start_ms, trim_end_ms)
        
    except Exception as e:
        logger.error(f"Error detecting silence boundaries in {audio_path}: {e}")
        return (0, 0)
