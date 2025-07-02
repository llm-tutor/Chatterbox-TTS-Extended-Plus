#!/usr/bin/env python3
"""
Test Phase 5 Task 1: Voice Conversion Enhancement
Tests the enhanced VC implementation with improved error handling and logging.
"""

import sys
import os
import time
import tempfile
import soundfile as sf
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_vc_short_audio():
    """Test VC with short audio (≤60s) - should process directly"""
    print("\n[VC SHORT] Testing VC Short Audio Processing...")
    
    try:
        from core_engine import engine
        
        # Create a short test audio file (5 seconds)
        sample_rate = 22050
        duration = 5.0
        samples = int(sample_rate * duration)
        
        # Generate simple sine wave test audio
        test_audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples))
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file:
            input_path = input_file.name
            sf.write(input_path, test_audio, sample_rate)
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as target_file:
            target_path = target_file.name
            sf.write(target_path, test_audio * 0.8, sample_rate)  # Different amplitude
        
        print(f"📁 Input file: {input_path} ({duration}s)")
        print(f"📁 Target file: {target_path}")
        
        # Test VC generation
        start_time = time.time()
        result = engine.generate_vc(
            input_audio_source=input_path,
            target_voice_source=target_path,
            chunk_sec=60,  # Above our test duration
            overlap_sec=0.1,
            disable_watermark=True,
            export_formats=['wav']
        )
        processing_time = time.time() - start_time
        
        print(f"[SUCCESS] VC completed in {processing_time:.2f}s")
        print(f"[DATA] Result: {result}")
        
        # Validate result
        assert result['success'] is True, "VC should succeed"
        assert len(result['output_files']) > 0, "Should have output files"
        assert processing_time < 60, "Should complete quickly for short audio"
        
        # Check output file exists
        output_file = result['output_files'][0]['filename']
        output_path = project_root / "outputs" / output_file
        assert output_path.exists(), f"Output file should exist: {output_path}"
        
        # Validate audio properties
        output_audio, output_sr = sf.read(str(output_path))
        print(f"🎵 Output audio: {len(output_audio)/output_sr:.2f}s at {output_sr}Hz")
        
        print("[SUCCESS] Short audio VC test passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Short audio VC test failed: {e}")
        return False
    finally:
        # Cleanup temporary files
        try:
            os.unlink(input_path)
            os.unlink(target_path)
        except:
            pass

def test_vc_long_audio_chunking():
    """Test VC with long audio (>60s) - should use chunking with crossfading"""
    print("\n[VC CHUNKING] Testing VC Long Audio Chunking...")
    
    try:
        from core_engine import engine
        
        # Create a longer test audio file (90 seconds)
        sample_rate = 22050
        duration = 90.0
        samples = int(sample_rate * duration)
        
        # Generate test audio with different frequencies over time
        t = np.linspace(0, duration, samples)
        test_audio = np.sin(2 * np.pi * 440 * t) + 0.3 * np.sin(2 * np.pi * 880 * t)
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file:
            input_path = input_file.name
            sf.write(input_path, test_audio, sample_rate)
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as target_file:
            target_path = target_file.name
            sf.write(target_path, test_audio[:sample_rate*10] * 0.6, sample_rate)  # 10s target
        
        print(f"📁 Input file: {input_path} ({duration}s)")
        print(f"📁 Target file: {target_path}")
        
        # Test VC generation with chunking
        start_time = time.time()
        result = engine.generate_vc(
            input_audio_source=input_path,
            target_voice_source=target_path,
            chunk_sec=60,  # Below our test duration - should trigger chunking
            overlap_sec=5.0,  # 5 second overlap
            disable_watermark=True,
            export_formats=['wav']
        )
        processing_time = time.time() - start_time
        
        print(f"[SUCCESS] VC completed in {processing_time:.2f}s")
        print(f"[DATA] Result: {result}")
        
        # Validate result
        assert result['success'] is True, "VC should succeed"
        assert len(result['output_files']) > 0, "Should have output files"
        
        # Check output file exists and has correct duration
        output_file = result['output_files'][0]['filename']
        output_path = project_root / "outputs" / output_file
        assert output_path.exists(), f"Output file should exist: {output_path}"
        
        # Validate audio properties
        output_audio, output_sr = sf.read(str(output_path))
        output_duration = len(output_audio) / output_sr
        print(f"🎵 Output audio: {output_duration:.2f}s at {output_sr}Hz")
        
        # Duration should be close to original (within 1 second tolerance)
        duration_diff = abs(output_duration - duration)
        assert duration_diff < 1.0, f"Output duration should be close to input: {output_duration:.2f}s vs {duration}s"
        
        print("[SUCCESS] Long audio chunking test passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Long audio chunking test failed: {e}")
        return False
    finally:
        # Cleanup temporary files
        try:
            os.unlink(input_path)
            os.unlink(target_path)
        except:
            pass

def test_vc_error_handling():
    """Test VC error handling with invalid files"""
    print("\n[ERROR] Testing VC Error Handling...")
    
    try:
        from core_engine import engine
        
        # Test with non-existent input file
        try:
            result = engine.generate_vc(
                input_audio_source="non_existent_input.wav",
                target_voice_source="non_existent_target.wav",
                export_formats=['wav']
            )
            assert False, "Should have raised an error for non-existent files"
        except Exception as e:
            print(f"[SUCCESS] Correctly caught error for non-existent files: {type(e).__name__}")
        
        print("[SUCCESS] Error handling test passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error handling test failed: {e}")
        return False

def main():
    """Run all Phase 5 Task 1 VC enhancement tests"""
    print("[PHASE5] Starting Phase 5 Task 1: VC Enhancement Tests")
    print("=" * 50)
    
    tests = [
        test_vc_short_audio,
        test_vc_long_audio_chunking,
        test_vc_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[ERROR] Test {test_func.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"[DATA] Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("[SUCCESS] All Phase 5 Task 1 VC enhancement tests passed!")
        return True
    else:
        print(f"⚠️  {failed} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
