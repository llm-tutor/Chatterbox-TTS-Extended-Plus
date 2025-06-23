# Advanced Features Guide

> **Chatterbox TTS Extended Plus** - Advanced capabilities and optimizations

## Overview

This guide covers advanced features that enhance the basic TTS and voice conversion capabilities, including speed control, batch processing, audio concatenation, and optimization techniques.

## Speed Factor Control

### Overview
Control playback speed of generated audio while preserving pitch and voice characteristics.

### Basic Usage
```bash
# Generate speech at 1.5x speed
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This will be spoken faster",
    "speed_factor": 1.5,
    "export_formats": ["wav"]
  }' \
  --output fast_speech.wav
```

### Speed Range
- **Minimum**: 0.5x (half speed)
- **Maximum**: 2.0x (double speed)  
- **Default**: 1.0x (normal speed)
- **Recommended**: 0.8x - 1.3x for natural-sounding results

### Programming Examples

**Python**:
```python
def generate_speech_with_speed(text, speed=1.0, voice=None):
    """Generate speech with custom speed"""
    
    payload = {
        "text": text,
        "speed_factor": speed,
        "export_formats": ["wav"]
    }
    
    if voice:
        payload["reference_audio_filename"] = voice
    
    response = requests.post(
        "http://localhost:7860/api/v1/tts",
        json=payload,
        stream=True
    )
    
    return response

# Usage examples
slow_speech = generate_speech_with_speed("Learn slowly", speed=0.8)
fast_speech = generate_speech_with_speed("Quick announcement", speed=1.3)
```

**Batch Speed Variations**:
```python
def create_speed_variants(text, voice=None):
    """Create multiple speed versions of the same text"""
    
    speeds = [0.8, 1.0, 1.2, 1.5]
    results = {}
    
    for speed in speeds:
        print(f"Generating at {speed}x speed...")
        response = generate_speech_with_speed(text, speed, voice)
        
        filename = f"speech_{speed}x.wav"
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        results[speed] = filename
    
    return results

# Create variants
variants = create_speed_variants(
    "The quick brown fox jumps over the lazy dog",
    voice="narrator.wav"
)
```
## Audio Concatenation

### Overview
Combine multiple audio files into a single output with level normalization and format conversion.

### Basic Concatenation
```bash
# Concatenate server files
curl -X POST http://localhost:7860/api/v1/concat \
  -H "Content-Type: application/json" \
  -d '{
    "segments": [
      {"type": "server_file", "filename": "intro.wav"},
      {"type": "server_file", "filename": "main_content.wav"},
      {"type": "server_file", "filename": "outro.wav"}
    ],
    "export_formats": ["wav", "mp3"]
  }' \
  --output combined_audio.wav
```

### Programming Examples

**Python - Server Files**:
```python
def concatenate_server_files(filenames, output_path="combined.wav"):
    """Concatenate files already on the server"""
    
    segments = [
        {"type": "server_file", "filename": f} 
        for f in filenames
    ]
    
    payload = {
        "segments": segments,
        "processing": {
            "normalize_levels": True,
            "crossfade_ms": 100
        },
        "export_formats": ["wav"]
    }
    
    response = requests.post(
        "http://localhost:7860/api/v1/concat",
        json=payload,
        stream=True
    )
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    else:
        print(f"Concatenation failed: {response.text}")
        return False
```
## Batch Processing

### Overview
Efficiently process multiple TTS requests with consistent voice and parameters.

