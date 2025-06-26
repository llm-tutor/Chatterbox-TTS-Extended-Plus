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
                
                # Add audio to combined stream with appropriate joining logic
                if len(combined_audio) == 0:
                    # First audio segment
                    combined_audio = audio_segment
                    logger.info(f"Added first audio segment: {filename}")
                else:
                    # Determine if crossfade should be applied
                    # Crossfade only applies between consecutive audio files
                    last_info = processing_info[-1] if processing_info else None
                    can_crossfade = (
                        crossfade_ms > 0 and 
                        last_info and 
                        last_info["type"] == "file"
                    )
                    
                    if can_crossfade:
                        combined_audio = combined_audio.append(audio_segment, crossfade=crossfade_ms)
                        logger.info(f"Applied {crossfade_ms}ms crossfade to {filename}")
                    else:
                        combined_audio += audio_segment
                        logger.info(f"Direct joined audio segment: {filename}")
                
                duration_seconds = len(audio_segment) / 1000.0
                total_duration += duration_seconds
                
                processing_info.append({
                    "type": "file",
                    "filename": filename,
                    "duration_seconds": duration_seconds,
                    "size_bytes": file_path.stat().st_size,
                    "trim_info": trim_info if trim else None
                })
                
                # Look ahead to determine gap handling for next iteration
                next_index = i + 1
                if next_index < len(parsed_items):
                    next_item = parsed_items[next_index]
                    gap_type = determine_gap_type(item, next_item, pause_duration_ms)
                    
                    if gap_type == "natural_pause":
                        # Insert natural pause between this file and the next
                        pause_duration = generate_natural_pause_duration(pause_duration_ms, pause_variation_ms)
                        pause_segment = generate_silence_segment(pause_duration)
                        combined_audio += pause_segment
                        
                        natural_pause_count += 1
                        pause_seconds = pause_duration / 1000.0
                        total_duration += pause_seconds
                        
                        processing_info.append({
                            "type": "natural_pause",
                            "duration_ms": pause_duration,
                            "duration_seconds": pause_seconds,
                            "base_duration_ms": pause_duration_ms,
                            "variation_applied_ms": pause_duration - pause_duration_ms
                        })
                        
                        logger.info(f"Added {pause_duration}ms natural pause after {filename}")
                
                i += 1
                
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                raise RuntimeError(f"Failed to process audio file {filename}: {e}")
        
        else:
            logger.warning(f"Unknown item type: {item.get('type')}")
            i += 1
    
    if len(combined_audio) == 0:
        raise RuntimeError("No audio content to concatenate")
    
    # Export the combined audio
    logger.info(f"Exporting enhanced concatenated audio to: {output_path}")
    
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
    
    logger.info(f"Enhanced mixed-mode concatenation completed in {processing_time:.2f}s")
    logger.info(f"Final audio: {final_duration:.2f}s, {final_size} bytes")
    logger.info(f"Processed: {file_count} audio files, {silence_count} manual silences, {natural_pause_count} natural pauses")
    
    # Calculate trimming summary if trimming was applied
    trim_summary = None
    if trim:
        trim_items = [item for item in processing_info if item["type"] == "file" and item.get("trim_info")]
        if trim_items:
            total_files = len(trim_items)
            files_trimmed = sum(1 for item in trim_items if item["trim_info"]["trimmed"])
            total_silence_removed = sum(
                item["trim_info"]["leading_silence_removed_ms"] + item["trim_info"]["trailing_silence_removed_ms"]
                for item in trim_items if item["trim_info"]["trimmed"]
            ) / 1000.0
            
            trim_summary = {
                "trim_applied": True,
                "trim_threshold_ms": trim_threshold_ms,
                "total_files": total_files,
                "files_trimmed": files_trimmed,
                "files_not_trimmed": total_files - files_trimmed,
                "total_silence_removed_seconds": total_silence_removed
            }

    return {
        "total_duration_seconds": final_duration,
        "file_count": file_count,
        "silence_segments": silence_count,
        "natural_pauses": natural_pause_count,
        "total_segments": len(parsed_items),
        "processing_time_seconds": processing_time,
        "processing_details": processing_info,
        "output_size_bytes": final_size,
        "crossfade_ms": crossfade_ms,
        "normalized": normalize_levels,
        "trim_summary": trim_summary
    }



