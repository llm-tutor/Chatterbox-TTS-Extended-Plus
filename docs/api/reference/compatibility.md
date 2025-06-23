# Compatibility Reference

> **Chatterbox TTS Extended Plus** - System requirements and compatibility information

## Overview

This document outlines system requirements, platform compatibility, and integration guidelines for the Chatterbox TTS Extended Plus API.

## System Requirements

### Minimum Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **OS** | Windows 10+, Ubuntu 18.04+, macOS 10.15+ | 64-bit required |
| **Python** | 3.8+ | 3.11+ recommended |
| **RAM** | 8GB | 16GB+ recommended for GPU |
| **Storage** | 10GB free space | 20GB+ recommended |
| **CPU** | 4+ cores | Intel/AMD x64 architecture |

### Recommended Requirements

| Component | Recommendation | Benefits |
|-----------|----------------|----------|
| **OS** | Ubuntu 22.04 LTS, Windows 11 | Best compatibility |
| **Python** | 3.11.x | Optimal performance |
| **RAM** | 16GB+ | Better concurrent processing |
| **Storage** | SSD with 50GB+ | Faster model loading |
| **GPU** | NVIDIA RTX 3060+ with 8GB VRAM | Hardware acceleration |

## Platform Support

### Operating Systems

**Fully Supported**:
- **Windows**: 10, 11 (x64)
- **Linux**: Ubuntu 18.04+, Debian 10+, CentOS 8+, RHEL 8+
- **macOS**: 10.15+ (Intel), 11.0+ (Apple Silicon)

**Limited Support**:
- **Windows**: Server 2019+ (enterprise use)
- **Linux**: Alpine, Arch (community support)
- **Docker**: Official containers available

### Python Versions

| Version | Status | Notes |
|---------|--------|-------|
| 3.8.x | Supported | Minimum version |
| 3.9.x | Supported | Stable |
| 3.10.x | Supported | Recommended |
| 3.11.x | Supported | Best performance |
| 3.12.x | Experimental | May have issues |
### Hardware Acceleration

**NVIDIA GPU Support**:
```yaml
Requirements:
  - CUDA 11.8+ or 12.0+
  - NVIDIA drivers 520+
  - VRAM: 6GB minimum, 8GB+ recommended
  
Supported Cards:
  - RTX 30 series: 3060, 3070, 3080, 3090
  - RTX 40 series: 4060, 4070, 4080, 4090
  - Professional: A4000, A5000, A6000
```

**CPU-Only Mode**:
- All processing falls back to CPU
- Slower but works on any system
- No special hardware requirements
- Memory usage: 4-8GB typical

## Dependencies

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.100+ | Web framework |
| `uvicorn` | 0.22+ | ASGI server |
| `torch` | 2.0+ | Deep learning framework |
| `torchaudio` | 2.0+ | Audio processing |
| `librosa` | 0.10+ | Audio analysis |
| `pydantic` | 2.0+ | Data validation |

### Audio Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `soundfile` | 0.12+ | Audio I/O |
| `pydub` | 0.25+ | Audio manipulation |
| `whisper` | 1.1+ | Speech recognition |
| `audiostretchy` | 1.3+ | Speed adjustment |

### Optional Dependencies

| Package | Version | Purpose | Fallback |
|---------|---------|---------|----------|
| `faster-whisper` | 0.9+ | Faster inference | `whisper` |
| `onnxruntime` | 1.15+ | ONNX models | PyTorch |
| `ffmpeg` | 4.4+ | Format conversion | `pydub` |

## API Compatibility

### HTTP Standards

**Supported HTTP Features**:
- HTTP/1.1 and HTTP/2
- Chunked transfer encoding
- Gzip compression
- CORS headers

**Request Formats**:
- `application/json` (primary)
- `multipart/form-data` (file uploads)

**Response Formats**:
- `application/json` (default)
- `audio/wav`, `audio/mpeg`, `audio/flac` (streaming)

### Client Compatibility

