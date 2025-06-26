# utils/concatenation/advanced.py - Advanced Concatenation Functions

import logging
import time
import shutil
import tempfile
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union

logger = logging.getLogger(__name__)


def concatenate_with_silence(parsed_items: List[Dict], output_path: Path, 
                           normalize_levels: bool = True, crossfade_ms: int = 0,
                           outputs_dir: Path = None, trim: bool = False, 
                           trim_threshold_ms: int = 200, pause_duration_ms: int = 0,
                           pause_variation_ms: int = 0) -> Dict[str, Any]:
    """
    Concatenate audio files and silence segments based on parsed instructions with mixed-mode support
    
    This function supports mixed manual silence and natural pause modes. Manual silences are applied
    where explicitly specified, while natural pauses fill gaps between consecutive audio files.
    
    Args:
        parsed_items: Output from parse_concat_files() containing file and silence instructions
        output_path: Where to save the result
        normalize_levels: Whether to normalize audio levels
        crossfade_ms: Crossfade duration between audio segments (not applied to silence)
        outputs_dir: Directory where audio files are located
        trim: Whether to trim silence from input audio files before concatenation
        trim_threshold_ms: Silence threshold for trimming (default: 200ms)
        pause_duration_ms: Natural pause duration between audio files (when no manual silence)
        pause_variation_ms: Randomization range for natural pauses
    
    Returns:
        Metadata about the concatenation process
    """
    try:
        from pydub import AudioSegment
    except ImportError:
        raise ImportError("pydub is required for audio concatenation")
    
    from ..audio.analysis import normalize_audio_format
    from ..audio.trimming import apply_audio_trimming
    from .parsing import generate_silence_segment, determine_gap_type, generate_natural_pause_duration
    
    start_time = time.time()
    combined_audio = AudioSegment.empty()
    processing_info = []
    total_duration = 0
    silence_count = 0
    file_count = 0
    natural_pause_count = 0
    
    logger.info(f"Starting enhanced mixed-mode concatenation with {len(parsed_items)} segments")
    
    # Process items with gap-aware logic
    i = 0
    while i < len(parsed_items):
        item = parsed_items[i]
        
        if item["type"] == "silence":
            # Handle explicit silence segments
            silence_segment = generate_silence_segment(item["duration_ms"])
            combined_audio += silence_segment
            
            silence_count += 1
            duration_seconds = item["duration_ms"] / 1000.0
            total_duration += duration_seconds
            
            processing_info.append({
                "type": "manual_silence",
                "duration_ms": item["duration_ms"],
                "duration_seconds": duration_seconds,
                "notation": item["source"]
            })
            
            logger.info(f"Added {item['duration_ms']}ms manual silence from notation: {item['source']}")
            i += 1
            
        elif item["type"] == "file":
            # Process audio file
            file_count += 1
            filename = item["source"]
            
            # Resolve and load audio file
            if outputs_dir:
                file_path = outputs_dir / filename
            else:
                file_path = Path(filename)
            
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")
            
            logger.info(f"Processing audio file {file_count}: {filename}")
            
            try:
                # Load and process audio file
                audio_segment = AudioSegment.from_file(str(file_path))
                audio_segment = normalize_audio_format(audio_segment, file_path)
                
                # Apply trimming if requested
                trim_info = {"trimmed": False}
                if trim:
                    trim_result = apply_audio_trimming(audio_segment, filename, trim_threshold_ms)
                    audio_segment = trim_result["audio_segment"]
                    # Extract metadata without the AudioSegment object
                    trim_info = {
                        "trimmed": trim_result["trimmed"],
                        "original_duration_ms": trim_result["original_duration_ms"],
                        "trimmed_duration_ms": trim_result["trimmed_duration_ms"],
                        "leading_silence_removed_ms": trim_result["leading_silence_removed_ms"],
                        "trailing_silence_removed_ms": trim_result["trailing_silence_removed_ms"]
                    }
                
                # Normalize levels if requested
                if normalize_levels:
                    target_dBFS = -20.0
                    change_in_dBFS = target_dBFS - audio_segment.dBFS
                    audio_segment = audio_segment.apply_gain(change_in_dBFS)
