# utils/concatenation/parsing.py - Concatenation Parsing and Helper Functions

import re
import logging
import random
from typing import List, Dict, Union

logger = logging.getLogger(__name__)


def parse_concat_files(files: List[str]) -> List[Dict[str, Union[str, int]]]:
    """
    Parse mixed file/silence array into processing instructions
    
    Args:
        files: List of filenames and silence notations like "(500ms)" or "(1.5s)"
    
    Returns:
        List of {"type": "file"|"silence", "source": str, "duration_ms": int}
        
    Raises:
        ValueError: If silence notation is invalid or duration out of range
    """
    silence_pattern = re.compile(r'^\((\d+(?:\.\d+)?)(ms|s)\)$')
    parsed_items = []
    
    for item in files:
        silence_match = silence_pattern.match(item)
        if silence_match:
            duration_value = float(silence_match.group(1))
            unit = silence_match.group(2)
            
            # Convert to milliseconds
            duration_ms = int(duration_value * 1000) if unit == 's' else int(duration_value)
            
            # Validate duration range (50ms to 10s)
            if not (50 <= duration_ms <= 10000):
                raise ValueError(f"Silence duration must be between 50ms and 10s, got: {item}")
            
            parsed_items.append({
                "type": "silence",
                "source": item,
                "duration_ms": duration_ms
            })
        else:
            parsed_items.append({
                "type": "file",
                "source": item,
                "duration_ms": 0  # Will be calculated from actual file
            })
    
    return parsed_items


def generate_silence_segment(duration_ms: int, sample_rate: int = 22050) -> 'AudioSegment':
    """
    Generate a silence segment of specified duration
    
    Args:
        duration_ms: Duration in milliseconds
        sample_rate: Target sample rate (match other audio)
    
    Returns:
        AudioSegment containing silence
    """
    try:
        from pydub import AudioSegment
    except ImportError:
        raise ImportError("pydub is required for silence generation")
    
    return AudioSegment.silent(duration=duration_ms, frame_rate=sample_rate)


def determine_gap_type(current_item: Dict, next_item: Dict, pause_duration_ms: int) -> str:
    """
    Determine what type of gap should be inserted between current and next items
    
    Args:
        current_item: Current item in the sequence 
        next_item: Next item in the sequence
        pause_duration_ms: Natural pause duration parameter
        
    Returns:
        'manual_silence' | 'natural_pause' | 'no_gap'
    """
    # If next item is manual silence, it will be handled by the main loop
    if next_item["type"] == "silence":
        return 'manual_silence'
    
    # Between two consecutive audio files
    if current_item["type"] == "file" and next_item["type"] == "file":
        if pause_duration_ms > 0:
            return 'natural_pause'
        else:
            return 'no_gap'
    
    return 'no_gap'


def generate_natural_pause_duration(base_duration_ms: int, variation_ms: int) -> int:
    """
    Generate a natural pause duration with random variation
    
    Args:
        base_duration_ms: Base pause duration
        variation_ms: Maximum variation range (±)
        
    Returns:
        Randomized pause duration in milliseconds
    """
    if variation_ms <= 0:
        return base_duration_ms
    
    variation = random.randint(-variation_ms, variation_ms)
    result = base_duration_ms + variation
    
    # Ensure minimum pause of 50ms
    return max(50, result)
