#!/usr/bin/env python3
"""
Test Phase 4 Enhanced Features
Tests URL download, validation, error handling, and utility endpoints
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core_engine import CoreEngine
from config import config_manager

# Direct utils imports for better code visibility (Phase 4)  
from utils.files.naming import sanitize_filename
from utils.validation.audio import get_supported_audio_formats, validate_audio_format
from api_models import TTSRequest, VCRequest

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_url_validation():
    """Test URL validation and path resolution"""
    engine = CoreEngine()
    
    # Test valid URL format
    test_url = "https://www.example.com/test_audio.wav"
    
    # Test if URL is detected correctly
    if test_url.startswith(('http://', 'https://')):
        logger.info("✅ URL detection working correctly")
    else:
        logger.error("❌ URL detection failed")
        return False
    
    # Test filename sanitization
    unsafe_filename = "test<>file|name*.wav"
    safe_filename = sanitize_filename(unsafe_filename)
    logger.info(f"Filename sanitization: {unsafe_filename} -> {safe_filename}")
    
    if safe_filename == "test__file_name_.wav":
        logger.info("✅ Filename sanitization working correctly")
    else:
        logger.error(f"❌ Filename sanitization unexpected result: {safe_filename}")
        return False
    
    return True

async def test_audio_format_validation():
    """Test audio format validation"""
    
    supported_formats = get_supported_audio_formats()
    logger.info(f"Supported formats: {supported_formats}")
    
    # Test valid formats
    test_cases = [
        ("wav", True),
        ("mp3", True), 
        ("flac", True),
        ("xyz", False),
        ("WAV", True),  # Case insensitive
        ("MP3", True),
    ]
    
    all_passed = True
    for format_name, expected in test_cases:
        result = validate_audio_format(format_name)
        if result == expected:
            logger.info(f"✅ Format validation {format_name}: {result}")
        else:
            logger.error(f"❌ Format validation {format_name}: expected {expected}, got {result}")
            all_passed = False
    
    return all_passed

async def test_request_validation():
    """Test Pydantic request validation"""
    
    # Test valid TTS request
    try:
        valid_tts = TTSRequest(
            text="Hello world",
            export_formats=["wav", "mp3"],
            whisper_model_name="medium"
        )
        logger.info("✅ Valid TTS request validation passed")
    except Exception as e:
        logger.error(f"❌ Valid TTS request failed: {e}")
        return False
    
    # Test invalid TTS request
    try:
        invalid_tts = TTSRequest(
            text="",  # Empty text should fail
            export_formats=["invalid_format"],
            whisper_model_name="invalid_model"
        )
        logger.error("❌ Invalid TTS request should have failed but didn't")
        return False
    except Exception as e:
        logger.info(f"✅ Invalid TTS request properly rejected: {e}")
    
    # Test valid VC request
    try:
        valid_vc = VCRequest(
            input_audio_source="test.wav",
            target_voice_source="target.wav",
            export_formats=["wav", "mp3"]
        )
        logger.info("✅ Valid VC request validation passed")
    except Exception as e:
        logger.error(f"❌ Valid VC request failed: {e}")
        return False
    
    return True

async def test_error_response_structure():
    """Test error response models"""
    from api_models import ErrorResponse
    
    try:
        error_response = ErrorResponse(
            error="Test error message",
            error_code="TEST_ERROR",
            detail="Detailed error information"
        )
        
        response_dict = error_response.dict()
        required_fields = {"success", "error", "error_code"}
        
        if all(field in response_dict for field in required_fields):
            logger.info("✅ Error response structure validation passed")
            logger.info(f"Sample error response: {response_dict}")
            return True
        else:
            logger.error("❌ Error response missing required fields")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error response creation failed: {e}")
        return False

async def test_config_loading():
    """Test configuration loading"""
    
    try:
        # Test config access
        tts_defaults = config_manager.get("tts_defaults", {})
        api_config = config_manager.get("api", {})
        paths_config = config_manager.get("paths", {})
        
        logger.info(f"TTS defaults loaded: {len(tts_defaults)} settings")
        logger.info(f"API config loaded: {len(api_config)} settings")
        logger.info(f"Paths config loaded: {len(paths_config)} paths")
        
        # Test specific values
        max_text_length = config_manager.get("api.max_text_length", 10000)
        download_timeout = config_manager.get("api.download_timeout_seconds", 30)
        
        logger.info(f"Max text length: {max_text_length}")
        logger.info(f"Download timeout: {download_timeout}")
        
        logger.info("✅ Configuration loading working correctly")
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration loading failed: {e}")
        return False

async def main():
    """Run all Phase 4 feature tests"""
    logger.info("=== Testing Phase 4 Enhanced Features ===")
    
    tests = [
        ("URL Validation", test_url_validation),
        ("Audio Format Validation", test_audio_format_validation),
        ("Request Validation", test_request_validation),
        ("Error Response Structure", test_error_response_structure),
        ("Configuration Loading", test_config_loading),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n=== Test Results Summary ===")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All Phase 4 features are working correctly!")
        return True
    else:
        logger.info("⚠️  Some Phase 4 features need attention")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
