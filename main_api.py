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
    ErrorResponse, HealthResponse, ConfigResponse, VoicesResponse, VoiceInfo
)
from core_engine import engine
from config import config_manager
from exceptions import (
    ChatterboxAPIError, ValidationError, ResourceError, 
    ModelLoadError, GenerationError
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
        dir_path.mkdir(exist_ok=True, parents=True)
        logger.info(f"Ensured directory exists: {dir_path}")
    
    # Preload models if configured
    if config_manager.get("models.preload_models", True):
        try:
            logger.info("Preloading models...")
            await engine.load_tts_model()
            await engine.load_vc_model()
            logger.info("Models preloaded successfully")
        except Exception as e:
            logger.warning(f"Could not preload models: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    engine.cleanup_temp_files()

# Create FastAPI app
app = FastAPI(
    title="Chatterbox TTS Extended Plus API",
    description="API for Text-to-Speech and Voice Conversion",
    version="1.2.0",
    lifespan=lifespan
)

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
outputs_dir.mkdir(exist_ok=True, parents=True)
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
        logger.info(f"TTS request for text: {request.text[:50]}...")
        result = await engine.generate_tts(**request.dict())
        logger.info(f"TTS generation completed successfully")
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
        logger.info(f"VC request: {request.input_audio_source} -> {request.target_voice_source}")
        result = await engine.generate_vc(**request.dict())
        logger.info(f"VC generation completed successfully")
        return VCResponse(**result)
    except ChatterboxAPIError:
        raise  # Let the exception handlers deal with these
    except Exception as e:
        logger.error(f"Unexpected error in VC generation: {e}")
        raise GenerationError(f"VC generation failed: {e}")

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - app_start_time
    return HealthResponse(
        status="healthy",
        models_loaded=engine.models_loaded.copy(),
        version="1.2.0",
        uptime_seconds=uptime
    )

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

# Mount Gradio UI (placeholder for Phase 5)
if config_manager.get("ui.enable_ui", True):
    try:
        # TODO: Import and mount Gradio app in Phase 5
        # import Chatter
        # gradio_app = Chatter.create_interface()
        # app = gr.mount_gradio_app(app, gradio_app, path="/ui")
        logger.info("Gradio UI mounting will be implemented in Phase 5")
    except Exception as e:
        logger.warning(f"Could not mount Gradio UI: {e}")

if __name__ == "__main__":
    host = config_manager.get("server.host", "127.0.0.1")
    port = config_manager.get("server.port", 7860)
    log_level = config_manager.get("server.log_level", "info").lower()
    
    logger.info(f"Starting server at {host}:{port}")
    uvicorn.run(
        "main_api:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=True  # Remove for production
    )
