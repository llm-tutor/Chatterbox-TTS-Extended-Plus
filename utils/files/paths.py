# utils/files/paths.py - Path Utilities

import logging
from pathlib import Path
from typing import Union, Optional

logger = logging.getLogger(__name__)


def normalize_audio_path(path_input: Union[str, Path]) -> Path:
    """Normalize audio path input to Path object"""
    if isinstance(path_input, str):
        return Path(path_input)
    return path_input


def get_audio_duration(file_path: Path) -> Optional[float]:
    """Get audio file duration in seconds"""
    try:
        import soundfile as sf
        with sf.SoundFile(str(file_path)) as f:
            return len(f) / f.samplerate
    except Exception as e:
        logger.warning(f"Could not get duration for {file_path}: {e}")
        return None
