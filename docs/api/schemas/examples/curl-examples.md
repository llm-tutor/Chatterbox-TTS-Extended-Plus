# cURL Examples
## Chatterbox TTS Extended Plus API

> **Two-Tier Testing Strategy**: Core examples for quick validation + Advanced examples for comprehensive testing
> **Base URL**: `http://localhost:7860`

---

# 🚀 **Core Examples (Implementation Validation)**

> **Purpose**: Quick validation during implementation phase closing  
> **Time**: 2-3 minutes maximum  
> **Requirements**: No specific voice file setup required  
> **Usage**: Routine development validation, CI/CD integration

These examples work universally on any setup and test essential functionality.

## Health & Status

### Basic Health Check
```bash
curl http://localhost:7860/api/v1/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-22T10:30:00Z",
  "uptime": "2h 15m 30s"
}
```

## Listing Operations

### List Available Voices
```bash
curl http://localhost:7860/api/v1/voices
```

### List Generated Files
```bash
curl http://localhost:7860/api/v1/outputs
```

## Basic Generation

### Basic TTS Generation (No Reference Voice)
```bash
curl -X POST http://localhost:7860/api/v1/tts \
-H "Content-Type: application/json" \
-d '{
  "text": "Hello, this is a basic TTS example for core validation.",
  "export_formats": ["wav"]
}'
```

### Basic Voice Conversion (Using Project Files)
```bash
curl -X POST http://localhost:7860/api/v1/vc \
-H "Content-Type: application/json" \
-d '{
  "input_audio_source": "test_inputs/chatterbox-hello_quick_brown.wav",
  "target_voice_source": "test_voices/linda_johnson_01.mp3",
  "export_formats": ["wav"]
}'
```

## Error Handling Validation

### Invalid Endpoint
```bash
curl http://localhost:7860/api/v1/nonexistent
```

**Expected Response:** `404 Not Found`

### Missing Required Parameter
```bash
curl -X POST http://localhost:7860/api/v1/tts \
-H "Content-Type: application/json" \
-d '{"export_formats": ["wav"]}'  # Missing required "text" parameter
```

**Expected Response:** `422 Validation Error`

---

# 🔧 **Advanced Examples (Developer Reference)**

> **Purpose**: Complete example validation for developers and releases  
> **Time**: 8-15 minutes (comprehensive validation)  
> **Requirements**: Specific voice files and setup required (see below)  
> **Usage**: Documentation releases, major API changes, developer onboarding

## 📋 **Required Voice Files for Advanced Examples**

Before running advanced examples, ensure these files exist:
- `reference_audio/test_voices/linda_johnson_01.mp3`
- `reference_audio/test_voices/linda_johnson_02.mp3`  
- `vc_inputs/test_inputs/chatterbox-hello_quick_brown.wav`
- `vc_inputs/test_inputs/chatterbox-in-a-village-of-la-mancha.mp3`

**Verify setup:**
```bash
curl http://localhost:7860/api/v1/voices | grep -E "(linda_johnson|test_voices)"
```

## Advanced Text-to-Speech (TTS)

### TTS with Voice Cloning
```bash
curl -X POST http://localhost:7860/api/v1/tts \
-H "Content-Type: application/json" \
-d '{
  "text": "This text will be spoken in the reference voice style.",
  "reference_audio_filename": "test_voices/linda_johnson_01.mp3",
  "exaggeration": 0.7,
  "temperature": 0.8,
  "export_formats": ["wav", "mp3"]
}'
```

### TTS with Speed Control (Enhanced)
```bash
# High-quality speed adjustment with audiostretchy
curl -X POST http://localhost:7860/api/v1/tts \
-H "Content-Type: application/json" \
-d '{
  "text": "This demonstrates high-quality speed adjustment with enhanced libraries.",
  "reference_audio_filename": "test_voices/linda_johnson_01.mp3",
  "speed_factor": 1.5,
  "speed_factor_library": "audiostretchy",
  "export_formats": ["wav"]
}'

# Auto library selection based on speed range
curl -X POST http://localhost:7860/api/v1/tts \
-H "Content-Type: application/json" \
-d '{
  "text": "Automatic library selection for optimal quality.",
  "speed_factor": 0.8,
  "speed_factor_library": "auto",
  "export_formats": ["wav"]
}'
```

