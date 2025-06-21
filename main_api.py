# main_api.py - FastAPI application entry point

import asyncio
import logging
import time
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Union, Optional

from fastapi import FastAPI, HTTPException, Request, Query, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api_models import (
    TTSRequest, VCRequest, TTSResponse, VCResponse, 
    ErrorResponse, HealthResponse, ConfigResponse,
    VoicesResponse, VoiceInfo, VoiceMetadata, ErrorSummaryResponse
)
from core_engine import engine_sync, get_or_load_tts_model, get_or_load_vc_model
from config import config_manager
from exceptions import (
    ChatterboxAPIError, ValidationError, ResourceError, 
    ModelLoadError, GenerationError
)

# Enhanced monitoring
from monitoring import (
    get_logger, get_metrics, get_system_metrics, 
    RequestLoggingMiddleware, log_request_body_middleware,
    record_operation_time
)

# Resource management
from management import cleanup_scheduler, resource_manager

# Setup enhanced logging
logger = get_logger(__name__)

# Track startup time for health endpoint
app_start_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting Chatterbox TTS Extended Plus API")
    
    # Create necessary directories
    for dir_key in ["output_dir", "temp_dir", "reference_audio_dir", "vc_input_dir"]:
        dir_path = Path(config_manager.get(f"paths.{dir_key}", dir_key.replace("_dir", "")))
        dir_path.mkdir(exist_ok=True)
    
    # Preload models if configured
    if config_manager.get("models.preload_models", True):
        try:
            logger.info("Preloading models...")
            get_or_load_tts_model()
            get_or_load_vc_model()
            logger.info("Models preloaded successfully")
        except Exception as e:
            logger.warning(f"Could not preload models: {e}")
    
    # Start cleanup scheduler
    try:
        cleanup_scheduler.start()
        logger.info("Cleanup scheduler started successfully")
    except Exception as e:
        logger.warning(f"Could not start cleanup scheduler: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    cleanup_scheduler.stop()
    engine_sync.cleanup_temp_files()


# ===== STREAMING RESPONSE UTILITIES =====

def create_file_stream_response(file_path: Path, media_type: str = "audio/wav") -> StreamingResponse:
    """Create a streaming response for audio file download"""
    def file_streamer():
        with open(file_path, "rb") as file:
            while chunk := file.read(8192):  # 8KB chunks
                yield chunk
    
    # Determine proper media type based on file extension
    ext = file_path.suffix.lower()
    content_type = {
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg', 
        '.flac': 'audio/flac',
        '.ogg': 'audio/ogg'
    }.get(ext, 'application/octet-stream')
    
    headers = {
        'Content-Disposition': f'attachment; filename="{file_path.name}"',
        'Content-Type': content_type
    }
    
    return StreamingResponse(
        file_streamer(),
        media_type=content_type,
        headers=headers
    )


def should_stream_response(response_mode: str = "stream") -> bool:
    """Determine if response should be streamed or return JSON URLs"""
    return response_mode.lower() in ["stream", "file", "download"]


# Create FastAPI app
app = FastAPI(
    title="Chatterbox TTS Extended Plus API",
    description="API for Text-to-Speech and Voice Conversion with Enhanced Monitoring",
    version="1.7.0",
    lifespan=lifespan
)

# Add enhanced request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add request body logging middleware for API endpoints
app.middleware("http")(log_request_body_middleware)
# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for outputs
outputs_dir = Path(config_manager.get("paths.output_dir", "outputs"))
outputs_dir.mkdir(exist_ok=True)
app.mount("/outputs", StaticFiles(directory=str(outputs_dir)), name="outputs")

# Exception handlers
@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error=str(exc),
            error_code="VALIDATION_ERROR"
        ).model_dump()
    )

@app.exception_handler(ResourceError)
async def resource_error_handler(request: Request, exc: ResourceError):
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error=str(exc),
            error_code="RESOURCE_NOT_FOUND"
        ).model_dump()
    )

