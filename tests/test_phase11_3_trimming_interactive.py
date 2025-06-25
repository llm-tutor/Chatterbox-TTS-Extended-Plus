#!/usr/bin/env python3
"""
Test file for Phase 11.3 Audio Trimming System
Interactive test for concat API with trimming functionality

This test demonstrates both stream mode (saves file) and URL mode (returns JSON)
with manual silence insertion and trimming parameters.
"""

import requests
import json
import time
from pathlib import Path
import os

# Configuration
API_BASE = "http://127.0.0.1:7860"
TEST_MEDIA_DIR = Path("tests/media")
OUTPUTS_DIR = Path("outputs")

def setup_test_environment():
    """Ensure test media directory exists"""
    TEST_MEDIA_DIR.mkdir(exist_ok=True)
    print(f"Test media directory: {TEST_MEDIA_DIR.absolute()}")
    print(f"Generated files will be saved to: {OUTPUTS_DIR.absolute()}")

def test_concat_trimming_stream_mode():
    """Test concatenation with trimming in stream mode (saves file directly)"""
    
    print("\n" + "="*60)
    print("TEST 1: Concatenation with Trimming - STREAM MODE")
    print("="*60)
    
    # Test files with manual silence insertion
    test_files = [
        "(1s)",  # 1 second opening silence
        "tts_2025-06-20_210501_416770_temp0.75_seed42.wav",  # sample rate: 24 kHz sample size: 32 bit
        "(300ms)",  # 800ms pause between segments # reduced to see trim
        "tts_2025-06-23_215032_224288_temp0.75_speed0.8.wav",  # 'la mancha' sample rate: 24 kHz sample size: 64 bit
        "(500ms)",  # 1.2 second dramatic pause # reduced to see trim
        "tts_2025-06-20_210538_684349_temp0.75_seed42.wav",  # sample rate: 24 kHz sample size: 32 bit
        "(500ms)"  # 500ms closing silence
    ]
    
    payload = {
        "files": test_files,
        "trim": True,
        "trim_threshold_ms": 200,
        "export_formats": ["wav"],
        "normalize_levels": True,
        "crossfade_ms": 100,
        "response_mode": "stream"  # Direct file download
    }
    
    print(f"📋 Test Configuration:")
    print(f"   Files: {len([f for f in test_files if not f.startswith('(')])} audio files")
    print(f"   Silence segments: {len([f for f in test_files if f.startswith('(')])}")
    print(f"   Trimming: {payload['trim']} (threshold: {payload['trim_threshold_ms']}ms)")
    print(f"   Crossfade: {payload['crossfade_ms']}ms")
    print(f"   Normalize: {payload['normalize_levels']}")
    
    print(f"\n🔄 Making request to {API_BASE}/api/v1/concat...")
    start_time = time.time()
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/concat", json=payload, stream=True)
        request_time = time.time() - start_time
        
        print(f"📊 Response received in {request_time:.2f}s")
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            # Extract filename from Content-Disposition header
            content_disposition = response.headers.get('content-disposition', '')
            filename = 'concat_trimming_test_stream_la_mancha01.wav'
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')
            
            # Save the file to tests/media
            output_path = TEST_MEDIA_DIR / filename
            
            print(f"💾 Saving audio file to: {output_path}")
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = output_path.stat().st_size
            print(f"✅ STREAM MODE TEST SUCCESSFUL")
            print(f"   Saved file: {filename}")
            print(f"   File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            print(f"   Location: {output_path}")
            
            return True
            
        else:
            print(f"❌ STREAM MODE TEST FAILED")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ STREAM MODE TEST ERROR: {e}")
        return False

def test_concat_trimming_url_mode():
    """Test concatenation with trimming in URL mode (returns JSON with metadata)"""
    
    print("\n" + "="*60)
    print("TEST 2: Concatenation with Trimming - URL MODE")
    print("="*60)
    
    # Different test configuration for URL mode
    test_files = [
        "(2s)",  # 2 second opening
        "tts_2025-06-20_210501_416770_temp0.75_seed42.wav",
        "(1.5s)",  # 1.5 second pause
        "tts_2025-06-20_210514_046499_temp0.75_seed42.wav",
        "(1s)",  # 1 second pause
        "tts_2025-06-20_210538_684349_temp0.75_seed42.wav"
        # No closing silence
    ]
    
    payload = {
        "files": test_files,
        "trim": True,
        "trim_threshold_ms": 150,  # More aggressive trimming
        "export_formats": ["wav", "mp3"],  # Multiple formats
        "normalize_levels": True,
        "response_mode": "url"  # JSON response with file info
    }
    
    print(f"📋 Test Configuration:")
    print(f"   Files: {len([f for f in test_files if not f.startswith('(')])} audio files")
    print(f"   Silence segments: {len([f for f in test_files if f.startswith('(')])}")
    print(f"   Trimming: {payload['trim']} (threshold: {payload['trim_threshold_ms']}ms)")
    print(f"   Export formats: {payload['export_formats']}")
    print(f"   Normalize: {payload['normalize_levels']}")
    
    print(f"\n🔄 Making request to {API_BASE}/api/v1/concat?response_mode=url...")
    start_time = time.time()
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/concat?response_mode=url", json=payload)
        request_time = time.time() - start_time
        
        print(f"📊 Response received in {request_time:.2f}s")
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ URL MODE TEST SUCCESSFUL")
            print(f"\n📄 Response Metadata:")
            print(f"   Output files: {result.get('output_files', [])}")
            
            gen_info = result.get('generation_info', {})
            print(f"\n🔧 Generation Details:")
            print(f"   Duration: {gen_info.get('total_duration_seconds', 0):.2f}s")
            print(f"   Processing time: {gen_info.get('total_processing_time_seconds', 0):.2f}s")
            print(f"   File count: {gen_info.get('file_count', 0)}")
            print(f"   Silence segments: {gen_info.get('silence_segments', 0)}")
            
            print(f"\n✂️  Trimming Results:")
            print(f"   Trim applied: {gen_info.get('trim_applied', False)}")
            print(f"   Files trimmed: {gen_info.get('files_trimmed', 0)}")
            print(f"   Files not trimmed: {gen_info.get('files_not_trimmed', 0)}")
            print(f"   Total silence removed: {gen_info.get('total_silence_removed_seconds', 0):.3f}s")
            
            # Show the enhanced filename
            output_files = result.get('output_files', [])
            if output_files:
                print(f"\n📝 Enhanced Filename Analysis:")
                filename = output_files[0]
                print(f"   Filename: {filename}")
                
                # Parse filename components
                if 'trim' in filename:
                    print(f"   ✅ Contains trim parameter")
                if 'sil' in filename:
                    print(f"   ✅ Contains silence count")
                if 'leveled' in filename:
                    print(f"   ✅ Contains normalization flag")
                
                print(f"\n💡 Manual Check:")
                print(f"   Look for these files in outputs/ directory:")
                for file in output_files:
                    print(f"   - {file}")
            
            return True
            
        else:
            print(f"❌ URL MODE TEST FAILED")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ URL MODE TEST ERROR: {e}")
        return False

def test_parameter_validation():
    """Test trimming parameter validation"""
    
    print("\n" + "="*60)
    print("TEST 3: Parameter Validation")
    print("="*60)
    
    # Test invalid trim threshold (too low)
    invalid_payload = {
        "files": ["tts_2025-06-20_210501_416770_temp0.75_seed42.wav"],
        "trim": True,
        "trim_threshold_ms": 25,  # Below minimum (50)
        "export_formats": ["wav"],
        "response_mode": "url"
    }
    
    print("🔍 Testing invalid trim_threshold_ms (25ms, below minimum 50ms)...")
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/concat?response_mode=url", json=invalid_payload)
        
        if response.status_code == 422:  # Validation error expected
            print("✅ VALIDATION TEST SUCCESSFUL")
            print("   Correctly rejected invalid trim_threshold_ms")
            return True
        else:
            print(f"❌ VALIDATION TEST FAILED")
            print(f"   Expected 422, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ VALIDATION TEST ERROR: {e}")
        return False

def main():
    """Run all trimming tests"""
    
    print("🎯 Phase 11.3 Audio Trimming System - Interactive Test")
    print("=" * 60)
    print("This test demonstrates the new trimming functionality with:")
    print("• Manual silence insertion: (1s), (800ms), etc.")
    print("• Audio trimming with configurable thresholds")
    print("• Both stream mode (saves file) and URL mode (returns JSON)")
    print("• Enhanced filename generation with trim parameters")
    print()
    
    setup_test_environment()
    
    # Check if API is available
    try:
        health_response = requests.get(f"{API_BASE}/api/v1/health", timeout=5)
        if health_response.status_code != 200:
            print(f"❌ API not available at {API_BASE}")
            print("   Please ensure the server is running with: python main_api.py")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API at {API_BASE}")
        print(f"   Error: {e}")
        print("   Please ensure the server is running with: python main_api.py")
        return
    
    print("🟢 API server is available\n")
    
    # Run tests
    results = []
    
    results.append(test_concat_trimming_stream_mode())
    results.append(test_concat_trimming_url_mode())
    results.append(test_parameter_validation())
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\n📁 Files generated:")
        print(f"   • Stream mode file saved to: {TEST_MEDIA_DIR}")
        print(f"   • URL mode files saved to: {OUTPUTS_DIR}")
        print("\n🎵 You can now manually test the audio files to verify quality!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n💡 Manual Testing Notes:")
    print("• Listen to the generated files to verify audio quality")
    print("• Check that silence insertion worked correctly")
    print("• Verify that trimming removed appropriate silence")
    print("• Compare stream vs URL mode outputs")

if __name__ == "__main__":
    main()