### TTS Audio Trimming

```bash
# TTS with automatic silence trimming
curl -X POST http://localhost:7860/api/v1/tts \
-H "Content-Type: application/json" \
-d '{
  "text": "This demonstrates automatic silence trimming for professional audio production.",
  "reference_audio_filename": "test_voices/professional_narrator.wav",
  "trim": true,
  "trim_threshold_ms": 150,
  "export_formats": ["wav"]
}'

# TTS with custom trimming threshold
curl -X POST http://localhost:7860/api/v1/tts \
-H "Content-Type: application/json" \
-d '{
  "text": "Custom trimming threshold for sensitive content.",
  "trim": true,
  "trim_threshold_ms": 100,
  "export_formats": ["wav"]
}'
```

### TTS Advanced Parameters
```bash
curl -X POST http://localhost:7860/api/v1/tts \
-H "Content-Type: application/json" \
-d '{
  "text": "Advanced TTS generation with all parameters.",
  "reference_audio_filename": "test_voices/linda_johnson_02.mp3",
  "exaggeration": 0.6,
  "temperature": 0.75,
  "seed": 42,
  "cfg_weight": 1.2,
  "num_candidates_per_chunk": 3,
  "max_attempts_per_candidate": 3,
  "bypass_whisper_checking": false,
  "whisper_model_name": "medium",
  "use_faster_whisper": true,
  "enable_batching": false,
  "smart_batch_short_sentences": true,
  "to_lowercase": true,
  "normalize_spacing": true,
  "fix_dot_letters": true,
  "remove_reference_numbers": true,
  "export_formats": ["wav", "mp3"],
  "disable_watermark": true
}'
```

## Advanced Voice Conversion (VC)

### Voice Conversion with URLs (Demo - URL won't work)
```bash
curl -X POST http://localhost:7860/api/v1/vc \
-H "Content-Type: application/json" \
-d '{
  "input_audio_source": "test_inputs/chatterbox-in-a-village-of-la-mancha.mp3",
  "target_voice_source": "test_voices/linda_johnson_02.mp3",
  "export_formats": ["wav", "mp3"]
}'
```

### Voice Conversion with Direct File Upload (Example - requires existing file)
```bash
# Note: This example requires you to have an actual audio file in the current directory
curl -X POST http://localhost:7860/api/v1/vc \
-F "input_audio=@sample_audio.wav" \
-F "target_voice_source=test_voices/linda_johnson_01.mp3" \
-F "chunk_sec=30" \
-F "export_formats=wav,mp3" \
--output converted_voice.wav
```

### Advanced Voice Conversion
```bash
curl -X POST http://localhost:7860/api/v1/vc \
-H "Content-Type: application/json" \
-d '{
  "input_audio_source": "test_inputs/chatterbox-in-a-village-of-la-mancha.mp3",
  "target_voice_source": "test_voices/linda_johnson_01.mp3",
  "chunk_sec": 60,
  "overlap_sec": 0.1,
  "export_formats": ["wav", "mp3", "flac"],
  "disable_watermark": true
}'
```

## Advanced Response Handling

### TTS Direct Download (Default)
```bash
# Get TTS as direct WAV download
curl -X POST http://localhost:7860/api/v1/tts \
-H "Content-Type: application/json" \
-d '{"text": "Hello world", "export_formats": ["wav", "mp3"]}' \
--output speech.wav

# Get TTS as MP3 download
curl -X POST http://localhost:7860/api/v1/tts \
-H "Content-Type: application/json" \
-d '{"text": "Hello world", "export_formats": ["wav", "mp3"]}' \
--output speech.mp3
```

### Get JSON Response with URLs (Legacy Mode)
```bash
curl -X POST http://localhost:7860/api/v1/tts?response_mode=url \
-H "Content-Type: application/json" \
-d '{"text": "Hello world", "export_formats": ["wav"]}'
```

