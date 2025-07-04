# Phase 11 Extended Features: Manual Silence Insertion & Audio Trimming
## Design Document for Tasks 11.2, 11.3, and 11.4

### **Overview**

This document outlines the design and implementation approach for two major production-level features:
1. **Manual Silence Insertion** - User-controlled silence placement in concatenated audio
2. **Audio Trimming** - Automatic removal of extraneous silence from audio files

These features address real-world audio production needs for video creation, podcasting, and professional audio content.

---

## **Feature 1: Manual Silence Insertion** (Task 11.2)

### **Core Concept**
Allow users to insert precise silence durations at any point in the concatenation sequence using intuitive string notation.

### **API Design**

#### **Silence Notation Format**
```
"(duration[unit])"
```

**Supported Units**:
- `ms` - milliseconds
- `s` - seconds (supports decimals)

**Examples**:
- `"(500ms)"` - 500 milliseconds of silence
- `"(1.5s)"` - 1.5 seconds of silence
- `"(2s)"` - 2 seconds of silence

#### **Enhanced Files Array**
```json
{
  "files": [
    "(500ms)",           // Opening silence
    "intro.wav",         // First audio file
    "(800ms)",           // Dramatic pause
    "main_content.wav",  // Second audio file
    "(1.5s)",            // Longer break
    "conclusion.wav",    // Final audio file
    "(1.0s)"             // Closing silence
  ]
}
```

### **Implementation Details**

#### **Parsing Logic**
```python
import re
from typing import List, Dict, Union

def parse_concat_files(files: List[str]) -> List[Dict[str, Union[str, int]]]:
    """
    Parse mixed file/silence array into processing instructions
    
    Returns:
        List of {"type": "file"|"silence", "source": str, "duration_ms": int}
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
```

#### **Silence Generation**
```python
from pydub import AudioSegment

def generate_silence_segment(duration_ms: int, sample_rate: int = 22050) -> AudioSegment:
    """
    Generate a silence segment of specified duration
    
    Args:
        duration_ms: Duration in milliseconds
        sample_rate: Target sample rate (match other audio)
    
    Returns:
        AudioSegment containing silence
    """
    return AudioSegment.silent(duration=duration_ms, frame_rate=sample_rate)
```

#### **Enhanced Concatenation Logic**
```python
def concatenate_with_silence(parsed_items: List[Dict], output_path: Path, 
                           sample_rate: int = 22050) -> Dict:
    """
    Concatenate audio files and silence segments
    
    Args:
        parsed_items: Output from parse_concat_files()
        output_path: Where to save the result
        sample_rate: Target sample rate
    
    Returns:
        Metadata about the concatenation process
    """
    combined_audio = AudioSegment.empty()
    processing_info = []
    
    for item in parsed_items:
        if item["type"] == "silence":
            silence_segment = generate_silence_segment(item["duration_ms"], sample_rate)
            combined_audio += silence_segment
            processing_info.append({
                "type": "silence",
                "duration_ms": item["duration_ms"],
                "notation": item["source"]
            })
        else:
            # Load and process audio file
            audio_segment = AudioSegment.from_file(item["source"])
            # Ensure consistent sample rate
            if audio_segment.frame_rate != sample_rate:
                audio_segment = audio_segment.set_frame_rate(sample_rate)
            
            combined_audio += audio_segment
            processing_info.append({
                "type": "file",
                "filename": item["source"],
                "duration_ms": len(audio_segment)
            })
    
    # Export final audio
    combined_audio.export(output_path, format="wav")
    
    return {
        "total_duration_ms": len(combined_audio),
        "segments_processed": len(parsed_items),
        "silence_segments": sum(1 for item in parsed_items if item["type"] == "silence"),
        "audio_segments": sum(1 for item in parsed_items if item["type"] == "file"),
        "processing_details": processing_info
    }
```

### **API Model Updates**
```python
from pydantic import BaseModel, Field, validator
from typing import List

class ConcatRequest(BaseModel):
    files: List[str] = Field(
        ..., 
        description="Audio files and silence notations. Use '(duration[ms|s])' for silence: ['file1.wav', '(500ms)', 'file2.wav']",
        examples=[
            ["intro.wav", "main.wav", "outro.wav"],
            ["(1s)", "speech.wav", "(500ms)", "music.wav", "(2s)"]
        ]
    )
    
    @validator('files')
    def validate_files_array(cls, v):
        if not v:
            raise ValueError("Files array cannot be empty")
        
        # Validate silence notation
        silence_pattern = re.compile(r'^\((\d+(?:\.\d+)?)(ms|s)\)$')
        for item in v:
            if silence_pattern.match(item):
                # Validate silence duration
                duration_value = float(silence_pattern.match(item).group(1))
                unit = silence_pattern.match(item).group(2)
                duration_ms = duration_value * 1000 if unit == 's' else duration_value
                
                if not (50 <= duration_ms <= 10000):
                    raise ValueError(f"Silence duration must be between 50ms and 10s: {item}")
        
        return v
    
    # ... existing fields (export_formats, normalize_levels, etc.)
```

