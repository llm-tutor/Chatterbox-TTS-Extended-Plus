# Text-to-Speech (TTS) Endpoint

Generate speech from text using advanced TTS with optional voice cloning and streaming response.

## Endpoint

**POST** `/api/v1/tts`

Convert text to speech with extensive customization options including voice cloning, quality validation, and output format control.

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `response_mode` | string | `"stream"` | Response mode: `"stream"` for direct file download, `"url"` for JSON response |
| `return_format` | string | first from export_formats | Format to stream: `"wav"`, `"mp3"`, `"flac"` |

## Request Body Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | string | Text to synthesize (max 10,000 characters) |

### Core Audio Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `reference_audio_filename` | string | null | Voice reference file from `reference_audio/` directory |
| `export_formats` | array | `["wav","mp3"]` | Output formats: `"wav"`, `"mp3"`, `"flac"` |
| `project` | string | null | Project folder path for organizing generated files within `outputs/` directory |
| `folder` | string | null | Alias for `project` parameter - folder path for organizing generated files |

### Voice Generation Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `exaggeration` | float | 0.5 | 0.0-1.0 | Voice expressiveness and emotion intensity |
| `temperature` | float | 0.75 | 0.0-2.0 | Generation randomness (lower = more consistent) |
| `seed` | integer | 0 | 0+ | Random seed for reproducible results (0 = random) |
| `cfg_weight` | float | 1.0 | 0.0-3.0 | Classifier-free guidance weight |

### Advanced Processing Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num_candidates_per_chunk` | integer | 3 | Number of generation candidates per text chunk |
| `max_attempts_per_candidate` | integer | 3 | Maximum retry attempts for failed generations |
| `bypass_whisper_checking` | boolean | false | Skip Whisper quality validation |
| `whisper_model_name` | string | `"medium"` | Whisper model size: `"tiny"`, `"base"`, `"small"`, `"medium"`, `"large"` |
| `use_faster_whisper` | boolean | true | Use faster-whisper backend for validation |
| `disable_watermark` | boolean | true | Disable audio watermarking |

### Text Processing Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_batching` | boolean | false | Enable text chunking and batching |
| `smart_batch_short_sentences` | boolean | true | Intelligently group short sentences |
| `to_lowercase` | boolean | true | Convert text to lowercase |
| `normalize_spacing` | boolean | true | Normalize whitespace and spacing |
| `fix_dot_letters` | boolean | true | Fix letter.dot.sequences (e.g., "U.S.A.") |
| `remove_reference_numbers` | boolean | true | Remove reference patterns like [1], (2) |

### Speed Control Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `speed_factor` | float | 1.0 | 0.5-2.0 | Playback speed multiplier |
| `speed_factor_library` | string | `"auto"` | - | Speed processing library: `"auto"`, `"audiostretchy"`, `"librosa"`, `"torchaudio"` |

#### Speed Factor Libraries

- **`auto`**: Smart selection with audiostretchy preferred for speech quality (recommended)
- **`audiostretchy`**: TDHS algorithm, superior speech quality with formant preservation
- **`librosa`**: Good baseline compatibility with adequate quality
- **`torchaudio`**: Basic fallback (affects pitch, use only when others unavailable)

### Audio Trimming Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `trim` | boolean | false | - | Apply silence trimming to generated audio |
| `trim_threshold_ms` | integer | 200 | 50-1000 | Silence threshold for trimming in milliseconds |

#### Audio Trimming Process

1. **Silence Detection**: Uses librosa to analyze audio for silence regions at beginning and end
2. **Threshold Analysis**: Detects silence below specified threshold in dB
3. **Conservative Approach**: Leaves a small buffer to avoid cutting into audio content
4. **Smart Processing**: Skips files that don't have significant silence

**Use Cases:**
- Remove unwanted silence from TTS generation artifacts
- Create consistent timing for audio concatenation
- Professional audio production workflows

## Request Examples

### Basic TTS

```json
{
  "text": "Hello, this is a basic TTS example.",
  "export_formats": ["wav"]
}
```

### Voice Cloning with Custom Parameters

```json
{
  "text": "This text will be spoken in the reference voice style.",
  "reference_audio_filename": "test_voices/linda_johnson_01.mp3",
  "exaggeration": 0.7,
  "temperature": 0.8,
  "seed": 42,
  "export_formats": ["wav", "mp3"]
}
```

### High-Quality Speed Control

```json
{
  "text": "This demonstrates high-quality speed adjustment with enhanced libraries.",
  "reference_audio_filename": "test_voices/linda_johnson_01.mp3",
  "speed_factor": 1.5,
  "speed_factor_library": "audiostretchy",
  "export_formats": ["wav"]
}
```

### Audio Trimming for Clean Output

