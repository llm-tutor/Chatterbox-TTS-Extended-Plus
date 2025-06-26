# main_api.py - FastAPI application entry point

import asyncio
import logging
import time as time_module
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Union, Optional, List

from fastapi import FastAPI, HTTPException, Request, Query, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api_models import (
    TTSRequest, VCRequest, TTSResponse, VCResponse, 
    ErrorResponse, HealthResponse, ConfigResponse,
    VoicesResponse, VoiceInfo, VoiceMetadata, ErrorSummaryResponse,
    VoiceUploadRequest, VoiceUploadResponse, GeneratedFileMetadata, GeneratedFilesResponse,
    VoiceMetadataUpdateRequest, VoiceDeletionResponse, VoiceFolderInfo, VoiceFoldersResponse,
    ConcatRequest, ConcatResponse, MixedConcatSegment, MixedConcatRequest
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

# Direct utils imports for better code visibility (Phase 4)
from utils.voice.metadata import load_voice_metadata, save_voice_metadata, create_voice_metadata_from_upload
from utils.voice.management import validate_voice_file, save_uploaded_voice, delete_voice_file, update_voice_metadata_only
from utils.voice.organization import bulk_delete_voices, get_voice_folder_structure
from utils.outputs.management import scan_generated_files, find_files_by_names, save_generation_metadata
from utils.concatenation.basic import concatenate_audio_files
from utils.concatenation.advanced import concatenate_with_trimming, concatenate_with_mixed_sources, concatenate_with_silence
from utils.concatenation.parsing import parse_concat_files
from utils.files.naming import generate_enhanced_filename

# Setup enhanced logging
logger = get_logger(__name__)

# Track startup time for health endpoint
app_start_time = time_module.time()

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
            
            timestamp = int(time_module.time())
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
    uptime = time_module.time() - app_start_time
    
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


@app.post("/api/v1/voice", response_model=VoiceUploadResponse)
async def upload_voice(
    voice_file: UploadFile = File(..., description="Voice audio file"),
    name: Optional[str] = Form(None, description="Voice name (defaults to filename)"),
    description: Optional[str] = Form(None, description="Voice description"),
    tags: Optional[str] = Form(None, description="Comma-separated voice tags"),
    folder_path: Optional[str] = Form(None, description="Folder organization path"),
    default_parameters: Optional[str] = Form(None, description="JSON string of default TTS parameters"),
    overwrite: bool = Form(False, description="Overwrite existing voice file")
):
    """Upload a new voice file with metadata"""
    from api_models import VoiceMetadata
    import json
    
    try:
        # Read file content
        file_content = await voice_file.read()
        
        # Validate file
        is_valid, error_msg = validate_voice_file(file_content, voice_file.filename)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Parse optional fields
        parsed_tags = []
        if tags:
            parsed_tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        parsed_default_params = {}
        if default_parameters:
            try:
                parsed_default_params = json.loads(default_parameters)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in default_parameters field")
        
        # Use provided name or fallback to filename
        voice_name = name if name else Path(voice_file.filename).stem
        
        # Save file
        success, message, saved_path = save_uploaded_voice(
            file_content=file_content,
            filename=voice_file.filename,
            folder_path=folder_path,
            overwrite=overwrite
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Create metadata
        upload_metadata = {
            'name': voice_name,
            'description': description,
            'tags': parsed_tags,
            'folder_path': folder_path,
            'default_parameters': parsed_default_params
        }
        
        metadata = create_voice_metadata_from_upload(saved_path, upload_metadata)
        
        # Save metadata
        save_voice_metadata(saved_path, metadata)
        
        # Create response
        voice_metadata = VoiceMetadata(**metadata)
        
        return VoiceUploadResponse(
            voice_metadata=voice_metadata,
            filename=saved_path.name,
            message=f"Voice '{voice_name}' uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Voice upload failed: {str(e)}")


@app.delete("/api/v1/voice/{filename}", response_model=VoiceDeletionResponse)
async def delete_voice(
    filename: str,
    confirm: bool = Query(False, description="Confirmation required to delete voice")
):
    """Delete a single voice file and its metadata"""
    
    if not confirm:
        raise HTTPException(status_code=400, detail="Deletion requires confirm=true parameter for safety")
    
    try:
        success, message, deleted_files = delete_voice_file(filename)
        
        if not success:
            raise HTTPException(status_code=404, detail=message)
        
        return VoiceDeletionResponse(
            message=message,
            deleted_files=deleted_files,
            deleted_count=len([f for f in deleted_files if not f.endswith('.json')])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Voice deletion failed: {str(e)}")


@app.delete("/api/v1/voices", response_model=VoiceDeletionResponse)
async def bulk_delete_voices(
    confirm: bool = Query(False, description="Confirmation required to delete voices"),
    folder: Optional[str] = Query(None, description="Delete voices in specific folder"),
    tag: Optional[str] = Query(None, description="Delete voices with specific tag"),
    search: Optional[str] = Query(None, description="Delete voices matching search term"),
    filenames: Optional[str] = Query(None, description="Comma-separated list of filenames to delete")
):
    """Bulk delete voices based on criteria"""
    
    if not confirm:
        raise HTTPException(status_code=400, detail="Bulk deletion requires confirm=true parameter for safety")
    
    # Parse filenames if provided
    filename_list = None
    if filenames:
        filename_list = [name.strip() for name in filenames.split(',') if name.strip()]
    
    try:
        success, message, deleted_files = bulk_delete_voices(
            folder=folder,
            tag=tag,
            search=search,
            filenames=filename_list
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return VoiceDeletionResponse(
            message=message,
            deleted_files=deleted_files,
            deleted_count=len([f for f in deleted_files if not f.endswith('.json')])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk voice deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk voice deletion failed: {str(e)}")


@app.put("/api/v1/voice/{filename}/metadata", response_model=VoiceUploadResponse)
async def update_voice_metadata(
    filename: str,
    metadata_update: VoiceMetadataUpdateRequest
):
    """Update voice metadata without changing the audio file"""
    from api_models import VoiceMetadata
    
    try:
        # Convert request to dict, excluding None values
        updates = metadata_update.model_dump(exclude_unset=True, exclude_none=True)
        
        success, message, updated_metadata = update_voice_metadata_only(filename, updates)
        
        if not success:
            raise HTTPException(status_code=404, detail=message)
        
        # Create response
        voice_metadata = VoiceMetadata(**updated_metadata)
        
        return VoiceUploadResponse(
            voice_metadata=voice_metadata,
            filename=filename,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice metadata update failed: {e}")
        raise HTTPException(status_code=500, detail=f"Voice metadata update failed: {str(e)}")


@app.get("/api/v1/voices/folders", response_model=VoiceFoldersResponse)
async def get_voice_folders():
    """Get voice library folder structure"""
    
    try:
        folder_data = get_voice_folder_structure()
        
        # Convert to response model
        folders = [VoiceFolderInfo(**folder_info) for folder_info in folder_data['folders']]
        
        return VoiceFoldersResponse(
            folders=folders,
            total_folders=folder_data['total_folders'],
            total_voices=folder_data['total_voices']
        )
        
    except Exception as e:
        logger.error(f"Failed to get voice folders: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get voice folders: {str(e)}")


@app.get("/api/v1/outputs", response_model=GeneratedFilesResponse)
async def list_generated_files(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    generation_type: Optional[str] = Query(None, description="Filter by generation type (tts, vc, concat)"),
    search: Optional[str] = Query(None, description="Search in filenames"),
    filenames: Optional[str] = Query(None, description="Comma-separated list of specific filenames to find")
):
    """List generated audio files with metadata, pagination, and search"""
    import math
    
    try:
        outputs_dir = Path(config_manager.get("paths.outputs_dir", "outputs"))
        
        # Handle specific filename lookup
        if filenames:
            filename_list = [name.strip() for name in filenames.split(',') if name.strip()]
            files_metadata = find_files_by_names(outputs_dir, filename_list)
        else:
            # Scan all files
            files_metadata = scan_generated_files(outputs_dir, generation_type)
            
            # Apply search filter
            if search:
                search_lower = search.lower()
                files_metadata = [
                    file_meta for file_meta in files_metadata
                    if search_lower in file_meta['filename'].lower()
                ]
        
        # Calculate pagination
        total_files = len(files_metadata)
        total_pages = max(1, math.ceil(total_files / page_size))
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_files = files_metadata[start_idx:end_idx]
        
        # Convert to response model
        response_files = [GeneratedFileMetadata(**file_meta) for file_meta in paginated_files]
        
        return GeneratedFilesResponse(
            files=response_files,
            count=len(response_files),
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
            total_files=total_files
        )
        
    except Exception as e:
        logger.error(f"Failed to list generated files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list generated files: {str(e)}")


@app.post("/api/v1/concat", response_model=ConcatResponse)
async def concatenate_audio(
    request: ConcatRequest,
    response_mode: str = Query("stream", description="Response mode: 'stream' or 'url'")
):
    """
    Concatenate multiple audio files from the outputs directory
    
    Combines multiple generated audio files into a single file with optional
    level normalization and crossfading between segments.
    """
    start_time = time_module.time()
    try:
        
        outputs_dir = Path(config_manager.get("paths.output_dir", "outputs"))
        if not outputs_dir.exists():
            raise HTTPException(status_code=404, detail="Outputs directory not found")
        
        # Parse the files array to detect silence notation
        parsed_items = parse_concat_files(request.files)
        
        # Check if we have any silence notation (manual silence mode)
        has_manual_silence = any(item["type"] == "silence" for item in parsed_items)
        
        # Validate and resolve file paths (only for actual files, not silence)
        source_files_info = []
        
        for item in parsed_items:
            if item["type"] == "file":
                filename = item["source"]
                file_path = outputs_dir / filename
                if not file_path.exists():
                    raise HTTPException(status_code=404, detail=f"File not found: {filename}")
                
                # Check if it's an audio file
                audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
                if file_path.suffix.lower() not in audio_extensions:
                    raise HTTPException(status_code=400, detail=f"Not an audio file: {filename}")
                
                source_files_info.append({
                    "filename": filename,
                    "size_bytes": file_path.stat().st_size
                })
        
        # Prepare concatenation parameters
        audio_file_count = sum(1 for item in parsed_items if item["type"] == "file")
        silence_count = sum(1 for item in parsed_items if item["type"] == "silence")
        
        concat_params = {
            "file_count": audio_file_count,
            "silence_segments": silence_count,
            "crossfade_ms": request.crossfade_ms,
            "normalize_levels": request.normalize_levels,
            "manual_silence": has_manual_silence
        }
        
        # Include pause parameters only if not using manual silence
        # TODO: We want to  use pause duration between two files without manual silence
        if not has_manual_silence:
            concat_params.update({
                "pause_duration_ms": request.pause_duration_ms,
                "pause_variation_ms": request.pause_variation_ms
            })
        
        # Include trimming parameters
        concat_params.update({
            "trim": request.trim,
            "trim_threshold_ms": request.trim_threshold_ms
        })
        
        # Generate output filenames for each format
        output_files = []
        generated_metadata = {}
        
        for export_format in request.export_formats:
            # Generate enhanced filename
            if request.output_filename:
                # Use custom filename
                base_filename = request.output_filename
            else:
                # Generate timestamp-based filename
                base_filename = generate_enhanced_filename("concat", concat_params, export_format)
            
            # Ensure proper extension
            if not base_filename.endswith(f".{export_format}"):
                if '.' in base_filename:
                    base_filename = base_filename.rsplit('.', 1)[0]
                base_filename = f"{base_filename}.{export_format}"
            
            output_path = outputs_dir / base_filename
            
            # Choose appropriate concatenation method
            if has_manual_silence:
                # Use enhanced mixed-mode concatenation with silence and pause support
                concat_metadata = concatenate_with_silence(
                    parsed_items=parsed_items,
                    output_path=output_path,
                    normalize_levels=request.normalize_levels,
                    crossfade_ms=request.crossfade_ms,
                    outputs_dir=outputs_dir,
                    trim=request.trim,
                    trim_threshold_ms=request.trim_threshold_ms,
                    pause_duration_ms=request.pause_duration_ms,
                    pause_variation_ms=request.pause_variation_ms
                )
            else:
                # Use concatenation with optional trimming
                file_paths = [outputs_dir / item["source"] for item in parsed_items if item["type"] == "file"]
                
                if request.trim:
                    concat_metadata = concatenate_with_trimming(
                        file_paths=file_paths,
                        output_path=output_path,
                        trim=request.trim,
                        trim_threshold_ms=request.trim_threshold_ms,
                        normalize_levels=request.normalize_levels,
                        crossfade_ms=request.crossfade_ms,
                        pause_duration_ms=request.pause_duration_ms,
                        pause_variation_ms=request.pause_variation_ms
                    )
                else:
                    # Use original concatenation with natural pauses
                    concat_metadata = concatenate_audio_files(
                        file_paths=file_paths,
                        output_path=output_path,
                        normalize_levels=request.normalize_levels,
                        crossfade_ms=request.crossfade_ms,
                        pause_duration_ms=request.pause_duration_ms,
                        pause_variation_ms=request.pause_variation_ms
                    )
            
            output_files.append(base_filename)
            
            if export_format == request.export_formats[0]:  # Store metadata once
                generated_metadata = concat_metadata
            
            # Save metadata JSON file
            metadata_to_save = {
                "type": "concat",
                "parameters": {
                    "source_files": request.files,
                    "normalize_levels": request.normalize_levels,
                    "crossfade_ms": request.crossfade_ms,
                    "manual_silence": has_manual_silence,
                    "file_count": audio_file_count,
                    "silence_segments": silence_count,
                    "trim": request.trim,
                    "trim_threshold_ms": request.trim_threshold_ms
                },
                "generation_info": concat_metadata,
                "source_files_info": source_files_info
            }
            
            # Add pause parameters only if not using manual silence
            # TODO: We want to  use pause duration between two files without manual silence
            if not has_manual_silence:
                metadata_to_save["parameters"].update({
                    "pause_duration_ms": request.pause_duration_ms,
                    "pause_variation_ms": request.pause_variation_ms
                })
            
            save_generation_metadata(output_path, metadata_to_save)
        
        # Record operation time
        operation_time_ms = (time_module.time() - start_time) * 1000
        # record_operation_time(operation_time_ms, "concat")  # Temporarily disabled for debugging
        
        # Prepare response
        response_data = ConcatResponse(
            output_files=output_files,
            total_duration_seconds=generated_metadata.get("total_duration_seconds"),
            file_count=audio_file_count,
            processing_time_seconds=generated_metadata.get("processing_time_seconds"),
            metadata=generated_metadata
        )
        
        # Handle response mode
        if response_mode == "stream" and len(output_files) == 1:
            # Stream the first (primary) file
            primary_file = outputs_dir / output_files[0]
            if primary_file.exists():
                def file_streamer():
                    with open(primary_file, "rb") as f:
                        while chunk := f.read(8192):
                            yield chunk
                
                # Determine content type
                content_type = "audio/wav"
                if primary_file.suffix.lower() == ".mp3":
                    content_type = "audio/mpeg"
                elif primary_file.suffix.lower() == ".flac":
                    content_type = "audio/flac"
                
                return StreamingResponse(
                    file_streamer(),
                    media_type=content_type,
                    headers={
                        "Content-Disposition": f"attachment; filename={primary_file.name}"
                    }
                )
        
        # Default: return URL-based response
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Concatenation failed: {e}")
        raise GenerationError(f"Audio concatenation failed: {e}")


@app.post("/api/v1/concat/mixed", response_model=ConcatResponse)
async def concatenate_mixed_audio(
    request_json: str = Form(..., description="JSON string of MixedConcatRequest"),
    uploaded_files: List[UploadFile] = File(default=[], description="Audio files to upload"),
    response_mode: str = Query("stream", description="Response mode: 'stream' or 'url'")
):
    """
    Concatenate audio files from mixed sources (server files + uploads + silence)
    
    Supports combining files from the outputs directory with uploaded files and manual silence.
    Use segments array to specify order and source type for each segment.
    """
    start_time = time_module.time()
    temp_files = []  # Track temporary files for cleanup
    
    try:
        # Parse the JSON request
        import json
        try:
            request_data = json.loads(request_json)
            request = MixedConcatRequest(**request_data)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON in request: {e}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid request format: {e}")
        
        
        outputs_dir = Path(config_manager.get("paths.output_dir", "outputs"))
        temp_dir = Path(config_manager.get("paths.temp_dir", "temp"))
        temp_dir.mkdir(exist_ok=True)
        
        # Validate that uploaded files match the expected upload segments
        upload_segments = [seg for seg in request.segments if seg.type == 'upload']
        max_upload_index = max([seg.index for seg in upload_segments], default=-1)
        
        if max_upload_index >= 0:
            expected_upload_count = max_upload_index + 1
            if len(uploaded_files) != expected_upload_count:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Expected {expected_upload_count} uploaded files, got {len(uploaded_files)}"
                )
        
        # Process uploaded files and save to temp directory
        upload_paths = {}
        for i, uploaded_file in enumerate(uploaded_files):
            # Validate file type
            if not uploaded_file.content_type or not uploaded_file.content_type.startswith('audio/'):
                if not uploaded_file.filename or not any(uploaded_file.filename.lower().endswith(ext) for ext in ['.wav', '.mp3', '.flac', '.ogg', '.m4a']):
                    raise HTTPException(status_code=400, detail=f"Invalid audio file: {uploaded_file.filename}")
            
            # Save uploaded file to temp directory
            file_extension = Path(uploaded_file.filename).suffix if uploaded_file.filename else '.wav'
            temp_filename = f"upload_{i}_{int(time_module.time() * 1000)}{file_extension}"
            temp_path = temp_dir / temp_filename
            
            try:
                with open(temp_path, "wb") as temp_file:
                    content = await uploaded_file.read()
                    temp_file.write(content)
                temp_files.append(temp_path)
                upload_paths[i] = temp_path
                
                logger.info(f"Saved uploaded file {i} as {temp_filename} ({len(content)} bytes)")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to save uploaded file {i}: {e}")
        
        # Check if we have any silence notation (manual silence mode)
        has_manual_silence = any(seg.type == 'silence' for seg in request.segments)
        
        # Validate and collect segment information
        source_files_info = []
        audio_segment_count = 0
        silence_count = 0
        
        for seg in request.segments:
            if seg.type == 'server_file':
                file_path = outputs_dir / seg.source
                if not file_path.exists():
                    raise HTTPException(status_code=404, detail=f"Server file not found: {seg.source}")
                
                # Check if it's an audio file
                audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
                if file_path.suffix.lower() not in audio_extensions:
                    raise HTTPException(status_code=400, detail=f"Not an audio file: {seg.source}")
                
                source_files_info.append({
                    "type": "server_file",
                    "filename": seg.source,
                    "size_bytes": file_path.stat().st_size
                })
                audio_segment_count += 1
                
            elif seg.type == 'upload':
                if seg.index not in upload_paths:
                    raise HTTPException(status_code=400, detail=f"Upload file with index {seg.index} not found")
                
                upload_path = upload_paths[seg.index]
                source_files_info.append({
                    "type": "upload",
                    "index": seg.index,
                    "filename": f"upload_{seg.index}_{upload_path.name}",
                    "size_bytes": upload_path.stat().st_size
                })
                audio_segment_count += 1
                
            elif seg.type == 'silence':
                silence_count += 1
        
        # Prepare metadata for filename generation
        filename_metadata = {
            "file_count": audio_segment_count,
            "silence_segments": silence_count,
            "upload_count": len(uploaded_files),
            "crossfade_ms": request.crossfade_ms,
            "normalize_levels": request.normalize_levels,
            "manual_silence": has_manual_silence
        }
        
        # Include pause parameters only if not using manual silence
        # TODO: We want to  use pause duration between two files without manual silence
        if not has_manual_silence:
            filename_metadata.update({
                "pause_duration_ms": request.pause_duration_ms,
                "pause_variation_ms": request.pause_variation_ms
            })
        
        # Include trimming parameters
        filename_metadata.update({
            "trim": request.trim,
            "trim_threshold_ms": request.trim_threshold_ms
        })
        
        # Generate output filenames for each format
        output_files = []
        generated_metadata = {}
        
        for export_format in request.export_formats:
            # Generate enhanced filename
            if request.output_filename:
                # Use custom filename with timestamp to avoid collisions
                base_filename = f"{request.output_filename}_{int(time_module.time() * 1000)}"
            else:
                # Generate timestamp-based filename
                base_filename = generate_enhanced_filename("mixed", filename_metadata)
            
            # Ensure proper extension
            if not base_filename.endswith(f".{export_format}"):
                if '.' in base_filename:
                    base_filename = base_filename.rsplit('.', 1)[0]
                base_filename = f"{base_filename}.{export_format}"
            
            output_path = outputs_dir / base_filename
            
            # Perform concatenation with mixed sources
            concat_result = concatenate_with_mixed_sources(
                segments=request.segments,
                upload_paths=upload_paths,
                output_path=output_path,
                outputs_dir=outputs_dir,
                normalize_levels=request.normalize_levels,
                crossfade_ms=request.crossfade_ms,
                trim=request.trim,
                trim_threshold_ms=request.trim_threshold_ms,
                pause_duration_ms=request.pause_duration_ms,
                pause_variation_ms=request.pause_variation_ms
            )
            
            output_files.append(base_filename)
            
            if export_format == request.export_formats[0]:  # Store metadata once
                generated_metadata = concat_result
        
        # Save metadata JSON file
        metadata_to_save = {
            "type": "concat",
            "timestamp": generated_metadata.get("timestamp"),
            "parameters": {
                "segments": [seg.model_dump() for seg in request.segments],
                "normalize_levels": request.normalize_levels,
                "crossfade_ms": request.crossfade_ms,
                "manual_silence": has_manual_silence,
                "audio_segment_count": audio_segment_count,
                "silence_segments": silence_count,
                "upload_count": len(uploaded_files),
                "trim": request.trim,
                "trim_threshold_ms": request.trim_threshold_ms
            },
            "generation_info": generated_metadata.get("generation_info", {}),
            "source_files_info": source_files_info
        }
        
        # Add pause parameters only if not using manual silence
        if not has_manual_silence:
            metadata_to_save["parameters"].update({
                "pause_duration_ms": request.pause_duration_ms,
                "pause_variation_ms": request.pause_variation_ms
            })
        
        save_generation_metadata(outputs_dir / output_files[0], metadata_to_save)
        
        # Record operation time
        operation_time_ms = (time_module.time() - start_time) * 1000
        record_operation_time("concatenation_mixed", operation_time_ms)
        
        # Prepare response
        response_data = ConcatResponse(
            output_files=output_files,
            total_duration_seconds=generated_metadata.get("total_duration_seconds"),
            file_count=audio_segment_count,
            processing_time_seconds=generated_metadata.get("processing_time_seconds"),
            metadata=generated_metadata
        )
        
        # Handle response mode
        if response_mode == "stream" and len(output_files) == 1:
            # Stream the first (primary) file
            primary_file = outputs_dir / output_files[0]
            if primary_file.exists():
                # Ensure file is fully written to disk
                import os
                try:
                    # Force file system sync to ensure data is written
                    fd = os.open(str(primary_file), os.O_RDONLY)
                    os.fsync(fd)
                    os.close(fd)
                except Exception as sync_error:
                    logger.warning(f"File sync failed: {sync_error}")
                
                def file_streamer():
                    with open(primary_file, "rb") as f:
                        while chunk := f.read(8192):
                            yield chunk
                
                # Determine content type
                content_type = "audio/wav"
                if primary_file.suffix.lower() == ".mp3":
                    content_type = "audio/mpeg"
                elif primary_file.suffix.lower() == ".flac":
                    content_type = "audio/flac"
                
                return StreamingResponse(
                    file_streamer(),
                    media_type=content_type,
                    headers={
                        "Content-Disposition": f"attachment; filename={primary_file.name}"
                    }
                )
        
        # Default: return URL-based response
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mixed concatenation failed: {e}")
        raise GenerationError(f"Mixed audio concatenation failed: {e}")
    finally:
        # Cleanup temporary files
        for temp_file in temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    logger.debug(f"Cleaned up temp file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")


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
