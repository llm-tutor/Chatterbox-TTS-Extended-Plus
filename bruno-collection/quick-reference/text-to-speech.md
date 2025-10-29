# Text-to-Speech (TTS) Quick Reference

Quick parameter guide and use case reference for the TTS endpoint.

## Request Variants Table

| # | Request File | Input | Response | Formats | Features |
|---|-------------|-------|----------|---------|----------|
| 1 | TTS - Basic Stream Response | JSON/Text | Stream | WAV | Basic, default voice |
| 2 | TTS - Stream with Format Selection | JSON/Text | Stream | WAV, MP3, FLAC | Voice cloning, format selection |
| 3 | TTS - URL Response with Metadata | JSON/Text | JSON/URL | WAV, MP3, FLAC | Metadata, processing time |
| 4 | TTS - Speed Control Example | JSON/Text | JSON/URL | WAV, MP3 | Speed adjustment (1.3x) |
| 5 | TTS - Audio Trimming Example | JSON/Text | JSON/URL | WAV, MP3 | Silence removal |
| 6 | TTS - Project Organization Example | JSON/Text | JSON/URL | WAV, MP3 | Folder organization |

## Parameter Quick Reference

### Core Parameters

| Parameter | Quick Values | Use When |
|-----------|--------------|----------|
| `text` | Any string (1-10,000 chars) | Required - text to synthesize |
| `reference_audio_filename` | "speaker_en/jamie_vc_to_david-2.wav" | Want voice cloning |
| `export_formats` | ["wav"], ["mp3"], ["wav","mp3","flac"] | Choose output formats |
| `project` | "my_audiobook/chapter_01" | Want organized folders |

### Voice Quality Parameters

| Parameter | Default | Quick Settings | Effect |
|-----------|---------|----------------|---------|
| `temperature` | 0.75 | 0.6=consistent, 0.8=varied | Randomness in generation |
| `exaggeration` | 0.5 | 0.3=calm, 0.7=expressive | Emotion intensity |
| `seed` | 0 (random) | 42, 123, etc. | Reproducibility |
| `cfg_weight` | 1.0 | 0.8-1.2 | Guidance strength |

### Speed Control

| Parameter | Default | Quick Settings | Result |
|-----------|---------|----------------|---------|
| `speed_factor` | 1.0 | 0.8=slower, 1.3=faster, 1.5=fast | Playback speed |
| `speed_factor_library` | "auto" | "audiostretchy" | Best quality for speech |

**Speed Examples**:
- 0.8: 20% slower (learning materials)
- 1.0: Normal speed
- 1.3: 30% faster (time-saving)
- 1.5: 50% faster (quick content)

### Audio Trimming

| Parameter | Default | Quick Settings | Purpose |
|-----------|---------|----------------|---------|
| `trim` | false | true | Enable silence removal |
| `trim_threshold_ms` | 200 | 150=aggressive, 250=conservative | Silence threshold |

### Processing Control

| Parameter | Default | Quick Settings | Effect |
|-----------|---------|----------------|---------|
| `bypass_whisper_checking` | false | true | Skip validation (faster) |
| `num_candidates_per_chunk` | 3 | 1=fast, 5=quality | Generation attempts |

## Response Mode Selection

| Mode | Query Parameter | Response Type | Use When |
|------|----------------|---------------|----------|
| Stream | `?response_mode=stream` or default | Binary audio file | Want immediate download |
| URL | `?response_mode=url` | JSON with URLs | Need metadata or batch processing |

### Format Selection (Stream Mode Only)

| Parameter | Values | Effect |
|-----------|--------|---------|
| `return_format` | "wav", "mp3", "flac" | Which format to stream (others in X-Alternative-Formats) |

## Common Use Cases

### 1. Quick Test (No Voice Cloning)
```json
{
  "text": "Hello world!",
  "export_formats": ["wav"]
}
```
**Time**: 2-3 seconds

