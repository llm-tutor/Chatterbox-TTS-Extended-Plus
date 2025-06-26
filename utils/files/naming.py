# utils/files/naming.py - File Naming Functions

import time
import hashlib
import random
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Union

logger = logging.getLogger(__name__)


def generate_unique_filename(prefix: str = "output", extension: str = "wav") -> str:
    """Generate a unique filename with timestamp and hash"""
    timestamp = int(time.time())
    random_hash = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
    return f"{prefix}_{timestamp}_{random_hash}.{extension}"


def generate_enhanced_filename(generation_type: str, parameters: Dict[str, Any], extension: str = "wav") -> str:
    """
    Generate enhanced filename with timestamp and key parameters
    
    Format: {type}_{timestamp}_{microseconds}_{key_params}.{ext}
    
    Args:
        generation_type: 'tts', 'vc', or 'concat'
        parameters: Dictionary of generation parameters
        extension: File extension (wav, mp3, etc.)
    
    Returns:
        Enhanced filename string
    """
    # Get current timestamp with microseconds
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H%M%S")
    microseconds = now.microsecond

    # Extract key parameters based on generation type
    param_parts = []

    if generation_type == "tts":
        # Include key TTS parameters
        if "temperature" in parameters:
            param_parts.append(f"temp{parameters['temperature']}")
        if "seed" in parameters and parameters["seed"] != 0:
            param_parts.append(f"seed{parameters['seed']}")
        if "exaggeration" in parameters and parameters["exaggeration"] != 0.5:
            param_parts.append(f"exag{parameters['exaggeration']}")
        if "speed_factor" in parameters and parameters["speed_factor"] != 1.0:
            param_parts.append(f"speed{parameters['speed_factor']}")
        if "trim" in parameters and parameters["trim"]:
            trim_threshold = parameters.get("trim_threshold_ms", 200)
            param_parts.append(f"trim{trim_threshold}")

    elif generation_type == "vc":
        # Include key VC parameters
        if "chunk_sec" in parameters and parameters["chunk_sec"] != 60:
            param_parts.append(f"chunk{parameters['chunk_sec']}")
        if "overlap_sec" in parameters and parameters["overlap_sec"] != 0.1:
            param_parts.append(f"overlap{parameters['overlap_sec']}")
        # Include reference to target voice if available
        if "target_voice_source" in parameters:
            voice_name = Path(parameters["target_voice_source"]).stem
            # Sanitize and truncate voice name
            voice_name = re.sub(r'[^\w\-]', '', voice_name)[:10]
            param_parts.append(f"voice{voice_name}")

    elif generation_type == "concat":
        # Include concat-specific parameters
        if "file_count" in parameters:
            param_parts.append(f"{parameters['file_count']}files")

        # Add silence count if manual silences were used
        if "silence_segments" in parameters and parameters["silence_segments"] > 0:
            param_parts.append(f"sil{parameters['silence_segments']}")

        # Add pause parameters only if not using manual silence
        if not parameters.get("manual_silence", False):
            if "pause_duration_ms" in parameters and parameters["pause_duration_ms"] > 0:
                pause_ms = parameters["pause_duration_ms"]
                variation_ms = parameters.get("pause_variation_ms", 0)
                if variation_ms > 0:
                    param_parts.append(f"pause{pause_ms}v{variation_ms}")
                else:
                    param_parts.append(f"pause{pause_ms}")

        if "crossfade_ms" in parameters and parameters["crossfade_ms"] > 0:
            param_parts.append(f"fade{parameters['crossfade_ms']}")
        if "normalize_levels" in parameters and parameters["normalize_levels"]:
            param_parts.append("leveled")

        # Add trim parameters
        if parameters.get("trim", False):
            trim_threshold = parameters.get("trim_threshold_ms", 200)
            param_parts.append(f"trim{trim_threshold}")

    # Construct filename
    param_string = "_".join(param_parts) if param_parts else "default"

    return f"{generation_type}_{timestamp}_{microseconds:06d}_{param_string}.{extension}"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem usage"""
    # Remove/replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    # Ensure it's not empty
    if not filename:
        filename = "unnamed"
    return filename


def normalize_audio_path(path_input: Union[str, Path]) -> Path:
    """Normalize audio path input to Path object"""
    if isinstance(path_input, str):
        return Path(path_input)
    return path_input


def sanitize_file_path(file_path: str) -> str:
    """Sanitize file path for safe usage"""
    # Convert to Path and resolve any relative components
    path = Path(file_path)

    # Remove any directory traversal attempts
    path_parts = []
    for part in path.parts:
        if part in ('..', '.'):
            continue
        part = sanitize_filename(part)
        path_parts.append(part)

    # Reconstruct path using forward slashes (cross-platform)
    if path_parts:
        return '/'.join(path_parts)
    else:
        return "unnamed"
