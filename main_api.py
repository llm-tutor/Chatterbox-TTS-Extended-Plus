# main_api.py - FastAPI application entry point

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api_models import (
    TTSRequest, VCRequest, TTSResponse, VCResponse, 
    ErrorResponse, HealthResponse, ConfigResponse,
    VoicesResponse, VoiceInfo
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
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    engine_sync.cleanup_temp_files()

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
async def generate_tts(request: TTSRequest):
    """Generate Text-to-Speech audio"""
    try:
        # Convert request to dict and call synchronous method
        request_dict = request.model_dump()
        
        # Run the synchronous TTS generation in thread pool for FastAPI compatibility
        def run_tts():
            return engine_sync.generate_tts(**request_dict)
        
        # Use run_in_executor for non-blocking FastAPI operation
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_tts)
        
        return TTSResponse(**result)
    except ChatterboxAPIError:
        raise  # Let the exception handlers deal with these
    except Exception as e:
        logger.error(f"Unexpected error in TTS generation: {e}")
        raise GenerationError(f"TTS generation failed: {e}")

@app.post("/api/v1/vc", response_model=VCResponse)
async def generate_vc(request: VCRequest):
    """Generate Voice Conversion"""
    try:
        # Convert request to dict and call synchronous method
        request_dict = request.model_dump()
        
        # Run the synchronous VC generation in thread pool for FastAPI compatibility
        def run_vc():
            return engine_sync.generate_vc(**request_dict)
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_vc)
        
        return VCResponse(**result)
    except ChatterboxAPIError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in VC generation: {e}")
        raise GenerationError(f"VC generation failed: {e}")

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
    
    return HealthResponse(
        status="healthy",
        models_loaded={"tts": tts_loaded, "vc": vc_loaded},
        version="1.7.0",
        uptime_seconds=uptime,
        metrics=basic_metrics,
        system_info=system_metrics['system']
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
async def list_voices():
    """List available reference voices"""
    voices = []
    
    ref_audio_dir = Path(config_manager.get("paths.reference_audio_dir", "reference_audio"))
    if ref_audio_dir.exists():
        # Supported audio extensions
        audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
        
        for audio_file in ref_audio_dir.rglob("*"):
            if audio_file.is_file() and audio_file.suffix.lower() in audio_extensions:
                relative_path = audio_file.relative_to(ref_audio_dir)
                
                # Get file info
                try:
                    file_size = audio_file.stat().st_size
                except:
                    file_size = None
                
                voices.append(VoiceInfo(
                    path=str(relative_path),
                    name=audio_file.stem,
                    size=file_size
                ))
    
    return VoicesResponse(voices=voices, count=len(voices))

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
        reload=False
    )