### Batch TTS Generation
```python
def batch_tts_generation(text_list, voice=None, batch_params=None):
    """Generate multiple TTS files with consistent settings"""
    
    if batch_params is None:
        batch_params = {
            "temperature": 0.8,
            "speed_factor": 1.0,
            "export_formats": ["wav"]
        }
    
    results = []
    
    for i, text in enumerate(text_list):
        print(f"Processing {i+1}/{len(text_list)}: {text[:50]}...")
        
        payload = {"text": text, **batch_params}
        if voice:
            payload["reference_audio_filename"] = voice
        
        try:
            response = requests.post(
                "http://localhost:7860/api/v1/tts",
                json=payload,
                stream=True
            )
            
            if response.status_code == 200:
                filename = f"batch_{i+1:03d}.wav"
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                results.append({"index": i, "text": text, "filename": filename})
                print(f"✓ Saved as {filename}")
            else:
                print(f"✗ Failed: {response.text}")
                results.append({"index": i, "text": text, "error": response.text})
                
        except Exception as e:
            print(f"✗ Exception: {e}")
            results.append({"index": i, "text": text, "error": str(e)})
    
    return results

# Usage
texts = [
    "Welcome to chapter one",
    "This is the second chapter", 
    "Chapter three begins here",
    "Finally, the conclusion"
]

results = batch_tts_generation(
    texts,
    voice="narrator.wav",
    batch_params={"temperature": 0.7, "speed_factor": 1.1}
)

# Print summary
successful = sum(1 for r in results if "filename" in r)
print(f"Batch complete: {successful}/{len(texts)} successful")
```
## OpenAI Compatibility Mode

### Overview
Use OpenAI-compatible endpoints for easy integration with existing applications.

### Basic Usage
```bash
# OpenAI-style TTS request
curl -X POST http://localhost:7860/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "chatterbox-tts",
    "input": "Hello, this is a test",
    "voice": "speaker1.wav",
    "response_format": "wav",
    "speed": 1.2
  }' \
  --output speech.wav
```

### Parameter Mapping
| OpenAI Parameter | Chatterbox Equivalent | Notes |
|-----------------|---------------------|-------|
| `model` | Ignored | Single model system |
| `input` | `text` | Text to synthesize |
| `voice` | `reference_audio_filename` | Voice file name |
| `response_format` | `export_formats[0]` | Primary format |
| `speed` | `speed_factor` | Playback speed |

### Programming Integration
```python
# Drop-in replacement for OpenAI client
def openai_compatible_tts(text, voice="speaker1.wav", speed=1.0):
    """OpenAI-compatible TTS function"""
    
    payload = {
        "model": "chatterbox-tts",  # Ignored but required
        "input": text,
        "voice": voice,
        "response_format": "wav",
        "speed": speed
    }
    
    response = requests.post(
        "http://localhost:7860/v1/audio/speech",
        json=payload,
        stream=True
    )
    
    return response

# Usage
response = openai_compatible_tts("Hello world", voice="narrator.wav", speed=1.1)
```

## Performance Optimization

### 1. Model Warm-up
```python
def warm_up_models():
    """Pre-load models for faster subsequent requests"""
    
    # Make a quick TTS request to initialize models
    warmup_response = requests.post(
        "http://localhost:7860/api/v1/tts",
        json={"text": "warmup", "export_formats": ["wav"]},
        timeout=60
    )
    
    if warmup_response.status_code == 200:
        print("✓ TTS model warmed up")
    else:
        print("✗ TTS warmup failed")
    
    # Test VC model if needed
    # Similar approach for voice conversion
```

