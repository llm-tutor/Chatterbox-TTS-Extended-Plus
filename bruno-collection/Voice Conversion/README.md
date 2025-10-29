# Voice Conversion Endpoint - Bruno Requests

This folder contains comprehensive Bruno request files for testing all variants of the Voice Conversion (VC) endpoint.

## Overview

The Voice Conversion endpoint transforms voice characteristics in audio files, applying a target voice's characteristics to an input audio file while preserving the original content and timing.

**Endpoint**: `POST /api/v1/vc`

## Request Files in This Folder

### JSON Request Method (Files on Server)

**1. VC - JSON Request - Stream Response.bru**
- **Input Method**: JSON body with file paths
- **Response**: Binary audio file streamed directly
- **Use Case**: Quick conversion of server-side files
- **Best For**: Testing, CLI scripts, server-to-server

**2. VC - JSON Request - Stream with Format Selection.bru**
- **Input Method**: JSON body with file paths
- **Response**: Stream specific format from multiple generated
- **Features**: Generate WAV, MP3, FLAC; stream preferred format
- **Best For**: Multi-format generation with immediate playback

**3. VC - JSON Request - URL Response.bru**
- **Input Method**: JSON body with file paths
- **Response**: JSON with file URLs and metadata
- **Use Case**: Batch processing, metadata requirements
- **Best For**: Web apps needing file info, async workflows

### File Upload Method (Direct Upload)

**4. VC - File Upload - Stream Response.bru**
- **Input Method**: Multipart form with file upload
- **Response**: Binary audio file streamed directly
- **Use Case**: Web interfaces, mobile apps
- **Best For**: User-uploaded content, forms

**5. VC - File Upload - Stream with Format Selection.bru**
- **Input Method**: Multipart form with file upload
- **Response**: Stream specific format from multiple generated
- **Features**: Upload + generate multiple formats + stream one
- **Best For**: Advanced chunking, quality optimization

**6. VC - File Upload - URL Response.bru**
- **Input Method**: Multipart form with file upload
- **Response**: JSON with file URLs and metadata
- **Use Case**: Complete upload-and-convert workflow
- **Best For**: Forms needing confirmation, user interfaces

## Quick Start

### Prerequisites

1. **Server Running**: Start API server on port 7860
2. **Environment**: Use "Local" environment in Bruno
3. **Files Ready**: 
   - **JSON method**: Files in `vc_inputs/` and `reference_audio/`
   - **Upload method**: Any audio files on your system

### Recommended First Test

Start with **"VC - JSON Request - Stream Response"**:

1. Open the request file
2. Verify file paths exist:
   - Input: `vc_inputs/josh.mp3`
   - Target: `reference_audio/speaker_en/DAVID-2.mp3`
3. Click "Send"
4. Download and play the streamed result

## Request Structure

### JSON Request Body
```json
{
  "input_audio_source": "josh.mp3",
  "target_voice_source": "speaker_en/DAVID-2.mp3",
  "chunk_sec": 60,
  "overlap_sec": 0.1,
  "export_formats": ["wav", "mp3"],
  "disable_watermark": true
}
```

### Multipart Form Data
```
input_audio: @file(./test-files/audio.wav)
target_voice_source: speaker_en/DAVID-2.mp3
chunk_sec: 60
overlap_sec: 0.1
export_formats: wav,mp3
disable_watermark: true
```

### Query Parameters
- `response_mode`: "stream" (default) or "url"
- `return_format`: "wav", "mp3", or "flac" (for stream mode)

## Parameters Explained

### Core Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `input_audio_source` | string | required | - | Input audio file path (JSON) or uploaded file (multipart) |
| `target_voice_source` | string | required | - | Target voice reference audio path |
| `chunk_sec` | integer | 60 | 10-300 | Audio chunk size in seconds |
| `overlap_sec` | float | 0.1 | 0.0-2.0 | Overlap between chunks for smooth transitions |
| `export_formats` | array/string | ["wav","mp3"] | wav,mp3,flac | Output formats to generate |
| `disable_watermark` | boolean | true | - | Disable audio watermarking |

### Parameter Optimization

**Chunk Size Selection** (chunk_sec):
- **< 2 minutes audio**: 60 seconds (single chunk, fastest)
- **2-10 minutes audio**: 30-45 seconds (balanced quality/speed)
- **> 10 minutes audio**: 20-30 seconds (prevents memory issues)

**Overlap Settings** (overlap_sec):
- **0.1s**: Standard, minimal overhead, good for speech
- **0.2s**: Smoother, better for music/singing
- **0.5-1.0s**: Very smooth but slower processing

**Format Selection**:
- **WAV**: Lossless, best quality, largest files (~10MB/min)
- **MP3**: Good quality, smallest files (~1MB/min), widely compatible
- **FLAC**: Lossless compressed, excellent balance (~5MB/min)

## Response Types

### Stream Response (response_mode=stream)

**Headers**:
```
Content-Type: audio/wav
Content-Disposition: attachment; filename="vc_2025-10-29_143045_789.wav"
X-Alternative-Formats: mp3:/outputs/vc_2025-10-29_143045_789.mp3
```

**Body**: Binary audio data

**Download**: Bruno automatically detects and offers to save the file