## Voice Management

### Upload New Voice
```bash
curl -X POST http://localhost:7860/api/v1/voice \
-F "voice_file=@my_voice.wav" \
-F "name=My Custom Voice" \
-F "description=A test voice for demonstrations" \
-F "tags=test,custom,demo" \
-F "folder_path=custom_voices"
```

### Search Voices
```bash
curl "http://localhost:7860/api/v1/voices?page=1&page_size=50&search=professional"
```

### Get Voice Details (Note: Endpoint may not be implemented)
```bash
curl http://localhost:7860/api/v1/voices/test_voices/linda_johnson_01.mp3
```

## Advanced File Operations

### Download Generated File (Example - requires actual generated file)
```bash
# Note: Replace with actual generated filename from outputs
curl http://localhost:7860/outputs/tts_output_example.wav --output downloaded_file.wav
```

### Get File Metadata (Example - requires actual generated file)
```bash
# Note: Replace with actual generated filename from outputs
curl http://localhost:7860/api/v1/outputs/tts_output_example.wav/metadata
```

## Advanced Error Testing

### Invalid Parameters
```bash
curl -X POST http://localhost:7860/api/v1/tts \
-H "Content-Type: application/json" \
-d '{"temperature": 2.0}'  # Invalid: missing text, temperature > 1.0
```

**Response:**
```json
{
  "success": false,
  "error": "Validation error: temperature must be between 0.0 and 1.0",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-06-22T10:30:00Z"
}
```

### Missing Reference File
```bash
curl -X POST http://localhost:7860/api/v1/tts \
-H "Content-Type: application/json" \
-d '{
  "text": "Test speech",
  "reference_audio_filename": "nonexistent.wav"
}'
```

**Response:**
```json
{
  "success": false,
  "error": "Audio file not found: nonexistent.wav in reference_audio",
  "error_code": "RESOURCE_NOT_FOUND",
  "timestamp": "2025-06-22T10:30:00Z"
}
```

---

# 🛠️ **Testing & Debugging Tools**

## Development Helpers

### Verbose Output
```bash
# Add verbose flag to see detailed request/response info
curl -v -X POST http://localhost:7860/api/v1/tts \
-H "Content-Type: application/json" \
-d '{"text": "Debug test"}'
```

### Save Response Headers
```bash
# Save headers to file for debugging
curl -D headers.txt -X POST http://localhost:7860/api/v1/tts \
-H "Content-Type: application/json" \
-d '{"text": "Header test"}' \
--output response.wav
```

### Timing Requests
```bash
# Time the request duration
time curl -X POST http://localhost:7860/api/v1/tts \
-H "Content-Type: application/json" \
-d '{"text": "Performance test"}' \
--output timed_response.wav
```

## Automation Helpers

### Setting Base URL Variable
```bash
# Set base URL for easier testing
export API_BASE="http://localhost:7860"

# Use in requests
curl $API_BASE/api/v1/health
curl -X POST $API_BASE/api/v1/tts -H "Content-Type: application/json" -d '{"text": "Test"}'
```

### Pretty JSON Output
```bash
# Format JSON responses for readability
curl http://localhost:7860/api/v1/voices | python -m json.tool

# Or with jq if installed
curl http://localhost:7860/api/v1/voices | jq '.'
```

### Audio Concatenation
> **Note**: Concatenation requires existing files in the `outputs/` directory. 
> The examples below show the complete workflow including file discovery.