@app.exception_handler(ModelLoadError)
async def model_load_error_handler(request: Request, exc: ModelLoadError):
    return JSONResponse(
        status_code=503,
        content=ErrorResponse(
            error=str(exc),
            error_code="MODEL_LOAD_ERROR"
        ).model_dump()
    )

@app.exception_handler(GenerationError)
async def generation_error_handler(request: Request, exc: GenerationError):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=str(exc),
            error_code="GENERATION_ERROR"
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            error_code="INTERNAL_ERROR"
        ).model_dump()
    )

# API Endpoints
@app.post("/api/v1/tts", response_model=TTSResponse)
async def generate_tts(
    request: TTSRequest, 
    response_mode: str = Query("stream", description="Response mode: 'stream' for direct download, 'url' for JSON response"),
    return_format: str = Query(None, description="Format to stream (wav, mp3, flac). If not specified, uses first format from export_formats")
) -> Union[TTSResponse, StreamingResponse]:
    """Generate Text-to-Speech audio with optional streaming response"""
    try:
        # Convert request to dict and call synchronous method
        request_dict = request.model_dump()
        
        # Run the synchronous TTS generation in thread pool for FastAPI compatibility
        def run_tts():
            return engine_sync.generate_tts(**request_dict)
        
        # Use run_in_executor for non-blocking FastAPI operation
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_tts)
        
        # Check if we should stream the response
        if should_stream_response(response_mode) and result.get('output_files'):
            # Determine which file to stream
            target_format = return_format or request.export_formats[0] if request.export_formats else "wav"
            target_format = target_format.lower()
            
            # Find the requested format in output files
            stream_file = None
            for file_info in result['output_files']:
                if file_info['format'].lower() == target_format:
                    stream_file = file_info
                    break
            
            if not stream_file:
                # Fallback to first available format
                stream_file = result['output_files'][0]
                logger.warning(f"Requested format '{target_format}' not found, using '{stream_file['format']}'")
            
            file_path = Path(stream_file['path'])
            if file_path.exists():
                logger.info(f"Streaming TTS output: {file_path.name} (format: {stream_file['format']})")
                
                # Create streaming response with additional headers containing alternative formats
                streaming_response = create_file_stream_response(file_path)
                
                # Add alternative format URLs in custom headers
                alt_formats = []
                for file_info in result['output_files']:
                    if file_info['format'] != stream_file['format']:
                        alt_formats.append(f"{file_info['format']}:{file_info['url']}")
                
                if alt_formats:
                    streaming_response.headers["X-Alternative-Formats"] = "|".join(alt_formats)
                
                return streaming_response
            else:
                logger.warning(f"Output file not found for streaming: {file_path}")
                # Fall back to JSON response
        
        # Return JSON response (default or fallback)
        return TTSResponse(**result)
    except ChatterboxAPIError:
        raise  # Let the exception handlers deal with these
    except Exception as e:
        logger.error(f"Unexpected error in TTS generation: {e}")
        raise GenerationError(f"TTS generation failed: {e}")