### **Use Cases & Examples**

#### **Video Production**
```bash
# Create narration with pauses for video overlay
curl -X POST http://localhost:7860/api/v1/concat \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      "(1.0s)",
      "intro_narration.wav",
      "(2.5s)",
      "main_content.wav", 
      "(1.0s)",
      "conclusion.wav",
      "(500ms)"
    ],
    "normalize_levels": true,
    "export_formats": ["wav", "mp3"]
  }'
```

#### **Podcast Production**
```bash
# Dramatic pause before reveal
curl -X POST http://localhost:7860/api/v1/concat \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      "setup.wav",
      "(1.2s)",
      "dramatic_reveal.wav",
      "(800ms)", 
      "reaction.wav"
    ]
  }'
```

---

## **Feature 2: Audio Trimming System** (Tasks 11.3 & 11.4)

### **Core Concept**
Automatically detect and remove extraneous silence from the beginning and end of audio files to ensure clean, professional concatenation and TTS output.

### **Implementation Strategy**

#### **Silence Detection Algorithm**
```python
import librosa
import numpy as np
from pathlib import Path

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
    # Load audio with librosa for precise analysis
    y, sr = librosa.load(audio_path, sr=None)
    
    # Convert dB threshold to amplitude
    silence_thresh_amplitude = librosa.db_to_amplitude(silence_thresh_db)
    
    # Find non-silent regions
    non_silent_intervals = librosa.effects.split(
        y, 
        top_db=-silence_thresh_db,
        frame_length=2048,
        hop_length=512
    )
    
    if len(non_silent_intervals) == 0:
        # Entire file is silence
        return (0, 0)
    
    # Calculate leading and trailing silence
    first_sound_sample = non_silent_intervals[0][0]
    last_sound_sample = non_silent_intervals[-1][1]
    
    # Convert samples to milliseconds
    leading_silence_ms = (first_sound_sample / sr) * 1000
    trailing_silence_ms = ((len(y) - last_sound_sample) / sr) * 1000
    
    # Only trim if silence exceeds threshold
    trim_start_ms = max(0, leading_silence_ms - threshold_ms) if leading_silence_ms > threshold_ms else 0
    trim_end_ms = max(0, trailing_silence_ms - threshold_ms) if trailing_silence_ms > threshold_ms else 0
    
    return (trim_start_ms, trim_end_ms)

def trim_audio_file(input_path: Path, output_path: Path, 
                   threshold_ms: int = 200) -> Dict:
    """
    Trim extraneous silence from audio file
    
    Returns:
        Metadata about the trimming operation
    """
    trim_start_ms, trim_end_ms = detect_silence_boundaries(input_path, threshold_ms)
    
    if trim_start_ms == 0 and trim_end_ms == 0:
        # No trimming needed, copy file
        shutil.copy2(input_path, output_path)
        return {
            "trimmed": False,
            "original_duration_ms": get_audio_duration_ms(input_path),
            "trimmed_duration_ms": get_audio_duration_ms(input_path),
            "leading_silence_removed_ms": 0,
            "trailing_silence_removed_ms": 0
        }
    
    # Load and trim audio
    audio = AudioSegment.from_file(input_path)
    
    # Apply trimming
    start_trim_samples = int(trim_start_ms)
    end_trim_samples = int(len(audio) - trim_end_ms)
    
    trimmed_audio = audio[start_trim_samples:end_trim_samples]
    
    # Export trimmed audio
    trimmed_audio.export(output_path, format="wav")
    
    return {
        "trimmed": True,
        "original_duration_ms": len(audio),
        "trimmed_duration_ms": len(trimmed_audio),
        "leading_silence_removed_ms": trim_start_ms,
        "trailing_silence_removed_ms": trim_end_ms
    }
```

### **Integration Points**

#### **Concat Pre-processing** (Task 11.3)
```python
def concatenate_with_trimming(files: List[str], trim: bool = False, 
                            trim_threshold_ms: int = 200, **kwargs) -> Dict:
    """
    Enhanced concatenation with optional pre-trimming
    """
    if not trim:
        # Use existing concatenation logic
        return concatenate_audio_files(files, **kwargs)
    
    # Pre-process files with trimming
    temp_dir = Path("temp") / f"trim_{int(time.time())}"
    temp_dir.mkdir(exist_ok=True)
    
    trimmed_files = []
    trim_metadata = []
    
    try:
        for file_path in files:
            trimmed_path = temp_dir / f"trimmed_{file_path.name}"
            trim_info = trim_audio_file(file_path, trimmed_path, trim_threshold_ms)
            trimmed_files.append(trimmed_path)
            trim_metadata.append({
                "original_file": str(file_path),
                "trim_info": trim_info
            })
        
        # Concatenate trimmed files
        result = concatenate_audio_files(trimmed_files, **kwargs)
        result["trim_metadata"] = trim_metadata
        result["pre_processing"] = "trim_applied"
        
        return result
        
    finally:
        # Cleanup temporary files
        shutil.rmtree(temp_dir, ignore_errors=True)
```

