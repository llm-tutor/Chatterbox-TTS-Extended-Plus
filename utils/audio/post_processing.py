"""
Audio post-processing utilities for TTS generation
Implements auto-editor and ffmpeg normalization from original Chatter.py
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

import ffmpeg
from monitoring import get_logger

logger = get_logger(__name__)


def apply_auto_editor_post_processing(
    audio_path: str, 
    generation_params: Dict[str, Any] = None
) -> str:
    """
    Apply auto-editor post-processing to audio file
    
    Ports the exact auto-editor logic from Chatter.py lines 968-989
    
    Args:
        audio_path: Path to the input audio file
        generation_params: Dictionary containing auto-editor parameters
        
    Returns:
        str: Path to the processed audio file (same as input path after processing)
        
    Raises:
        Exception: If auto-editor processing fails (logged but doesn't interrupt pipeline)
    """
    if not generation_params:
        generation_params = {}
        
    use_auto_editor = generation_params.get('use_auto_editor', False)
    if not use_auto_editor:
        return audio_path
    
    # Get auto-editor parameters
    keep_original_wav_ae = generation_params.get('keep_original_wav_ae', False)
    ae_threshold = generation_params.get('ae_threshold', 0.06)
    ae_margin = generation_params.get('ae_margin', 0.2)
    
    try:
        logger.info(f"🎬 Applying auto-editor post-processing to: {Path(audio_path).name}")
        logger.info(f"   ⚙️ Parameters: threshold={ae_threshold}, margin={ae_margin}s, keep_original={keep_original_wav_ae}")
        
        # Create paths for processing (use temp directory to avoid file association triggers)
        audio_path_obj = Path(audio_path)
        temp_dir = Path(tempfile.gettempdir())
        temp_cleaned = temp_dir / f"{audio_path_obj.stem}_cleaned.wav"
        
        if keep_original_wav_ae:
            backup_path = str(audio_path_obj.with_name(audio_path_obj.stem + "_original.wav"))
            os.rename(audio_path, backup_path)
            auto_editor_input = backup_path
        else:
            auto_editor_input = audio_path

        # Build auto-editor command (output to temp directory, don't open file)
        auto_editor_cmd = [
            "auto-editor",
            "--edit", f"audio:threshold={ae_threshold}",
            "--margin", f"{ae_margin}s",
            "--export", "audio",
            "--no-open",  # Prevent auto-editor from opening the file
            auto_editor_input,
            "-o", str(temp_cleaned)
        ]

        logger.info(f"   🔧 Running command: {' '.join(auto_editor_cmd)}")
        subprocess.run(auto_editor_cmd, check=True)

        if temp_cleaned.exists():
            # Move processed file back to original location
            shutil.move(str(temp_cleaned), audio_path)
            logger.info(f"   ✅ Auto-editor post-processing completed: {Path(audio_path).name}")
        else:
            logger.warning(f"   ⚠️ Auto-editor output not found: {temp_cleaned}")
            
    except Exception as e:
        logger.error(f"   ❌ Auto-editor post-processing failed: {e}")
        logger.info(f"   ℹ️ Continuing with original audio file")
        # Return original path as fallback (don't interrupt pipeline)
        
    return audio_path


def apply_ffmpeg_normalization_post_processing(
    audio_path: str, 
    generation_params: Dict[str, Any] = None
) -> str:
    """
    Apply ffmpeg audio normalization post-processing
    
    Ports the exact normalize_with_ffmpeg function from Chatter.py lines 370-391
    
    Args:
        audio_path: Path to the input audio file
        generation_params: Dictionary containing normalization parameters
        
    Returns:
        str: Path to the processed audio file (same as input path after processing)
        
    Raises:
        Exception: If ffmpeg normalization fails (logged but doesn't interrupt pipeline)
    """
    if not generation_params:
        generation_params = {}
        
    normalize_audio = generation_params.get('normalize_audio', False)
    if not normalize_audio:
        return audio_path
    
    # Get normalization parameters
    normalize_method = generation_params.get('normalize_method', 'ebu')
    normalize_level = generation_params.get('normalize_level', -24.0)
    normalize_tp = generation_params.get('normalize_tp', -2.0)
    normalize_lra = generation_params.get('normalize_lra', 7.0)
    
    try:
        logger.info(f"🔊 Applying ffmpeg normalization to: {Path(audio_path).name}")
        logger.info(f"   ⚙️ Method: {normalize_method}, Level: {normalize_level}, TP: {normalize_tp}, LRA: {normalize_lra}")
        
        # Create temporary output file
        audio_path_obj = Path(audio_path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_output = temp_file.name
        
        # Apply normalization based on method (exact logic from Chatter.py)
        if normalize_method == "ebu":
            loudnorm = f"loudnorm=I={normalize_level}:TP={normalize_tp}:LRA={normalize_lra}"
            logger.info(f"   🔧 EBU normalization filter: {loudnorm}")
            (
                ffmpeg
                .input(audio_path)
                .output(temp_output, af=loudnorm)
                .overwrite_output()
                .run(quiet=True)
            )
        elif normalize_method == "peak":
            logger.info(f"   🔧 Peak normalization using dynaudnorm")
            (
                ffmpeg
                .input(audio_path)
                .output(temp_output, af="dynaudnorm")
                .overwrite_output()
                .run(quiet=True)
            )
        else:
            raise ValueError(f"Unknown normalization method: {normalize_method}")
        
        # Replace original file with normalized version (cross-drive compatible)
        shutil.move(temp_output, audio_path)
        logger.info(f"   ✅ FFmpeg normalization completed: {Path(audio_path).name}")
        
    except Exception as e:
        logger.error(f"   ❌ FFmpeg normalization failed: {e}")
        logger.info(f"   ℹ️ Continuing with original audio file")
        # Clean up temp file if it exists
        if 'temp_output' in locals() and os.path.exists(temp_output):
            try:
                os.unlink(temp_output)
            except:
                pass
        # Return original path as fallback (don't interrupt pipeline)
        
    return audio_path


def apply_complete_post_processing_pipeline(
    audio_path: str, 
    generation_params: Dict[str, Any] = None
) -> str:
    """
    Apply complete post-processing pipeline in correct order
    
    Order matches Chatter.py:
    1. Auto-editor (if enabled)
    2. FFmpeg normalization (if enabled)
    
    Args:
        audio_path: Path to the input audio file
        generation_params: Dictionary containing all post-processing parameters
        
    Returns:
        str: Path to the fully processed audio file
    """
    if not generation_params:
        generation_params = {}
    
    # Step 1: Auto-editor post-processing
    processed_path = apply_auto_editor_post_processing(audio_path, generation_params)
    
    # Step 2: FFmpeg normalization
    processed_path = apply_ffmpeg_normalization_post_processing(processed_path, generation_params)
    
    return processed_path