### URL Response (response_mode=url)

**JSON Body**:
```json
{
  "success": true,
  "output_files": [
    {
      "format": "wav",
      "filename": "vc_2025-10-29_143045_789_chunk60_overlap0.1.wav",
      "url": "/outputs/vc_2025-10-29_143045_789_chunk60_overlap0.1.wav",
      "path": "E:/Repos/Chatterbox-TTS-Extended-Plus/outputs/vc_2025-10-29_143045_789_chunk60_overlap0.1.wav"
    },
    {
      "format": "mp3",
      "filename": "vc_2025-10-29_143045_789_chunk60_overlap0.1.mp3",
      "url": "/outputs/vc_2025-10-29_143045_789_chunk60_overlap0.1.mp3",
      "path": "E:/Repos/Chatterbox-TTS-Extended-Plus/outputs/vc_2025-10-29_143045_789_chunk60_overlap0.1.mp3"
    }
  ],
  "processing_time_seconds": 8.7,
  "message": "Voice conversion completed successfully",
  "timestamp": "2025-10-29T14:30:45Z"
}
```

## File Setup Guide

### JSON Request Method

**1. Create Required Directories**:
```
vc_inputs/           # Input audio files
reference_audio/     # Target voice files
```

**2. Add Test Files**:
```
vc_inputs/
├── josh.mp3
├── sean.mp3
└── test_inputs/
    └── sample.mp3

reference_audio/
├── speaker_en/
│   └── DAVID-2.mp3
└── test_voices/
    └── linda_johnson_02.mp3
```

**3. Update Request Paths**:
- Edit JSON request bodies to match your actual file names
- Paths are relative to project root

### File Upload Method

**Option 1: Use test-files Directory** (Recommended)
```bash
mkdir bruno-collection/test-files
# Copy your audio files here
```

In Bruno requests:
```
input_audio: @file(./test-files/recording.wav)
```

**Option 2: Use Absolute Paths**
```
input_audio: @file(C:/Users/YourName/Music/recording.wav)
```

## Testing Workflow

### Recommended Testing Order

1. **JSON Stream** → Basic functionality
2. **JSON Stream Format** → Multi-format generation
3. **JSON URL** → Metadata and URL handling
4. **Upload Stream** → File upload capability
5. **Upload Stream Format** → Advanced features
6. **Upload URL** → Complete upload workflow

### Validation Checklist

For each request:
- [ ] Request completes with HTTP 200
- [ ] Response contains expected data/headers
- [ ] Generated files are playable
- [ ] File sizes are reasonable
- [ ] Alternative formats accessible (stream mode)
- [ ] Processing time acceptable
- [ ] Metadata accurate (URL mode)

## Troubleshooting

### Common Issues

**"File not found" Error**:
- **JSON method**: Verify files exist in `vc_inputs/` and `reference_audio/`
- **Upload method**: Check file path in `@file()` is correct
- Use absolute paths if relative paths fail

**Upload Fails**:
- Check file size (max 100MB)
- Verify format: WAV, MP3, or FLAC only
- Ensure file is not corrupted

**Poor Quality Output**:
- Use higher quality target voice (10-30s clear speech)
- Reduce chunk_sec for better processing
- Increase overlap_sec for smoother transitions
- Ensure input audio is clear with minimal noise

**Processing Too Slow**:
- Increase chunk_sec to reduce processing time
- Use fewer export_formats
- Check server isn't processing other requests

**First Request Timeout**:
- Models load on first request (30-60s)
- Make a simple health check first: GET /api/v1/health
- Subsequent requests will be much faster

### Monitoring

**Check Server Logs**:
```powershell
Get-Content logs/chatterbox_extended.log -Tail 20
```

**Look For**:
- Error messages with context
- Processing duration times
- Model loading status

## Performance Benchmarks

**Typical Processing Times** (60s chunks):
- 30 seconds audio: 15-30 seconds
- 2 minutes audio: 45-90 seconds
- 5 minutes audio: 2-4 minutes
- 10+ minutes: 0.4-0.8x audio length

**Factors Affecting Speed**:
- Chunk size (smaller = slower but better quality)
- Number of export formats
- Audio length and complexity
- System resources available

## Related Documentation

### Quick Reference
- **[VC Quick Reference](../quick-reference/voice-conversion.md)** - Parameter guide and use case summary

### API Documentation
- **[VC Endpoint Docs](../../docs/api/endpoints/voice-conversion.md)** - Complete API reference
- **[File Uploads Guide](../../docs/api/guides/file-uploads.md)** - Upload specifications
- **[Error Handling](../../docs/api/guides/error-handling.md)** - Error codes and solutions

### Testing
- **[VC Test Client](../../tests/test_vc_client.py)** - Python test client with examples

## Tips for Success

1. **Start Simple**: Use JSON Stream with default parameters first
2. **Test Incrementally**: Add features one at a time
3. **Monitor Logs**: Watch server logs during processing
4. **Optimize Parameters**: Adjust chunk_sec and overlap_sec based on results
5. **Choose Right Mode**: Stream for immediate use, URL for workflows
6. **Plan Formats**: Generate only formats you need to save time

---

*For general Bruno collection information, see [main README](../README.md)*  
*Last updated: October 29, 2025*
