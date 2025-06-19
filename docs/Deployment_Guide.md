# Deployment Guide - Chatterbox TTS Extended Plus

## Quick Deployment

### Prerequisites
- Python 3.8+
- CUDA-compatible GPU (recommended) or CPU
- 8GB+ RAM
- 10GB+ disk space for models

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd Chatterbox-TTS-Extended-Plus
```

2. **Create virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Setup directories:**
```bash
mkdir -p reference_audio/speaker1
mkdir -p vc_inputs
mkdir -p outputs
mkdir -p temp
mkdir -p logs
```

5. **Start the server:**
```bash
python main_api.py
```

### Configuration

Edit `config.yaml` to customize:

```yaml
server:
  host: "127.0.0.1"    # Change to "0.0.0.0" for network access
  port: 7860
  
paths:
  reference_audio_dir: "reference_audio"
  vc_input_dir: "vc_inputs"
  output_dir: "outputs"
  
models:
  device: "auto"       # auto, cuda, cpu
  preload_models: true
```

### Adding Audio Files

**Reference Audio (for TTS and VC targets):**
- Place in `reference_audio/` directory
- Organize in subdirectories (e.g., `speaker1/`, `speaker2/`)
- Supported formats: WAV, MP3, FLAC
- Recommended: 10-60 second samples, good quality

**VC Input Audio:**
- Place in `vc_inputs/` directory
- Any length audio files to be converted

### Testing

```bash
# Health check
curl http://localhost:7860/api/v1/health

# Basic TTS
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "export_formats": ["wav"]}'
```

### Production Deployment

For production use:

1. **Use a process manager:**
```bash
# Using systemd (Linux)
sudo nano /etc/systemd/system/chatterbox-tts.service
```

2. **Enable HTTPS with reverse proxy:**
```nginx
# Nginx configuration
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Configure firewall:**
```bash
# Allow only specific IPs
ufw allow from 192.168.1.0/24 to any port 7860
```

### Troubleshooting

**Common Issues:**

1. **CUDA not detected:**
   - Install PyTorch with CUDA support
   - Check `nvidia-smi` output
   - Set `device: "cpu"` in config if needed

2. **Models not loading:**
   - Check internet connection for first-time download
   - Ensure sufficient disk space
   - Check logs for detailed errors

3. **Audio files not found:**
   - Verify file paths and permissions
   - Check directory structure
   - Ensure supported audio formats

4. **Performance issues:**
   - Use GPU if available
   - Reduce `num_candidates_per_chunk`
   - Disable Whisper validation for speed

### Monitoring

Check logs at: `logs/chatterbox_extended.log`

Monitor endpoints:
- Health: `/api/v1/health`
- System status via logs
- File system usage in `outputs/` directory

### Security Considerations

**For local use only:**
- Default configuration binds to localhost only
- No authentication required
- File system access limited to configured directories

**For network deployment:**
- Change host to `0.0.0.0` in config
- Add firewall rules
- Consider adding authentication
- Use HTTPS in production
- Limit file upload sizes
- Monitor disk usage for outputs