```bash
# First, list available output files to find files to concatenate
curl http://localhost:7860/api/v1/outputs?generation_type=tts&page_size=5

# Basic concatenation using files from outputs (replace with actual filenames from above)
# Example using hypothetical filenames from the outputs list:
curl -X POST http://localhost:7860/api/v1/concat \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["tts_2025-06-24_141456_306396_temp0.75.wav", "tts_2025-06-24_134725_685369_temp0.75.wav"],
    "export_formats": ["wav", "mp3"]
  }' \
  --output concatenated_audio.wav

# Concatenation with custom settings
curl -X POST http://localhost:7860/api/v1/concat \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["first_segment.wav", "second_segment.wav", "third_segment.wav"],
    "export_formats": ["wav"],
    "normalize_levels": true,
    "pause_duration_ms": 800,
    "pause_variation_ms": 200,
    "crossfade_ms": 100
  }' \
  --output full_presentation.wav

# Get URL response instead of direct download (safer for testing)
curl -X POST "http://localhost:7860/api/v1/concat?response_mode=url" \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["segment_a.wav", "segment_b.wav"],
    "export_formats": ["wav", "mp3"],
    "normalize_levels": true
  }'

# Complete workflow: Generate TTS files, then concatenate them
# Step 1: Generate first segment
curl -X POST "http://localhost:7860/api/v1/tts?response_mode=url" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Welcome to our presentation.",
    "export_formats": ["wav"]
  }'

# Step 2: Generate second segment  
curl -X POST "http://localhost:7860/api/v1/tts?response_mode=url" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This concludes our demonstration.",
    "export_formats": ["wav"]
  }'

# Step 3: List outputs to get the generated filenames
curl http://localhost:7860/api/v1/outputs?generation_type=tts&page_size=2

# Step 4: Concatenate using the actual generated filenames
# (Replace the filenames below with those returned from Step 3)
curl -X POST "http://localhost:7860/api/v1/concat?response_mode=url" \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["tts_YYYY-MM-DD_HHMMSS_microseconds_temp0.75.wav", "tts_YYYY-MM-DD_HHMMSS_microseconds_temp0.75.wav"],
    "export_formats": ["wav"],
    "normalize_levels": true,
    "pause_duration_ms": 600,
    "pause_variation_ms": 150
  }'
```

### Audio Concatenation with Trimming (Phase 11.3)

```bash
# Concatenation with audio trimming enabled
curl -X POST "http://localhost:7860/api/v1/concat?response_mode=url" \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["recorded_intro.wav", "recorded_main.wav", "recorded_outro.wav"],
    "trim": true,
    "trim_threshold_ms": 200,
    "export_formats": ["wav"],
    "normalize_levels": true
  }'

# Professional video production with trimming and silence insertion
curl -X POST "http://localhost:7860/api/v1/concat?response_mode=url" \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      "(1s)",
      "narration_intro.wav",
      "(2.5s)",
      "narration_main.wav",
      "(1.5s)",
      "narration_conclusion.wav",
      "(500ms)"
    ],
    "trim": true,
    "trim_threshold_ms": 150,
    "normalize_levels": true,
    "export_formats": ["wav"]
  }'

# Podcast production with trimming and crossfade
curl -X POST http://localhost:7860/api/v1/concat \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["segment1.wav", "segment2.wav", "segment3.wav"],
    "trim": true,
    "trim_threshold_ms": 100,
    "crossfade_ms": 300,
    "normalize_levels": true,
    "export_formats": ["mp3"]
  }' \
  --output trimmed_podcast.mp3
```

### Batch Testing
```bash
# Test multiple endpoints quickly
for endpoint in health voices outputs; do
  echo "Testing $endpoint..."
  curl -s http://localhost:7860/api/v1/$endpoint | head -c 100
  echo
done
```

---

# 📚 **Usage Guidelines**

## When to Use Core Examples
- **Implementation phase closing**: Quick validation before moving to next phase
- **CI/CD pipeline**: Automated validation in deployment pipeline  
- **Development setup**: Verify basic functionality after setup
- **Troubleshooting**: Quick smoke test to identify obvious issues

## When to Use Advanced Examples
- **Documentation releases**: Ensure all examples work correctly
- **Major API changes**: Comprehensive validation of new features
- **Developer onboarding**: Complete API functionality demonstration
- **Integration testing**: Full end-to-end workflow validation

## Setup Validation Commands
```bash
# Verify core setup (should always work)
curl http://localhost:7860/api/v1/health

# Verify advanced setup (requires voice files)
curl http://localhost:7860/api/v1/voices | grep -E "(linda_johnson|test_voices)"
```