@app.post("/api/v1/vc", response_model=VCResponse)
async def generate_vc(
    request: Request,
    response_mode: str = Query("stream", description="Response mode: 'stream' for direct download, 'url' for JSON response"),
    return_format: str = Query(None, description="Format to stream (wav, mp3, flac). If not specified, uses first format from export_formats"),
    # File upload parameters (optional for multipart/form-data)
    input_audio: UploadFile = File(None, description="Input audio file to convert (alternative to input_audio_source)"),
    target_voice_source: str = Form(None, description="Target voice source (filename or URL)"),
    chunk_sec: int = Form(None, description="Chunk size in seconds"),
    overlap_sec: float = Form(None, description="Overlap in seconds"),
    disable_watermark: bool = Form(None, description="Disable watermark"),
    export_formats: str = Form(None, description="Export formats (comma-separated)")
) -> Union[VCResponse, StreamingResponse]:
    """Generate Voice Conversion with support for both JSON and file upload"""
    temp_input_path = None
    try:
        # Check content type to determine request mode
        content_type = request.headers.get("content-type", "")
        logger.info(f"VC request debug - content_type: {content_type}, input_audio: {input_audio is not None}")
        
        if content_type.startswith("application/json"):
            # JSON mode - parse manually
            json_body = await request.json()
            vc_request = VCRequest(**json_body)
            request_dict = vc_request.model_dump()
            logger.info(f"JSON mode: parsed request with keys: {list(request_dict.keys())}")
            
        elif input_audio and input_audio.filename:
            # File upload mode (multipart/form-data)
            # File upload mode
            if not target_voice_source:
                raise ValidationError("target_voice_source is required for file upload")
            
            # Validate uploaded file
            allowed_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
            file_ext = Path(input_audio.filename).suffix.lower()
            if file_ext not in allowed_extensions:
                raise ValidationError(f"Unsupported audio format: {file_ext}. Supported: {allowed_extensions}")
            
            # Validate file size (max 100MB)
            max_size = 100 * 1024 * 1024  # 100MB
            content = await input_audio.read()
            if len(content) > max_size:
                raise ValidationError(f"File too large. Maximum size: {max_size // (1024*1024)}MB")
            
            # Create temp directory and save uploaded file
            temp_dir = Path(config_manager.get("paths.temp_dir", "temp"))
            temp_dir.mkdir(exist_ok=True)
            
            import time
            timestamp = int(time.time())
            temp_filename = f"upload_{timestamp}_{input_audio.filename}"
            temp_input_path = temp_dir / temp_filename
            
            with open(temp_input_path, "wb") as temp_file:
                temp_file.write(content)
            
            logger.info(f"Uploaded file saved to: {temp_input_path}")
            
            # Build request parameters from form data
            export_formats_list = [fmt.strip() for fmt in export_formats.split(",")] if export_formats else ["wav", "mp3"]
            
            request_dict = {
                'input_audio_source': str(temp_input_path),
                'target_voice_source': target_voice_source,
                'chunk_sec': chunk_sec if chunk_sec is not None else 60,
                'overlap_sec': overlap_sec if overlap_sec is not None else 0.1,
                'disable_watermark': disable_watermark if disable_watermark is not None else True,
                'export_formats': export_formats_list
            }
            
        else:
            raise ValidationError("Either provide JSON body or upload files with form parameters")
        
        # Run the synchronous VC generation
        def run_vc():
            return engine_sync.generate_vc(**request_dict)
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_vc)
        
        # Check if we should stream the response
        if should_stream_response(response_mode) and result.get('output_files'):
            # Determine which file to stream
            if request_dict.get('export_formats'):
                target_format = return_format or request_dict['export_formats'][0]
            else:
                target_format = return_format or "wav"
            target_format = target_format.lower()
            
            # Find the requested format in output files
            stream_file = None
            for file_info in result['output_files']:
                if file_info['format'].lower() == target_format:
                    stream_file = file_info
                    break
            
            if not stream_file:
                # Fallback to first available format
                stream_file = result['output_files'][0]
                logger.warning(f"Requested format '{target_format}' not found, using '{stream_file['format']}'")
            
            file_path = Path(stream_file['path'])
            if file_path.exists():
                logger.info(f"Streaming VC output: {file_path.name} (format: {stream_file['format']})")
                
                # Create streaming response with additional headers containing alternative formats
                streaming_response = create_file_stream_response(file_path)
                
                # Add alternative format URLs in custom headers
                alt_formats = []
                for file_info in result['output_files']:
                    if file_info['format'] != stream_file['format']:
                        alt_formats.append(f"{file_info['format']}:{file_info['url']}")
                
                if alt_formats:
                    streaming_response.headers["X-Alternative-Formats"] = "|".join(alt_formats)
                
                return streaming_response
            else:
                logger.warning(f"Output file not found for streaming: {file_path}")
                # Fall back to JSON response
        
        # Return JSON response (default or fallback)
        return VCResponse(**result)
        
    except ChatterboxAPIError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in VC generation: {e}")
        raise GenerationError(f"VC generation failed: {e}")
    finally:
        # Clean up temp file if it was created
        if temp_input_path and temp_input_path.exists():
            try:
                temp_input_path.unlink()
                logger.debug(f"Cleaned up temp file: {temp_input_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {temp_input_path}: {e}")

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Enhanced health check endpoint with detailed metrics"""
    uptime = time.time() - app_start_time
    
    # Check if models are loaded
    tts_loaded = False
    vc_loaded = False
    try:
        from core_engine import _tts_model, _vc_model
        tts_loaded = _tts_model is not None
        vc_loaded = _vc_model is not None
    except:
        pass
    
    # Get basic metrics
    basic_metrics = get_metrics()
    system_metrics = get_system_metrics()
    
    # Get resource status and warnings
    resource_status = resource_manager.get_resource_status()
    warnings = resource_status.get("warnings", [])
    
    # Get error summary from error tracker
    from resilience import error_tracker
    error_summary = error_tracker.get_error_summary(hours=24)
    
    return HealthResponse(
        status="healthy",
        models_loaded={"tts": tts_loaded, "vc": vc_loaded},
        version="1.8.2",  # Updated for error handling features
        uptime_seconds=uptime,
        metrics=basic_metrics,
        system_info=system_metrics['system'],
        resource_status=resource_status,
        warnings=warnings if warnings else None,
        error_summary=error_summary if error_summary['total_errors'] > 0 else None
    )

@app.get("/api/v1/metrics")
async def get_detailed_metrics():
    """Get detailed system and performance metrics"""
    with logger.operation_timer("get_metrics"):
        return get_system_metrics()

@app.get("/api/v1/config", response_model=ConfigResponse)
async def get_config():
    """Get configuration information"""
    return ConfigResponse(
        tts_defaults=config_manager.get("tts_defaults", {}),
        vc_defaults=config_manager.get("vc_defaults", {}),
        supported_formats=["wav", "mp3", "flac"],
        api_limits={
            "max_text_length": config_manager.get("api.max_text_length", 10000),
            "download_timeout_seconds": config_manager.get("api.download_timeout_seconds", 30)
        }
    )

@app.get("/api/v1/voices", response_model=VoicesResponse)
async def list_voices(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for voice names"),
    folder: Optional[str] = Query(None, description="Filter by folder path")
):
    """List available reference voices with enhanced metadata, pagination, and search"""
    from utils import load_voice_metadata
    import math
    
    voices = []
    
    ref_audio_dir = Path(config_manager.get("paths.reference_audio_dir", "reference_audio"))
    if ref_audio_dir.exists():
        # Supported audio extensions
        audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
        
        for audio_file in ref_audio_dir.rglob("*"):
            if audio_file.is_file() and audio_file.suffix.lower() in audio_extensions:
                relative_path = audio_file.relative_to(ref_audio_dir)
                
                # Load enhanced metadata
                metadata = load_voice_metadata(audio_file)
                
                # Calculate folder path
                folder_path = str(relative_path.parent) if relative_path.parent != Path('.') else None
                
                # Apply folder filter
                if folder and folder_path != folder:
                    continue
                
                # Apply search filter
                if search:
                    search_lower = search.lower()
                    if not (search_lower in metadata.get('name', '').lower() or 
                           search_lower in metadata.get('description', '').lower() or
                           any(search_lower in tag.lower() for tag in metadata.get('tags', []))):
                        continue
                
                voice_metadata = VoiceMetadata(
                    name=metadata.get('name', audio_file.stem),
                    description=metadata.get('description'),
                    duration_seconds=metadata.get('duration_seconds'),
                    sample_rate=metadata.get('sample_rate'),
                    file_size_bytes=metadata.get('file_size_bytes'),
                    format=metadata.get('format'),
                    default_parameters=metadata.get('default_parameters'),
                    tags=metadata.get('tags', []),
                    created_date=metadata.get('created_date'),
                    last_used=metadata.get('last_used'),
                    usage_count=metadata.get('usage_count', 0),
                    folder_path=folder_path
                )
                voices.append(voice_metadata)
    
    # Calculate pagination
    total_voices = len(voices)
    total_pages = math.ceil(total_voices / page_size) if total_voices > 0 else 1
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_voices = voices[start_idx:end_idx]
    
    return VoicesResponse(
        voices=paginated_voices,
        count=len(paginated_voices),
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )

@app.get("/api/v1/resources")
async def get_resource_status():
    """Get current resource usage status"""
    return resource_manager.get_resource_status()

@app.post("/api/v1/cleanup")
async def force_cleanup():
    """Force immediate cleanup operation"""
    return cleanup_scheduler.force_cleanup()

@app.get("/api/v1/cleanup/status")
async def get_cleanup_status():
    """Get cleanup scheduler status and history"""
    return {
        "scheduler": cleanup_scheduler.get_status(),
        "history": cleanup_scheduler.get_history(limit=5)
    }

@app.get("/api/v1/errors/summary", response_model=ErrorSummaryResponse)
async def get_error_summary():
    """Get error summary for the last 24 hours"""
    from resilience import error_tracker
    
    summary = error_tracker.get_error_summary(hours=24)
    recent_errors = error_tracker.get_recent_errors(count=5)
    
    return ErrorSummaryResponse(
        total_errors=summary['total_errors'],
        by_category=summary['by_category'],
        by_severity=summary['by_severity'], 
        by_operation=summary['by_operation'],
        most_frequent=summary['most_frequent'],
        unresolved_count=summary['unresolved_count'],
        recent_errors=recent_errors
    )

@app.get("/api/v1/errors/recent")
async def get_recent_errors(count: int = 10):
    """Get recent errors for debugging"""
    from resilience import error_tracker
    return {
        "recent_errors": error_tracker.get_recent_errors(count=min(count, 50)),
        "total_stored": len(error_tracker.errors)
    }

# Mount Gradio UI
if config_manager.get("ui.enable_ui", True):
    try:
        import gradio as gr
        import Chatter
        
        logger.info("Loading Gradio UI...")
        gradio_app = Chatter.create_interface()
        mount_path = config_manager.get("ui.mount_path", "/ui")
        app = gr.mount_gradio_app(app, gradio_app, path=mount_path)
        logger.info(f"Gradio UI successfully mounted at {mount_path}")
        
    except Exception as e:
        logger.error(f"Failed to mount Gradio UI: {e}")
        logger.info("API will continue to work, but UI will not be available")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with navigation"""
    return {
        "message": "Chatterbox TTS Extended Plus API",
        "version": "1.7.0",
        "endpoints": {
            "api_docs": "/docs",
            "gradio_ui": "/ui",
            "health_check": "/api/v1/health",
            "metrics": "/api/v1/metrics",
            "tts_generation": "/api/v1/tts",
            "voice_conversion": "/api/v1/vc"
        }
    }

if __name__ == "__main__":
    host = config_manager.get("server.host", "127.0.0.1")
    port = config_manager.get("server.port", 7860)
    log_level = config_manager.get("server.log_level", "info").lower()
    
    logger.info("Starting Chatterbox TTS Extended Plus API")
    logger.info(f"Server: {host}:{port}")
    logger.info(f"API Docs: http://{host}:{port}/docs")
    logger.info(f"Gradio UI: http://{host}:{port}/ui")
    logger.info(f"Metrics: http://{host}:{port}/api/v1/metrics")
    
    uvicorn.run(
        "main_api:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=True  # Enable auto-reload for development
    )