```json
{
  "text": "This demonstrates automatic silence trimming for professional audio production.",
  "reference_audio_filename": "test_voices/professional_narrator.wav",
  "trim": true,
  "trim_threshold_ms": 150,
  "export_formats": ["wav"]
}
```

## Response Formats

### Streaming Response (default)

When `response_mode="stream"` (default), the API returns the audio file directly:

```
HTTP/1.1 200 OK
Content-Type: audio/wav
Content-Disposition: attachment; filename="tts_2025-06-22_143022_456_temp0.75_seed42.wav"
X-Alternative-Formats: mp3:/outputs/tts_2025-06-22_143022_456_temp0.75_seed42.mp3

[Binary audio data]
```

**Response Headers:**
- `Content-Type`: MIME type of the streamed audio format
- `Content-Disposition`: Contains the generated filename
- `X-Alternative-Formats`: Pipe-separated list of alternative format URLs in format `format:url`

**Project Folder Support:**
When using the `project` parameter, generated files are organized in subfolders within `outputs/`, and URLs reflect the folder structure:
```
X-Alternative-Formats: mp3:/outputs/my_project/tts_2025-06-22_143022_456_temp0.75_seed42.mp3
```

### JSON Response

When `response_mode="url"`, the API returns JSON with file information:

```json
{
  "success": true,
  "output_files": [
    {
      "format": "wav",
      "filename": "tts_2025-06-22_143022_456_temp0.75_seed42.wav",
      "url": "/outputs/tts_2025-06-22_143022_456_temp0.75_seed42.wav",
      "path": "/path/to/outputs/tts_2025-06-22_143022_456_temp0.75_seed42.wav"
    },
    {
      "format": "mp3", 
      "filename": "tts_2025-06-22_143022_456_temp0.75_seed42.mp3",
      "url": "/outputs/tts_2025-06-22_143022_456_temp0.75_seed42.mp3",
      "path": "/path/to/outputs/tts_2025-06-22_143022_456_temp0.75_seed42.mp3"
    }
  ],
  "generation_seed_used": 42,
  "processing_time_seconds": 5.2,
  "message": "TTS generation completed successfully",
  "timestamp": "2025-06-22T14:30:22Z"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Operation success status |
| `output_files` | array | Generated audio file information |
| `generation_seed_used` | integer | Actual seed used for generation |
| `processing_time_seconds` | float | Total processing time |
| `message` | string | Success message |
| `timestamp` | string | ISO 8601 response timestamp |

#### Output File Object

| Field | Type | Description |
|-------|------|-------------|
| `format` | string | Audio format (wav, mp3, flac) |
| `filename` | string | Generated filename with parameters |
| `url` | string | Download URL path |
| `path` | string | Full file system path |

## Usage Examples

### cURL Examples

#### Basic TTS with Streaming Response

```bash
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test of the TTS API.",
    "export_formats": ["wav"]
  }' \
  --output generated_speech.wav
```

#### Voice Cloning with JSON Response

```bash
curl -X POST http://localhost:7860/api/v1/tts?response_mode=url \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This will sound like the reference speaker.",
    "reference_audio_filename": "test_voices/linda_johnson_02.mp3",
    "temperature": 0.8,
    "exaggeration": 0.6,
    "export_formats": ["wav", "mp3"]
  }'
```

#### Project Organization Example

```bash
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This will be saved in the specified project folder.",
    "project": "my_audiobook/chapter_01",
    "reference_audio_filename": "narrator_voice.wav",
    "export_formats": ["wav", "mp3"]
  }' \
  --output chapter01_part1.wav
```

**Note:** Files are saved to `outputs/my_audiobook/chapter_01/` and alternative formats are available at URLs like `/outputs/my_audiobook/chapter_01/filename.mp3`.

#### Speed Control Example

```bash
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This speech will be faster than normal.",
    "speed_factor": 1.3,
    "speed_factor_library": "audiostretchy",
    "export_formats": ["wav"]
  }' \
  --output fast_speech.wav
```

### Python Examples

#### Basic TTS Function

```python
import requests