#### **TTS Post-processing** (Task 11.4)
```python
def generate_tts_with_trimming(text: str, trim: bool = False, 
                             trim_threshold_ms: int = 200, **kwargs) -> Dict:
    """
    Enhanced TTS generation with optional post-trimming
    """
    # Generate TTS using existing logic
    tts_result = generate_tts_base(text, **kwargs)
    
    if not trim:
        return tts_result
    
    # Apply trimming to generated audio
    original_path = Path(tts_result["output_path"])
    temp_trimmed_path = original_path.with_suffix(".trimmed.wav")
    
    try:
        trim_info = trim_audio_file(original_path, temp_trimmed_path, trim_threshold_ms)
        
        if trim_info["trimmed"]:
            # Replace original with trimmed version
            shutil.move(temp_trimmed_path, original_path)
            
            # Update result metadata
            tts_result["trim_applied"] = True
            tts_result["trim_info"] = trim_info
            tts_result["post_processing"] = "trim_applied"
        else:
            # No trimming needed
            tts_result["trim_applied"] = False
            tts_result["trim_info"] = trim_info
        
        return tts_result
        
    finally:
        # Cleanup temporary file if it exists
        if temp_trimmed_path.exists():
            temp_trimmed_path.unlink(missing_ok=True)
```

### **API Model Updates**

#### **Enhanced ConcatRequest**
```python
class ConcatRequest(BaseModel):
    # ... existing fields
    
    trim: bool = Field(
        default=False, 
        description="Remove extraneous silence from input files before concatenation"
    )
    trim_threshold_ms: int = Field(
        default=200, 
        ge=50, 
        le=1000,
        description="Minimum silence duration (ms) to consider for trimming"
    )
```

#### **Enhanced TTSRequest**
```python
class TTSRequest(BaseModel):
    # ... existing fields
    
    trim: bool = Field(
        default=False, 
        description="Remove extraneous silence from generated audio"
    )
    trim_threshold_ms: int = Field(
        default=200, 
        ge=50, 
        le=1000,
        description="Minimum silence duration (ms) to consider for trimming"
    )
```

### **Enhanced Filename Generation**
```python
def generate_enhanced_filename(generation_type: str, parameters: dict, 
                             export_format: str) -> str:
    """
    Updated to include silence and trim parameters
    """
    # ... existing logic
    
    if generation_type == "concat":
        # ... existing concat logic
        
        # Add trim parameters
        if parameters.get("trim", False):
            param_parts.append(f"trim{parameters.get('trim_threshold_ms', 200)}")
        
        # Add silence count if manual silences were used
        silence_count = parameters.get("silence_segments", 0)
        if silence_count > 0:
            param_parts.append(f"sil{silence_count}")
    
    elif generation_type == "tts":
        # ... existing TTS logic
        
        # Add trim parameters
        if parameters.get("trim", False):
            param_parts.append(f"trim{parameters.get('trim_threshold_ms', 200)}")
```

---

## **Testing Strategy**

### **Unit Tests**
- Silence notation parsing validation
- Silence generation accuracy
- Trimming algorithm effectiveness
- Edge case handling (very short files, all-silence files)

### **Integration Tests**
- Mixed file/silence concatenation workflows
- Trimming with various audio types and qualities
- Performance with large files and multiple operations
- Metadata accuracy and completeness

### **User Acceptance Tests**
- Video production workflows
- Podcast creation scenarios
- Professional audio editing use cases
- Backwards compatibility verification

---

## **Documentation Requirements**

### **API Documentation Updates**
- Enhanced curl examples showing silence notation
- Trimming parameter explanations and use cases
- Professional workflow examples (video, podcast, audio editing)
- Performance considerations and best practices

### **User Guides**
- Video production workflow guide
- Podcast creation best practices
- Audio editing automation examples
- Troubleshooting trimming issues

---

## **Performance Considerations**

### **Optimization Strategies**
- Cache trimmed audio files for repeated use
- Parallel processing for multiple file operations
- Memory-efficient handling of large audio files
- Progress tracking for long operations

### **Resource Management**
- Temporary file cleanup
- Memory usage monitoring
- Disk space management for trim operations
- Concurrent operation limits

---

## **Future Enhancements**

### **Advanced Features**
- Custom silence detection algorithms
- Adaptive trimming based on audio content type
- Batch trimming operations
- Audio quality analysis and recommendations

### **Integration Opportunities**
- Voice activity detection (VAD) integration
- Noise reduction during trimming
- Advanced audio analysis and metadata
- Machine learning-based silence detection

---

*This design document provides the foundation for implementing professional-grade silence insertion and audio trimming features in Phase 11 of the API refinement project.*