def concatenate_with_trimming(file_paths: List[Path], output_path: Path,
                            trim: bool = False, trim_threshold_ms: int = 200,
                            normalize_levels: bool = True, crossfade_ms: int = 0,
                            pause_duration_ms: int = 600, pause_variation_ms: int = 200,
                            silence_thresh_db: float = -40.0) -> Dict[str, Any]:
    """
    Enhanced concatenation with optional pre-trimming of input files
    
    Args:
        file_paths: List of paths to audio files to concatenate
        output_path: Output file path
        trim: Whether to trim silence from input files before concatenation
        trim_threshold_ms: Minimum silence duration to consider for trimming
        normalize_levels: Whether to normalize audio levels
        crossfade_ms: Crossfade duration in milliseconds
        pause_duration_ms: Base pause duration between clips in milliseconds
        pause_variation_ms: Random variation in pause duration in milliseconds
        silence_thresh_db: dB threshold for silence detection
    
    Returns:
        Dictionary with concatenation and trimming metadata
    """
    import shutil
    import tempfile
    
    from ..audio.trimming import trim_audio_file
    from .basic import concatenate_audio_files
    
    if not trim:
        # Use existing concatenation logic
        return concatenate_audio_files(
            file_paths=file_paths,
            output_path=output_path,
            normalize_levels=normalize_levels,
            crossfade_ms=crossfade_ms,
            pause_duration_ms=pause_duration_ms,
            pause_variation_ms=pause_variation_ms
        )
    
    # Pre-process files with trimming
    logger.info(f"Starting concatenation with trimming: {len(file_paths)} files")
    
    # Create temporary directory for trimmed files
    temp_dir = Path(tempfile.mkdtemp(prefix="trim_"))
    
    trimmed_files = []
    trim_metadata = []
    start_time = time.time()
    
    try:
        # Trim each file
        for i, file_path in enumerate(file_paths):
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")
            
            logger.info(f"Trimming file {i+1}/{len(file_paths)}: {file_path.name}")
            
            trimmed_path = temp_dir / f"trimmed_{i:03d}_{file_path.name}"
            trim_info = trim_audio_file(
                file_path, trimmed_path, trim_threshold_ms, silence_thresh_db
            )
            
            trimmed_files.append(trimmed_path)
            trim_metadata.append({
                "original_file": str(file_path),
                "trimmed_file": str(trimmed_path),
                "trim_info": trim_info
            })
        
        # Concatenate trimmed files
        logger.info("Concatenating trimmed files...")
        concat_result = concatenate_audio_files(
            file_paths=trimmed_files,
            output_path=output_path,
            normalize_levels=normalize_levels,
            crossfade_ms=crossfade_ms,
            pause_duration_ms=pause_duration_ms,
            pause_variation_ms=pause_variation_ms
        )
        
        # Add trimming metadata to result
        total_original_duration = sum(item["trim_info"]["original_duration_ms"] for item in trim_metadata) / 1000.0
        total_trimmed_duration = sum(item["trim_info"]["trimmed_duration_ms"] for item in trim_metadata) / 1000.0
        total_silence_removed = sum(
            item["trim_info"]["leading_silence_removed_ms"] + item["trim_info"]["trailing_silence_removed_ms"] 
            for item in trim_metadata
        ) / 1000.0
        
        concat_result.update({
            "trim_applied": True,
            "trim_metadata": trim_metadata,
            "trim_threshold_ms": trim_threshold_ms,
            "silence_thresh_db": silence_thresh_db,
            "total_original_duration_seconds": total_original_duration,
            "total_trimmed_duration_seconds": total_trimmed_duration,
            "total_silence_removed_seconds": total_silence_removed,
            "files_trimmed": sum(1 for item in trim_metadata if item["trim_info"]["trimmed"]),
            "files_not_trimmed": sum(1 for item in trim_metadata if not item["trim_info"]["trimmed"])
        })
        
        processing_time = time.time() - start_time
        concat_result["total_processing_time_seconds"] = processing_time
        
        logger.info(f"Concatenation with trimming completed in {processing_time:.2f}s")
        logger.info(f"Silence removed: {total_silence_removed:.2f}s from {len(file_paths)} files")
        
        return concat_result
        
    finally:
        # Cleanup temporary files
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.debug(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Error cleaning up temporary directory {temp_dir}: {e}")



def concatenate_with_mixed_sources(
    segments: list, upload_paths: dict, output_path: Path, outputs_dir: Path,
    normalize_levels: bool = True, crossfade_ms: int = 0,
    trim: bool = False, trim_threshold_ms: int = 200,
    pause_duration_ms: int = 0, pause_variation_ms: int = 0) -> dict:
    """
    Concatenate audio from mixed sources (server files, uploads, silence)
    
    Args:
        segments: List of MixedConcatSegment objects defining the concatenation order
        upload_paths: Dictionary mapping upload indices to their temporary file paths
        output_path: Where to save the concatenated result
        outputs_dir: Directory containing server files
        normalize_levels: Whether to normalize audio levels
        crossfade_ms: Crossfade duration between audio segments
        trim: Whether to trim silence from audio files before concatenation
        trim_threshold_ms: Silence threshold for trimming
        pause_duration_ms: Natural pause duration between audio files (when no manual silence)
        pause_variation_ms: Randomization range for natural pauses
    
    Returns:
        Dictionary with concatenation metadata
    """
    import random
    import re
    from datetime import datetime
    
    from ..audio.trimming import apply_audio_trimming
    
    try:
        from pydub import AudioSegment
        
        start_time = time.time()
        
        logger.info(f"Starting mixed source concatenation with {len(segments)} segments")
        
        # Check if we have any manual silence (affects pause behavior)
        has_manual_silence = any(seg.type == 'silence' for seg in segments)
        
        # Process segments and build concatenation queue
        audio_segments = []
        audio_segment_count = 0
        silence_count = 0
        processing_metadata = []
        
        for i, segment in enumerate(segments):
            if segment.type == 'server_file':
                # Load server file
                file_path = outputs_dir / segment.source
                logger.debug(f"Loading server file: {file_path}")
                
                if trim:
                    # Apply trimming to server file
                    audio_segment = AudioSegment.from_file(str(file_path))
                    trim_result = apply_audio_trimming(audio_segment, segment.source, trim_threshold_ms)
                    audio_segment = trim_result["audio_segment"]
                    # Extract serializable trim info (exclude AudioSegment object)
                    trim_info = {k: v for k, v in trim_result.items() if k != "audio_segment"}
                    processing_metadata.append({
                        "segment_index": i,
                        "type": "server_file",
                        "source": segment.source,
                        "trim_info": trim_info
                    })
                else:
                    audio_segment = AudioSegment.from_file(str(file_path))
                    processing_metadata.append({
                        "segment_index": i,
                        "type": "server_file",
                        "source": segment.source,
                        "trim_info": {"trimmed": False}
                    })
                
                if normalize_levels:
                    audio_segment = audio_segment.normalize()
                
                audio_segments.append(audio_segment)
                audio_segment_count += 1
                
            elif segment.type == 'upload':
                # Load uploaded file
                upload_path = upload_paths[segment.index]
                logger.debug(f"Loading uploaded file: {upload_path}")
                
                if trim:
                    # Apply trimming to uploaded file
                    audio_segment = AudioSegment.from_file(str(upload_path))
                    trim_result = apply_audio_trimming(audio_segment, str(upload_path.name), trim_threshold_ms)
                    audio_segment = trim_result["audio_segment"]
                    # Extract serializable trim info (exclude AudioSegment object)
                    trim_info = {k: v for k, v in trim_result.items() if k != "audio_segment"}
                    processing_metadata.append({
                        "segment_index": i,
                        "type": "upload",
                        "index": segment.index,
                        "source": str(upload_path.name),
                        "trim_info": trim_info
                    })
                else:
                    audio_segment = AudioSegment.from_file(str(upload_path))
                    processing_metadata.append({
                        "segment_index": i,
                        "type": "upload",
                        "index": segment.index,
                        "source": str(upload_path.name),
                        "trim_info": {"trimmed": False}
                    })
                
                if normalize_levels:
                    audio_segment = audio_segment.normalize()
                
                audio_segments.append(audio_segment)
                audio_segment_count += 1
                
            elif segment.type == 'silence':
                # Parse silence duration
                silence_pattern = re.compile(r'^\((\d+(?:\.\d+)?)(ms|s)\)$')
                match = silence_pattern.match(segment.source)
                if not match:
                    raise ValueError(f"Invalid silence notation: {segment.source}")
                
                duration_value = float(match.group(1))
                unit = match.group(2)
                duration_ms = duration_value * 1000 if unit == 's' else duration_value
                
                # Generate silence segment
                silence_segment = AudioSegment.silent(duration=int(duration_ms))
                audio_segments.append(silence_segment)
                silence_count += 1
                
                processing_metadata.append({
                    "segment_index": i,
                    "type": "silence",
                    "source": segment.source,
                    "duration_ms": duration_ms
                })
                
                logger.debug(f"Generated silence: {duration_ms}ms")
        
        # Build final concatenated audio with proper gap handling
        logger.info(f"Concatenating {len(audio_segments)} segments (audio: {audio_segment_count}, silence: {silence_count})")
        
        if len(audio_segments) == 0:
            raise ValueError("No audio segments to concatenate")
        
        # Start with first segment
        final_audio = audio_segments[0]
        
        # Process remaining segments with gap logic
        for i in range(1, len(audio_segments)):
            current_segment = audio_segments[i]
            prev_segment_info = processing_metadata[i-1]
            current_segment_info = processing_metadata[i]
            
            # Determine what goes between segments
            gap_audio = None
            
            # Check if there was an explicit silence between these segments
            if (i > 1 and processing_metadata[i-1]["type"] == "silence"):
                # Previous segment was silence, no additional gap needed
                gap_audio = None
            elif not has_manual_silence and pause_duration_ms > 0:
                # Add natural pause between consecutive audio segments
                if (prev_segment_info["type"] in ["server_file", "upload"] and 
                    current_segment_info["type"] in ["server_file", "upload"]):
                    
                    # Calculate pause with variation
                    if pause_variation_ms > 0:
                        variation = random.randint(-pause_variation_ms, pause_variation_ms)
                        actual_pause_ms = max(50, pause_duration_ms + variation)
                    else:
                        actual_pause_ms = pause_duration_ms
                    
                    gap_audio = AudioSegment.silent(duration=actual_pause_ms)
                    logger.debug(f"Added natural pause: {actual_pause_ms}ms between segments {i-1} and {i}")
            
            # Apply crossfading if specified (only between audio segments, not silence)
            if (crossfade_ms > 0 and gap_audio is None and 
                prev_segment_info["type"] in ["server_file", "upload"] and 
                current_segment_info["type"] in ["server_file", "upload"]):
                
                # Apply crossfade
                crossfade_duration = min(crossfade_ms, len(final_audio), len(current_segment))
                final_audio = final_audio.append(current_segment, crossfade=crossfade_duration)
                logger.debug(f"Applied crossfade: {crossfade_duration}ms between segments {i-1} and {i}")
            else:
                # Standard concatenation (with optional gap)
                if gap_audio:
                    final_audio = final_audio + gap_audio
                final_audio = final_audio + current_segment
        
        # Export the final audio
        logger.info(f"Exporting concatenated audio to {output_path}")
        final_audio.export(str(output_path), format=output_path.suffix[1:])
        
        # Calculate metadata
        processing_time = time.time() - start_time
        total_duration_seconds = len(final_audio) / 1000.0
        
        # Prepare generation info
        generation_info = {
            "processing_time_seconds": processing_time,
            "total_duration_seconds": total_duration_seconds,
            "audio_segment_count": audio_segment_count,
            "silence_segment_count": silence_count,
            "crossfade_applied": crossfade_ms > 0,
            "normalization_applied": normalize_levels,
            "trim_applied": trim,
            "manual_silence_mode": has_manual_silence
        }
        
        if trim:
            # Add trim statistics
            trim_stats = {
                "files_trimmed": sum(1 for meta in processing_metadata 
                                   if meta.get("trim_info", {}).get("trimmed", False)),
                "total_silence_removed_ms": sum(
                    meta.get("trim_info", {}).get("leading_silence_removed_ms", 0) +
                    meta.get("trim_info", {}).get("trailing_silence_removed_ms", 0)
                    for meta in processing_metadata
                )
            }
            generation_info.update(trim_stats)
        
        if not has_manual_silence and pause_duration_ms > 0:
            generation_info.update({
                "natural_pauses_added": sum(1 for i in range(1, len(processing_metadata))
                                          if (processing_metadata[i-1]["type"] in ["server_file", "upload"] and
                                              processing_metadata[i]["type"] in ["server_file", "upload"])),
                "pause_duration_ms": pause_duration_ms,
                "pause_variation_ms": pause_variation_ms
            })
        
        logger.info(f"Mixed source concatenation completed in {processing_time:.2f}s")
        logger.info(f"Result: {total_duration_seconds:.2f}s audio from {audio_segment_count} files + {silence_count} silence segments")
        
        return {
            "type": "concat",
            "status": "success",
            "total_duration_seconds": total_duration_seconds,
            "processing_metadata": processing_metadata,
            "generation_info": generation_info
        }
        
    except ImportError as e:
        raise ImportError("pydub is required for audio concatenation") from e
    except Exception as e:
        logger.error(f"Error in mixed source concatenation: {e}")
        raise RuntimeError(f"Failed to concatenate mixed sources: {e}") from e
