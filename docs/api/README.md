# Chatterbox TTS Extended Plus - API Documentation

Welcome to the comprehensive API documentation for Chatterbox TTS Extended Plus. This documentation is organized into focused sections to help you find exactly what you need quickly and efficiently.

## How to Use This Documentation

### For New Users
1. Start with the [Quick Start Guide](quick-start.md) to get up and running in minutes
2. Explore specific endpoints in the [Endpoints](endpoints/) directory
3. Review [Examples](schemas/examples/) for copy-paste code samples

### For Developers
1. Check [Endpoint Documentation](endpoints/) for detailed API references
2. Review [Schema Documentation](schemas/) for request/response models
3. Use [Feature Guides](guides/) for advanced functionality

### For Integrators
1. Download the [OpenAPI Specification](openapi.yaml) for tool integration
2. Review [Compatibility](reference/compatibility.md) for supported standards
3. Check [Configuration](reference/configuration.md) for deployment options

## Documentation Structure

### Getting Started
- **[Quick Start Guide](quick-start.md)** - Installation, basic setup, and first API calls
- **[Error Handling Guide](guides/error-handling.md)** - Understanding and handling API errors

### API Reference
- **[Health Endpoint](endpoints/health.md)** - Service status and diagnostics
- **[Text-to-Speech (TTS)](endpoints/tts.md)** - Generate speech from text
- **[Voice Conversion (VC)](endpoints/voice-conversion.md)** - Transform voice characteristics
- **[Audio Concatenation](endpoints/concatenation.md)** - Combine multiple audio files with professional features
- **[Voice Management](endpoints/voice-management.md)** - Upload and manage reference voices
- **[File Operations](endpoints/file-operations.md)** - List, download, and manage generated files and VC inputs with folder organization

### Advanced Features
- **[Streaming Responses](guides/streaming-responses.md)** - Direct file downloads
- **[File Uploads](guides/file-uploads.md)** - Upload audio files for processing
- **[File Management Workflows](guides/file-management-workflows.md)** - Complete file organization, search, and cleanup workflows
- **[Advanced Features](guides/advanced-features.md)** - Speed control, concatenation, and more

### Code Examples
- **[cURL Examples](schemas/examples/curl-examples.md)** - Command-line API usage
- **[Python Examples](schemas/examples/python-examples.md)** - Python integration code

### Technical Reference
- **[Request Models](schemas/request-models.md)** - API request structures
- **[Response Models](schemas/response-models.md)** - API response formats
- **[Configuration](reference/configuration.md)** - Server and feature configuration
- **[File Structure](reference/file-structure.md)** - Audio file organization
- **[OpenAI Compatibility](reference/compatibility.md)** - Compatible endpoints and differences
- **[Administrative Endpoints](reference/administrative-endpoints.md)** - System monitoring, cleanup, and debugging endpoints

## API Endpoint Classification

This documentation uses a two-tier approach to organize endpoints based on their intended audience:

### Core API (Main Documentation)
**Audience**: End users, application developers, API integrators  
**Coverage**: Primary functionality for TTS, voice conversion, and voice management  
**Location**: Main `openapi.yaml` specification and endpoint documentation

**Includes**: `/tts`, `/vc`, `/concat`, `/voice*`, `/voices*`, `/outputs`, `/health`, `/config`

### Administrative API (Separate Documentation)
**Audience**: System administrators, DevOps teams, monitoring systems  
**Coverage**: System monitoring, resource management, cleanup, and debugging  
**Location**: [Administrative Endpoints Reference](reference/administrative-endpoints.md)

**Includes**: `/metrics`, `/resources`, `/cleanup*`, `/errors*`

> **Note**: This separation supports future automation where endpoint classification and documentation generation will be handled automatically based on endpoint patterns and purposes.

## Interactive Documentation

When the API server is running, you can access interactive documentation:
- **Swagger UI:** http://localhost:7860/docs
- **ReDoc:** http://localhost:7860/redoc

## Quick Reference

### Essential Commands
```bash
# Start the API server
python main_api.py

# Health check
curl http://localhost:7860/api/v1/health

# Simple TTS generation
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world!", "export_formats": ["wav", "mp3"]}'
```

### Key URLs
- **Base URL:** http://localhost:7860
- **API Prefix:** /api/v1
- **Generated Files:** http://localhost:7860/outputs/{filename}

## Project Information

**Version:** 1.0.0  
**Repository:** [Chatterbox-TTS-Extended-Plus](../../)  
**Main README:** [README-API.md](../../README-API.md)

## Documentation Maintenance

For information on updating and maintaining this documentation, see [How to Update API Docs](how-to-update-api-docs.md).

---

*Last updated: June 22, 2025*