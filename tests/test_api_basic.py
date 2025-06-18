# test_api_basic.py - Basic API testing script

"""
Basic testing script for the Chatterbox TTS Extended Plus API.
This script tests import functionality and basic setup.
For full API testing, the server needs to be running.
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test configuration
        from config import config_manager
        print("[OK] Configuration import successful")
        
        # Test core engine
        from core_engine import engine
        print("[OK] Core engine import successful")
        
        # Test API models
        from api_models import TTSRequest, VCRequest, TTSResponse, VCResponse
        print("[OK] API models import successful")
        
        # Test main API
        import main_api
        print("[OK] Main API import successful")
        
        # Test exceptions
        from exceptions import ChatterboxAPIError, ValidationError
        print("[OK] Exceptions import successful")
        
        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config import config_manager
        
        # Test basic config values
        host = config_manager.get("server.host")
        port = config_manager.get("server.port") 
        print(f"[OK] Server config: {host}:{port}")
        
        # Test paths
        output_dir = config_manager.get("paths.output_dir")
        print(f"[OK] Output directory: {output_dir}")
        
        # Test TTS defaults
        tts_defaults = config_manager.get("tts_defaults", {})
        print(f"[OK] TTS defaults loaded: {len(tts_defaults)} parameters")
        
        return True
    except Exception as e:
        print(f"[FAIL] Configuration test failed: {e}")
        traceback.print_exc()
        return False

def test_directory_structure():
    """Test that required directories exist"""
    print("\nTesting directory structure...")
    
    try:
        from config import config_manager
        
        required_dirs = [
            "paths.output_dir",
            "paths.temp_dir",
            "paths.reference_audio_dir",
            "paths.vc_input_dir"
        ]
        
        for dir_key in required_dirs:
            dir_path = Path(config_manager.get(dir_key))
            if dir_path.exists():
                print(f"[OK] Directory exists: {dir_path}")
            else:
                print(f"[WARN] Directory missing: {dir_path}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Directory test failed: {e}")
        traceback.print_exc()
        return False

def test_api_models():
    """Test API model creation"""
    print("\nTesting API models...")
    
    try:
        from api_models import TTSRequest, VCRequest
        
        # Test TTS request model
        tts_request = TTSRequest(text="Hello world. Here we go again.")
        print(f"[OK] TTS request created: {tts_request.text}")
        
        # Test VC request model
        vc_request = VCRequest(
            input_audio_source="ElevenLabs_2025-06-16T00_38_05_Jamie_gen_sp100_s50_sb75_se0_b_m2.mp3",
            target_voice_source="speaker_en/DAVID-2.mp3"
        )
        print(f"[OK] VC request created: {vc_request.input_audio_source} -> {vc_request.target_voice_source}")
        
        return True
    except Exception as e:
        print(f"[FAIL] API models test failed: {e}")
        traceback.print_exc()
        return False

def test_core_engine_basic():
    """Test core engine basic functionality"""
    print("\nTesting core engine...")
    
    try:
        from core_engine import engine
        
        # Test device detection
        device = engine.device
        print(f"[OK] Device detected: {device}")
        
        # Test models status
        models_status = engine.models_loaded
        print(f"[OK] Models status: {models_status}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Core engine test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all basic tests"""
    print("Chatterbox TTS Extended Plus - Basic API Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_directory_structure,
        test_api_models,
        test_core_engine_basic
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[CRASH] Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("[SUCCESS] All basic tests passed!")
        print("\nNext steps:")
        print("1. Start the API server: python main_api.py")
        print("2. Test endpoints with curl or Postman")
        print("3. Check the health endpoint: GET http://localhost:7860/api/v1/health")
    else:
        print("[FAIL] Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