### 2. Voice Cloning
```json
{
  "text": "Your text here",
  "reference_audio_filename": "speaker_en/jamie_vc_to_david-2.wav",
  "export_formats": ["wav", "mp3"]
}
```
**Time**: 5-10 seconds

### 3. Reproducible Generation
```json
{
  "text": "Same every time",
  "seed": 42,
  "temperature": 0.6
}
```
**Time**: 3-5 seconds

### 4. Faster Speech (Audiobooks)
```json
{
  "text": "Your audiobook text",
  "speed_factor": 1.3,
  "speed_factor_library": "audiostretchy"
}
```
**Time**: 8-12 seconds

### 5. Professional Output (Trimmed)
```json
{
  "text": "Clean professional audio",
  "trim": true,
  "trim_threshold_ms": 150,
  "export_formats": ["wav"]
}
```
**Time**: 5-8 seconds

### 6. Organized Project
```json
{
  "text": "Chapter content",
  "project": "audiobook/chapter_01",
  "reference_audio_filename": "narrator.wav"
}
```
**Time**: 6-10 seconds

## Performance Estimates

| Scenario | Approximate Time | Notes |
|----------|------------------|-------|
| Basic (1 sentence) | 2-3s | No voice cloning |
| Voice cloning (1 paragraph) | 8-12s | With reference audio |
| Speed adjusted (1.3x) | 10-15s | Using audiostretchy |
| Trimmed audio | +1-2s | Additional processing |
| Multiple formats (3) | +2-5s | Parallel generation |
| With validation | +30-50% | Whisper checking |

## Example Reference Audio Files

Common reference audio files used in examples:

| Path | Description | Use Case |
|------|-------------|----------|
| `speaker_en/jamie_vc_to_david-2.wav` | English speaker | General voice cloning |
| `speaker_en/DAVID-2.mp3` | David voice | Alternative English voice |
| `test_voices/linda_johnson_01.mp3` | Linda voice #1 | Testing |
| `test_voices/linda_johnson_02.mp3` | Linda voice #2 | Testing |

## Optimization Tips

### For Fastest Processing
- Use `bypass_whisper_checking: true`
- Single format only: `["wav"]`
- Lower candidates: `num_candidates_per_chunk: 1`
- No speed adjustment or trimming

### For Best Quality
- Use quality reference audio (10-30s clear speech)
- Enable Whisper checking (default)
- Higher candidates: `num_candidates_per_chunk: 3-5`
- Lower temperature: `0.6-0.7`
- Use audiostretchy for speed control

### For Consistency
- Set fixed seed: `seed: 42`
- Lower temperature: `0.6`
- Same reference audio each time
- Consistent exaggeration value

### For Expressiveness
- Higher exaggeration: `0.7-0.8`
- Moderate temperature: `0.75-0.85`
- Quality reference audio with emotion

## Format Comparison

| Format | Quality | Size (per min) | Compatibility | Best For |
|--------|---------|----------------|---------------|----------|
| WAV | Lossless | ~10 MB | Universal | Production, editing |
| MP3 | Good | ~1 MB | Universal | Distribution, streaming |
| FLAC | Lossless | ~5 MB | Most players | Archive, quality priority |

## Troubleshooting Quick Guide

| Problem | Quick Fix |
|---------|-----------|
| Too slow | Set `bypass_whisper_checking: true` |
| Inconsistent output | Use fixed `seed` and lower `temperature` |
| Poor voice match | Use better quality reference audio (10-30s) |
| Unnatural speed | Try `speed_factor_library: "audiostretchy"` |
| Too much silence | Enable `trim: true` |
| Text too long | Split into chunks or enable `enable_batching` |

## Related Documentation

- **[Full TTS Endpoint Docs](../../docs/api/endpoints/tts.md)** - Complete API reference
- **[TTS README](../Text-to-Speech/README.md)** - Detailed Bruno collection guide
- **[Speed Control Guide](../../docs/api/guides/advanced-features.md#speed-control)** - Speed adjustment details

---

*Last updated: October 29, 2025*