### 2. Concurrent Requests
```python
import concurrent.futures
import threading

class ConcurrentTTSProcessor:
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.session = requests.Session()
    
    def generate_single(self, text, voice=None, **kwargs):
        """Generate single TTS with session reuse"""
        
        payload = {"text": text, **kwargs}
        if voice:
            payload["reference_audio_filename"] = voice
        
        response = self.session.post(
            "http://localhost:7860/api/v1/tts",
            json=payload,
            stream=True
        )
        
        return response
    
    def batch_generate(self, text_voice_pairs):
        """Process multiple TTS requests concurrently"""
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all requests
            future_to_index = {
                executor.submit(
                    self.generate_single, 
                    pair["text"], 
                    pair.get("voice"),
                    **pair.get("params", {})
                ): i 
                for i, pair in enumerate(text_voice_pairs)
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    response = future.result()
                    results.append((index, response))
                except Exception as e:
                    results.append((index, e))
        
        # Sort by original order
        results.sort(key=lambda x: x[0])
        return [r[1] for r in results]

# Usage
processor = ConcurrentTTSProcessor(max_workers=2)

requests_data = [
    {"text": "First sentence", "voice": "speaker1.wav"},
    {"text": "Second sentence", "voice": "speaker1.wav"},
    {"text": "Third sentence", "voice": "speaker2.wav"}
]

responses = processor.batch_generate(requests_data)
```
### 3. Memory and Resource Management
```python
import gc
import psutil

def monitor_resource_usage():
    """Monitor memory and CPU usage during processing"""
    
    process = psutil.Process()
    
    print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
    print(f"CPU percent: {process.cpu_percent():.1f}%")
    
    # GPU memory (if available)
    try:
        import torch
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024 / 1024
            cached = torch.cuda.memory_reserved() / 1024 / 1024
            print(f"GPU memory: {allocated:.1f} MB allocated, {cached:.1f} MB cached")
    except ImportError:
        pass

def optimize_memory_usage():
    """Clean up memory between large batches"""
    
    # Force garbage collection
    gc.collect()
    
    # Clear GPU cache if available
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass

# Usage in batch processing
for i in range(0, len(large_text_list), batch_size):
    batch = large_text_list[i:i+batch_size]
    
    # Process batch
    process_batch(batch)
    
    # Clean up memory
    if i % (batch_size * 5) == 0:  # Every 5 batches
        optimize_memory_usage()
        monitor_resource_usage()
```

## Advanced Voice Conversion

### Chunk Size Optimization
```python
def optimize_vc_chunk_size(audio_duration_seconds):
    """Determine optimal chunk size based on audio length"""
    
    if audio_duration_seconds < 60:
        return 30  # Small chunks for short audio
    elif audio_duration_seconds < 300:
        return 60  # Standard chunks for medium audio
    else:
        return 90  # Larger chunks for long audio

def smart_voice_conversion(input_file, target_voice, output_file):
    """Voice conversion with optimized chunk size"""
    
    # Get audio duration (you'd implement this)
    duration = get_audio_duration(input_file)
    chunk_size = optimize_vc_chunk_size(duration)
    
    with open(input_file, 'rb') as f:
        files = {'input_audio': f}
        data = {
            'target_voice_source': target_voice,
            'chunk_sec': chunk_size,
            'overlap_sec': 0.1
        }
        
        response = requests.post(
            "http://localhost:7860/api/v1/vc",
            files=files,
            data=data,
            stream=True
        )
        
        if response.status_code == 200:
            with open(output_file, 'wb') as out_f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        out_f.write(chunk)
            return True
    
    return False
```

## Integration Patterns

### Webhook Notifications
```python
def tts_with_webhook(text, callback_url, **kwargs):
    """Generate TTS with completion webhook"""
    
    payload = {
        "text": text,
        "webhook_url": callback_url,
        **kwargs
    }
    
    # Start async generation
    response = requests.post(
        "http://localhost:7860/api/v1/tts/async",
        json=payload
    )
    
    if response.status_code == 202:
        result = response.json()
        return result["task_id"]
    else:
        raise Exception(f"Failed to start async TTS: {response.text}")

# Webhook handler (Flask example)
from flask import Flask, request

app = Flask(__name__)

@app.route('/tts-complete', methods=['POST'])
def handle_tts_completion():
    data = request.json
    
    task_id = data.get('task_id')
    success = data.get('success')
    output_url = data.get('output_url')
    
    if success:
        print(f"TTS {task_id} completed: {output_url}")
        # Download and process the file
    else:
        print(f"TTS {task_id} failed: {data.get('error')}")
    
    return "OK"
```

## See Also

- [Streaming Responses Guide](streaming-responses.md) - Efficient file handling
- [File Uploads Guide](file-uploads.md) - Upload optimization
- [Error Handling Guide](error-handling.md) - Robust error handling
- [TTS Endpoint](../endpoints/tts.md) - Complete TTS API reference
- [Voice Conversion Endpoint](../endpoints/voice-conversion.md) - VC API reference
