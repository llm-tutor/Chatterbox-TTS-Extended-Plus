# Configuration Reference

> **Chatterbox TTS Extended Plus** - Complete configuration guide and reference

## Overview

This document describes all configuration options available in the Chatterbox TTS system, including default values, validation rules, and best practices.

## Configuration File Structure

The main configuration is stored in `config.yaml` in the project root:

```yaml
# Server Configuration
server:
  host: "0.0.0.0"
  port: 7860
  debug: false
  reload: false

# Model Configuration  
models:
  tts_model_path: "models/tts"
  vc_model_path: "models/vc"
  whisper_model: "medium"
  device: "auto"  # auto, cpu, cuda

# Audio Processing
audio:
  sample_rate: 22050
  output_formats: ["wav", "mp3"]
  max_file_size_mb: 100

# API Limits
api:
  max_text_length: 10000
  max_concurrent_requests: 5
  rate_limit_per_minute: 60
  
# File Paths
paths:
  reference_audio_dir: "reference_audio"
  vc_input_dir: "vc_inputs"
  output_dir: "outputs"
  temp_dir: "temp"

# Speed Factor Configuration
speed_factor:
  default_speed_factor: 1.0
  min_speed_factor: 0.5
  max_speed_factor: 2.0
  preferred_library: "auto"
```
## Server Configuration

### Basic Server Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `server.host` | string | "0.0.0.0" | Server bind address |
| `server.port` | integer | 7860 | Server port |
| `server.debug` | boolean | false | Enable debug mode |
| `server.reload` | boolean | false | Enable auto-reload on code changes |

### Production vs Development

**Development Configuration**:
```yaml
server:
  host: "127.0.0.1"
  port: 7860
  debug: true
  reload: true
```

**Production Configuration**:
```yaml
server:
  host: "0.0.0.0" 
  port: 7860
  debug: false
  reload: false
```

## Model Configuration

### Model Paths and Loading

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `models.tts_model_path` | string | "models/tts" | TTS model directory |
| `models.vc_model_path` | string | "models/vc" | Voice conversion model directory |
| `models.whisper_model` | string | "medium" | Whisper model size |
| `models.device` | string | "auto" | Processing device |

### Device Selection

| Value | Description | Use Case |
|-------|-------------|----------|
| `"auto"` | Automatic GPU/CPU selection | Recommended |
| `"cpu"` | Force CPU processing | Low memory, compatibility |
| `"cuda"` | Force GPU processing | High performance |
| `"cuda:0"` | Specific GPU device | Multi-GPU systems |

### Whisper Model Options

| Model | Size | Speed | Accuracy | Memory |
|-------|------|-------|----------|---------|
| `"tiny"` | 39MB | Fastest | Lower | 1GB |
| `"base"` | 74MB | Fast | Good | 1GB |
| `"small"` | 244MB | Medium | Better | 2GB |
| `"medium"` | 769MB | Slower | High | 5GB |
| `"large"` | 1550MB | Slowest | Highest | 10GB |

## Audio Processing Configuration

### Core Audio Settings

| Setting | Type | Default | Range | Description |
|---------|------|---------|-------|-------------|
| `audio.sample_rate` | integer | 22050 | 8000-48000 | Audio sample rate in Hz |
| `audio.output_formats` | array | ["wav", "mp3"] | - | Default export formats |
| `audio.max_file_size_mb` | integer | 100 | 1-1000 | Maximum upload size |

### Format Configuration

**Supported Formats**:
```yaml
audio:
  supported_input_formats: ["wav", "mp3", "flac", "m4a", "ogg"]
  supported_output_formats: ["wav", "mp3", "flac"]
  default_output_format: "wav"
```

## API Limits and Security

### Request Limits

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `api.max_text_length` | integer | 10000 | Maximum text characters |
| `api.max_concurrent_requests` | integer | 5 | Concurrent request limit |
| `api.rate_limit_per_minute` | integer | 60 | Requests per minute per IP |
| `api.request_timeout_seconds` | integer | 300 | Request timeout |

### Security Settings

```yaml
api:
  cors_enabled: true
  cors_origins: ["*"]  # Restrict in production
  api_key_required: false
  allowed_file_extensions: [".wav", ".mp3", ".flac"]
  sanitize_filenames: true
```

## File Path Configuration

### Directory Structure

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `paths.reference_audio_dir` | string | "reference_audio" | Voice reference files |
| `paths.vc_input_dir` | string | "vc_inputs" | VC source audio files |
| `paths.output_dir` | string | "outputs" | Generated audio files |
| `paths.temp_dir` | string | "temp" | Temporary downloads |

### Path Resolution

**Relative Paths** (recommended):
```yaml
paths:
  reference_audio_dir: "reference_audio"
  vc_input_dir: "vc_inputs"
  output_dir: "outputs"
```

**Absolute Paths** (for custom locations):
```yaml
paths:
  reference_audio_dir: "/var/chatterbox/voices"
  vc_input_dir: "/var/chatterbox/inputs"
  output_dir: "/var/chatterbox/outputs"
```

## Speed Factor Configuration

### Default Settings

| Setting | Type | Default | Range | Description |
|---------|------|---------|-------|-------------|
| `speed_factor.default_speed_factor` | float | 1.0 | 0.5-2.0 | Default playback speed |
| `speed_factor.min_speed_factor` | float | 0.5 | 0.1-1.0 | Minimum allowed speed |
| `speed_factor.max_speed_factor` | float | 2.0 | 1.0-5.0 | Maximum allowed speed |
| `speed_factor.preferred_library` | string | "auto" | - | Speed processing library |

## Environment Variables

### Runtime Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `CHATTERBOX_CONFIG` | "config.yaml" | Configuration file path |
| `CHATTERBOX_HOST` | "0.0.0.0" | Override server host |
| `CHATTERBOX_PORT` | "7860" | Override server port |
| `CHATTERBOX_DEBUG` | "false" | Enable debug mode |

### Model Paths

| Variable | Description |
|----------|-------------|
| `TTS_MODEL_PATH` | Override TTS model path |
| `VC_MODEL_PATH` | Override VC model path |
| `WHISPER_MODEL` | Override Whisper model |

## Configuration Management

### Loading Configuration

```python
from config import config_manager

# Get configuration value
host = config_manager.get("server.host", "0.0.0.0")
port = config_manager.get("server.port", 7860)

# Get nested configuration
tts_defaults = config_manager.get("models.tts_defaults", {})
```

### Runtime Updates

```python
# Update configuration at runtime
config_manager.set("api.max_concurrent_requests", 10)

# Save configuration
config_manager.save_config()
```

## Best Practices

### Production Deployment

1. **Security Configuration**:
```yaml
api:
  cors_origins: ["https://yourdomain.com"]
  api_key_required: true
  rate_limit_per_minute: 30
```

2. **Performance Optimization**:
```yaml
models:
  device: "cuda"
api:
  max_concurrent_requests: 3
```

3. **Resource Management**:
```yaml
audio:
  max_file_size_mb: 50
api:
  request_timeout_seconds: 180
```

### Development Setup

```yaml
server:
  debug: true
  reload: true
models:
  device: "cpu"  # For development without GPU
api:
  max_concurrent_requests: 1
```

## See Also

- [File Structure Reference](file-structure.md) - Directory organization
- [Compatibility Reference](compatibility.md) - System requirements
- [Advanced Features Guide](../guides/advanced-features.md) - Feature configuration
- [Error Handling Guide](../guides/error-handling.md) - Error configuration
