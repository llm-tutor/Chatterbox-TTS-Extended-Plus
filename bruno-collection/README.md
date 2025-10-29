# Chatterbox TTS Extended Plus - Bruno API Collection

This Bruno collection provides comprehensive testing and documentation for the Chatterbox TTS Extended Plus API endpoints.

## Overview

Bruno is a fast, Git-friendly, open-source API client. This collection is structured to provide easy testing of all major API endpoints with multiple request variants for each.

## Prerequisites

1. **Install Bruno**: Download from [https://www.usebruno.com/](https://www.usebruno.com/)
2. **Start the API Server**: 
   ```bash
   cd E:\Repos\Chatterbox-TTS-Extended-Plus
   .venv\Scripts\activate
   python main_api.py
   ```
3. **Prepare Test Files**: Ensure you have audio files in the required directories (see endpoint-specific docs)

## Collection Structure

```
bruno-collection/
├── README.md                          # This file - overview and index
├── quick-reference/                   # Quick reference guides
│   ├── README.md                     # Quick reference index
│   ├── voice-conversion.md           # VC quick reference
│   ├── text-to-speech.md             # TTS quick reference
│   └── concatenation.md              # Concat quick reference
├── environments/
│   └── Local.bru                     # Local environment (localhost:7860)
├── Voice Conversion/                  # VC endpoint requests (6 variants)
│   └── [.bru request files]
├── Text-to-Speech/                    # TTS endpoint requests (6 variants)
│   └── [.bru request files]
└── Audio Concatenation/               # Concat endpoint requests (7 variants)
    └── [.bru request files]
```

## Available Endpoints

### Voice Conversion (VC)
**Status**: ✅ Complete (6 request variants)  
**Endpoint**: POST /api/v1/vc  
**Purpose**: Transform voice characteristics in audio files

**Request Variants**:
- JSON Request × Stream Response
- JSON Request × Stream with Format Selection
- JSON Request × URL Response
- File Upload × Stream Response
- File Upload × Stream with Format Selection
- File Upload × URL Response

**Documentation**:
- **Detailed Guide**: [Voice Conversion Folder](Voice%20Conversion/) (includes comprehensive README)
- **Quick Reference**: [voice-conversion.md](quick-reference/voice-conversion.md)

### Text-to-Speech (TTS)
**Status**: ✅ Complete (6 request variants)  
**Endpoint**: POST /api/v1/tts  
**Purpose**: Generate speech from text with voice cloning and advanced features

**Request Variants**:
- Basic Stream Response (default voice)
- Stream with Format Selection (voice cloning, multiple formats)
- URL Response with Metadata (JSON response)
- Speed Control Example (adjustable playback speed)
- Audio Trimming Example (silence removal)
- Project Organization Example (folder structure)

**Documentation**:
- **Detailed Guide**: [Text-to-Speech Folder](Text-to-Speech/) (includes comprehensive README)
- **Quick Reference**: [text-to-speech.md](quick-reference/text-to-speech.md)

### Audio Concatenation
**Status**: ✅ Complete (7 request variants)  
**Endpoints**: POST /api/v1/concat (basic), POST /api/v1/concat/mixed (advanced)  
**Purpose**: Combine multiple audio files with professional production features

**Request Variants**:
- Basic Stream Response (simple concatenation)
- Basic URL Response (metadata and file info)
- Basic with Trimming (automatic silence removal)
- Basic with Crossfade (smooth transitions)
- Mixed Stream Response (server files + uploads + silence)
- Mixed Stream Format Selection (multiple formats)
- Mixed URL Response (complete workflow with metadata)

**Documentation**:
- **Detailed Guide**: [Audio Concatenation Folder](Audio%20Concatenation/) (includes comprehensive README)
- **Quick Reference**: [concatenation.md](quick-reference/concatenation.md)

### Voice Management
**Status**: 🚧 Planned  
**Endpoints**: POST /api/v1/voices, GET /api/v1/voices, DELETE /api/v1/voices/{name}  
**Purpose**: Upload and manage reference voices

*Coming soon...*

### File Operations
**Status**: 🚧 Planned  
**Endpoints**: GET /api/v1/outputs, GET /api/v1/outputs/{filename}, DELETE /api/v1/outputs  
**Purpose**: List, download, and manage generated files

*Coming soon...*

## Getting Started

### 1. Open Collection in Bruno

1. Launch Bruno
2. Click "Open Collection"
3. Navigate to: `E:\Repos\Chatterbox-TTS-Extended-Plus\bruno-collection`
4. Select the folder

### 2. Configure Environment

The collection uses the `Local` environment by default:
- **Base URL**: `http://localhost:7860/api/v1`

To modify:
1. Go to Environments in Bruno
2. Select "Local"
3. Update variables as needed

### 3. Start Testing

#### Option 1: Browse by Endpoint
Navigate to endpoint folders (e.g., "Voice Conversion") and select specific requests.

#### Option 2: Use Quick References
Check [quick-reference/](quick-reference/) for parameter guides and use case summaries.

### 4. Run Your First Request

**For Voice Conversion**: **VC - JSON Request - Stream Response**

1. Navigate to `Voice Conversion` folder
2. Open "VC - JSON Request - Stream Response"
3. Review the pre-configured request
4. Update file paths if needed (josh.mp3, DAVID-2.mp3)
5. Click "Send" or press Ctrl+Enter
6. View the streamed audio response

**For Text-to-Speech**: **TTS - Basic Stream Response**

1. Navigate to `Text-to-Speech` folder
2. Open "TTS - Basic Stream Response"
3. Review the text parameter
4. Click "Send" or press Ctrl+Enter
5. Download and play the generated speech

## General Tips and Best Practices

### File Preparation

**For Voice Conversion**:

**JSON Requests** (files on server):
- Input audio: Place in `vc_inputs/` directory
- Target voices: Place in `reference_audio/` directory

**File Upload Requests**:
- Upload directly from anywhere on your system
- Update file path in Bruno: `@file(C:/path/to/audio.wav)`

**For Text-to-Speech**:

**Reference Audio** (optional, for voice cloning):
- Place reference voices in `reference_audio/` directory
- Examples: `speaker_en/jamie_vc_to_david-2.wav`, `test_voices/linda_johnson_01.mp3`
- Requirements: 10-30 seconds of clear speech, minimal noise

### Response Types

**Stream Mode** (response_mode=stream):
- Returns binary audio file directly
- Fastest for immediate playback
- Check X-Alternative-Formats header for other formats

**URL Mode** (response_mode=url):
- Returns JSON with file URLs and metadata
- Best for batch processing
- Includes processing time and file information

### Performance Considerations

**First Request After Server Start**:
- Model loading may cause delay (30-60 seconds)
- Subsequent requests will be much faster
- Consider making a health check first: GET /api/v1/health

**Processing Time Estimates**:

**Voice Conversion**:
- 30 seconds audio: 15-30 seconds
- 2 minutes audio: 45-90 seconds  
- 5 minutes audio: 2-4 minutes
- 10+ minutes: 0.4-0.8x audio length

**Text-to-Speech**:
- 1-2 sentences: 2-5 seconds
- 1 paragraph: 5-15 seconds (with quality validation)
- Long text (batched): 30-60 seconds
- With voice cloning: +20-50% processing time

### Monitoring and Debugging

**View Server Logs**:
```powershell
# View last 20 lines
Get-Content logs/chatterbox_extended.log -Tail 20

# Monitor in real-time
Get-Content logs/chatterbox_extended.log -Wait
```

**Check Server Health**:
- GET http://localhost:7860/api/v1/health
- Verify model status and configuration

## Troubleshooting

### Common Issues

**Server Not Running**:
- Start server: `python main_api.py`
- Check health endpoint: GET /api/v1/health
- Verify port 7860 is available

**File Not Found**:
- Verify file paths in requests
- Check files exist in correct directories
- For uploads, use absolute paths

**Slow Performance**:
- First request after start takes longer (model loading)
- Check server logs for errors
- For VC: Increase chunk_sec parameter
- For TTS: Set `bypass_whisper_checking: true` for faster processing

**Request Fails**:
- Review response body for error details
- Check server logs: `logs/chatterbox_extended.log`
- Verify file formats (WAV, MP3, FLAC supported)

## Related Documentation

### API Documentation
- **Main API Docs**: `docs/api/README.md`
- **Voice Conversion**: `docs/api/endpoints/voice-conversion.md`
- **Text-to-Speech**: `docs/api/endpoints/tts.md`
- **Quick Start Guide**: `docs/api/quick-start.md`
- **Error Handling**: `docs/api/guides/error-handling.md`

### Development
- **Implementation Protocols**: `docs/dev/implementation-protocols.md`
- **VC Test Client**: `tests/test_vc_client.py`
- **TTS Test Client**: `tests/test_tts_client.py`

## Contributing

When adding new endpoints to this collection:

1. Create endpoint folder with descriptive name
2. Add .bru request files for all variants
3. Create detailed README.md in endpoint folder
4. Add quick reference to `quick-reference/` directory
5. Update this main README.md with endpoint info
6. Test all requests and verify documentation

## Support

For issues or questions:
1. Check endpoint-specific README files
2. Review API documentation in `docs/api/`
3. Check server logs in `logs/chatterbox_extended.log`
4. Consult implementation protocols in `docs/dev/`

---

*Last updated: October 29, 2025*