**Tested Clients**:
- `curl` 7.68+
- `requests` (Python) 2.28+
- `fetch` API (JavaScript)
- `axios` (JavaScript) 1.4+
- Postman 10.0+

**Browser Support**:
- Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

## Integration Compatibility

### OpenAI API Compatibility

**Compatible Endpoints**:
```python
# OpenAI-style requests work directly
POST /v1/audio/speech
{
  "model": "chatterbox-tts",
  "input": "Hello world",
  "voice": "speaker1.wav"
}
```

**Parameter Mapping**:
| OpenAI | Chatterbox | Notes |
|--------|------------|-------|
| `model` | Ignored | Single model system |
| `input` | `text` | Direct mapping |
| `voice` | `reference_audio_filename` | Voice file name |
| `speed` | `speed_factor` | 1:1 mapping |

### Framework Integration

**FastAPI/Starlette**:
- Native integration, middleware compatible

**Django/Flask**:
- HTTP client integration, async view support

**Express.js/Node.js**:
- HTTP client integration, Promise/async compatible

## Docker Compatibility

### Official Images

```dockerfile
# CPU-only image
FROM chatterbox/tts:latest-cpu

# GPU-enabled image  
FROM chatterbox/tts:latest-gpu
```

### Docker Requirements

| Requirement | CPU Image | GPU Image |
|-------------|-----------|-----------|
| Docker | 20.10+ | 20.10+ |
| RAM | 8GB | 16GB |
| Storage | 10GB | 15GB |
| GPU Support | - | NVIDIA Container Toolkit |

## Cloud Platform Support

### AWS
- EC2 instances (g4dn, p3, p4 families)
- ECS/Fargate containers
- Lambda (CPU-only, limited)

### Google Cloud
- Compute Engine (N1, N2 with GPUs)
- Cloud Run (CPU-only)
- GKE clusters

### Azure
- Virtual Machines (NCv3, NDv2 series)
- Container Instances
- AKS clusters

## Performance Benchmarks

### TTS Generation Speed

| Configuration | Text Length | Generation Time | Real-time Factor |
|---------------|-------------|-----------------|------------------|
| RTX 4090 | 100 chars | 0.8s | 15x |
| RTX 3080 | 100 chars | 1.2s | 10x |
| CPU (i7-12700K) | 100 chars | 4.5s | 2.5x |
| CPU (i5-10400) | 100 chars | 8.2s | 1.4x |

### Voice Conversion Speed

| Configuration | Audio Length | Processing Time | Real-time Factor |
|---------------|--------------|-----------------|------------------|
| RTX 4090 | 60s | 12s | 5x |
| RTX 3080 | 60s | 18s | 3.3x |
| CPU (i7-12700K) | 60s | 180s | 0.33x |

## Known Limitations

### Current Limitations
- Single concurrent GPU user
- Model switching requires restart
- Maximum 100MB file uploads
- No real-time streaming (yet)

### Platform-Specific Issues

**Windows**:
- Antivirus may flag model files
- Long path names may cause issues
- PowerShell encoding considerations

**macOS**:
- Apple Silicon requires Rosetta for some dependencies
- Microphone permissions for audio processing
- Gatekeeper warnings for unsigned binaries

**Linux**:
- ALSA/PulseAudio configuration for audio
- CUDA driver installation complexity
- SELinux policies may block operations

## Troubleshooting

### Common Installation Issues

**CUDA Not Found**:
```bash
# Check CUDA installation
nvidia-smi
nvcc --version

# Install CUDA toolkit if missing
# Follow NVIDIA installation guide
```

**Python Version Issues**:
```bash
# Check Python version
python --version

# Use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

**Memory Issues**:
```yaml
# Reduce memory usage in config.yaml
api:
  max_concurrent_requests: 1
models:
  device: "cpu"  # Switch to CPU if GPU memory insufficient
```

## See Also

- [Configuration Reference](configuration.md) - System configuration
- [File Structure Reference](file-structure.md) - File organization
- [Quick Start Guide](../quick-start.md) - Installation guide
- [Advanced Features Guide](../guides/advanced-features.md) - Performance optimization