def generate_tts(text, voice_file=None, formats=["wav", "mp3"]):
    payload = {
        "text": text,
        "export_formats": formats
    }
    if voice_file:
        payload["reference_audio_filename"] = voice_file
    
    # Get JSON response
    response = requests.post(
        "http://localhost:7860/api/v1/tts?response_mode=url",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Generated {len(result['output_files'])} files:")
        for file_info in result['output_files']:
            print(f"  {file_info['format']}: {file_info['url']}")
        return result
    else:
        print(f"Error {response.status_code}: {response.text}")

# Usage
generate_tts("Hello world!")
generate_tts("Custom voice test", "my_voice.wav")
```

#### Direct File Download

```python
import requests

def download_tts(text, filename, voice_file=None):
    payload = {
        "text": text,
        "export_formats": ["wav"]
    }
    if voice_file:
        payload["reference_audio_filename"] = voice_file
    
    # Stream response (default behavior)
    response = requests.post(
        "http://localhost:7860/api/v1/tts",
        json=payload,
        headers={"Content-Type": "application/json"},
        stream=True
    )
    
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {filename}")
    else:
        print(f"Error {response.status_code}: {response.text}")

# Usage
download_tts("Hello world!", "output.wav", "speaker1.wav")
```

### JavaScript Examples

#### Browser/Node.js Client

```javascript
async function generateTTS(text, options = {}) {
    const payload = {
        text: text,
        export_formats: options.formats || ["wav", "mp3"],
        ...options
    };
    
    const url = options.responseMode === 'url' 
        ? 'http://localhost:7860/api/v1/tts?response_mode=url'
        : 'http://localhost:7860/api/v1/tts';
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        if (options.responseMode === 'url') {
            const data = await response.json();
            console.log('Generated files:', data.output_files);
            return data;
        } else {
            // Handle binary response
            const blob = await response.blob();
            const downloadUrl = URL.createObjectURL(blob);
            console.log('Download URL created:', downloadUrl);
            return downloadUrl;
        }
    } catch (error) {
        console.error('TTS generation failed:', error);
    }
}

// Usage examples
generateTTS("Hello world!", { responseMode: 'url' });
generateTTS("Custom voice", { 
    reference_audio_filename: "speaker1.wav",
    temperature: 0.8,
    responseMode: 'url'
});
```

## Quality Validation

When `bypass_whisper_checking` is `false` (default), the API performs quality validation:

1. **Generate multiple candidates** for each text chunk
2. **Transcribe each candidate** using Whisper
3. **Compare transcription** to original text 
4. **Select best candidates** (similarity ≥ 95%)
5. **Retry failed chunks** up to max attempts
6. **Fall back gracefully** for persistent failures

This ensures high-quality output but increases processing time.

## Error Handling

### Common Error Responses

```json
{
  "success": false,
  "error": "Text is required",
  "detail": "The 'text' field cannot be empty",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-06-22T14:30:22Z"
}
```

### Common Error Types

| Error Code | HTTP Status | Description | Solution |
|------------|-------------|-------------|----------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters | Check parameter types and values |
| `FILE_NOT_FOUND` | 404 | Reference audio file not found | Verify file exists in `reference_audio/` |
| `TEXT_TOO_LONG` | 400 | Text exceeds maximum length | Split text into smaller chunks |
| `GENERATION_FAILED` | 500 | TTS generation failed | Try different parameters or retry |
| `PROCESSING_ERROR` | 500 | Internal processing error | Check logs and retry |

## Performance Tips

### Optimization Strategies

1. **Use appropriate chunk size**: Enable batching for long texts
2. **Choose optimal parameters**: Lower temperature for consistency, higher for variety
3. **Select efficient formats**: WAV for quality, MP3 for size
4. **Leverage caching**: Use same seed for reproducible results
5. **Bypass validation**: Set `bypass_whisper_checking: true` for faster processing

### Expected Processing Times

| Text Length | Processing Time | Notes |
|-------------|----------------|-------|
| 1-2 sentences | 2-5 seconds | Basic generation |
| 1 paragraph | 5-15 seconds | With quality validation |
| Long text (batched) | 30-60 seconds | Depends on chunk count |
| With voice cloning | +20-50% | Additional processing |

## File Organization

### Reference Audio Files

Place reference voice files in the `reference_audio/` directory:

```
reference_audio/
├── speaker1.wav
├── speaker2.wav
├── voices/
│   ├── formal.wav
│   └── casual.wav
└── characters/
    ├── protagonist.wav
    └── narrator.wav
```

### Generated Files

TTS output files are saved to the `outputs/` directory with descriptive names:

```
outputs/
├── tts_2025-06-22_143022_456_temp0.75_seed42.wav
├── tts_2025-06-22_143022_456_temp0.75_seed42.mp3
└── tts_2025-06-22_143100_789_speed1.5.wav
```

## Related Endpoints

- **[Voice Management](voice-management.md)** - Upload and manage reference voices
- **[File Operations](file-operations.md)** - List and download generated files
- **[Health Check](health.md)** - Verify API status

## Advanced Features

- **[Streaming Responses](../guides/streaming-responses.md)** - Direct file downloads
- **[Speed Control](../guides/advanced-features.md#speed-control)** - Detailed speed adjustment
- **[Quality Validation](../guides/advanced-features.md#quality-validation)** - Whisper checking

---

*Need help? Check the [Quick Start Guide](../quick-start.md) or [Error Handling Guide](../guides/error-handling.md)*
