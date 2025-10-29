# Voice Conversion - Quick Reference

> **Endpoint**: POST /api/v1/vc  
> **Purpose**: Transform voice characteristics in audio files  
> **Full Documentation**: [Voice Conversion README](../Voice%20Conversion/README.md)

## Request Variants Summary

| # | Name | Input Method | Response Mode | Use Case |
|---|------|--------------|---------------|----------|
| 1 | JSON Stream | JSON (server files) | Stream binary | Quick conversion of server files |
| 2 | JSON Stream Format | JSON (server files) | Stream specific format | Multiple formats, stream one |
| 3 | JSON URL | JSON (server files) | JSON with URLs | Batch processing, metadata needs |
| 4 | Upload Stream | Multipart upload | Stream binary | Web/mobile app uploads |
| 5 | Upload Stream Format | Multipart upload | Stream specific format | Upload + multiple formats |
| 6 | Upload URL | Multipart upload | JSON with URLs | Complete upload workflow |

## Parameter Quick Reference

### Chunk Size (chunk_sec)
- Less than 2 min audio: 60 seconds
- 2-10 min audio: 30-45 seconds  
- More than 10 min audio: 20-30 seconds

### Overlap (overlap_sec)
- Standard: 0.1 seconds
- Smooth music: 0.2 seconds
- Very smooth: 0.5-1.0 seconds

### Formats (export_formats)
- JSON: ["wav", "mp3", "flac"]
- Form: wav,mp3,flac

## Endpoint Details

**URL**: POST /api/v1/vc

**Query Parameters**:
- response_mode=stream (default, returns binary)
- response_mode=url (returns JSON)
- return_format=mp3 (which format to stream)

## Example Files

### Server-side Files (JSON Method)
- Input: vc_inputs/josh.mp3
- Target: reference_audio/speaker_en/DAVID-2.mp3

### File Upload Paths (Multipart Method)
- Local: @file(./test-files/recording.wav)
- Absolute: @file(C:/Users/You/Documents/audio.mp3)

---

*For detailed documentation, parameters, troubleshooting, and examples, see the [main Voice Conversion README](../README.md)*
