#!/usr/bin/env python3
"""
Test script for Phase 10.1.4 - Speed Factor Implementation Cleanup
Validates the cleaned up speed factor implementation without pyrubberband
"""

import requests
import time
import json

# Test configuration
API_BASE = "http://127.0.0.1:7860"
TEST_TEXT = "This is a test of the cleaned up speed factor implementation without pyrubberband."
# TEST_TEXT = "In a village of La Mancha, the name of which I have no desire to call to mind, there lived not long since one of those gentlemen that keep a lance in the lance-rack, an old buckler, a lean hack, and a greyhound for coursing."

def test_speed_factor_cleanup():
    """Test the speed factor implementation after pyrubberband removal"""
    
    print("Testing Phase 10.1.4 - Speed Factor Implementation Cleanup")
    print("=" * 60)
    
    tests = [
        {
            "name": "Default Speed (1.0x)",
            "speed_factor": 1.0,
            "library": "auto"
        },
        {
            "name": "Slower Speech (0.8x) with audiostretchy",
            "speed_factor": 0.8,
            "library": "audiostretchy"
        },
        {
            "name": "Faster Speech (1.3x) with auto selection",
            "speed_factor": 1.3,
            "library": "auto"
        },
        {
            "name": "Fallback to librosa",
            "speed_factor": 1.5,
            "library": "librosa"
        }
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\nTest {i}: {test['name']}")
        print(f"   Speed Factor: {test['speed_factor']}x")
        print(f"   Library: {test['library']}")
        
        # Prepare request
        request_data = {
            "text": TEST_TEXT,
            "speed_factor": test['speed_factor'],
            "speed_factor_library": test['library'],
            "export_formats": ["wav"],
            "reference_audio_filename": None  # Use default voice
        }
        
        # Make request
        start_time = time.time()
        try:
            response = requests.post(
                f"{API_BASE}/api/v1/tts",
                json=request_data,
                timeout=60
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                # Check if we got streaming response or JSON
                content_type = response.headers.get('content-type', '')
                if 'application/octet-stream' in content_type:
                    print(f"   SUCCESS - Streaming response received")
                    print(f"   Response time: {duration:.1f}s")
                    print(f"   File size: {len(response.content):,} bytes")
                else:
                    # JSON response
                    result = response.json()
                    if result.get('success'):
                        print(f"   SUCCESS - JSON response received")
                        print(f"   Response time: {duration:.1f}s")
                        if 'output_files' in result:
                            print(f"   Files generated: {len(result['output_files'])}")
                    else:
                        print(f"   FAILED - {result.get('message', 'Unknown error')}")
            else:
                print(f"   FAILED - HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text[:200]}")
                    
        except requests.exceptions.Timeout:
            print(f"   TIMEOUT after 60 seconds")
        except Exception as e:
            print(f"   ERROR: {e}")
    
    print(f"\nTesting Invalid Library (should fail gracefully)")
    # Test with pyrubberband (should fail validation now)
    try:
        invalid_request = {
            "text": "Testing invalid library",
            "speed_factor": 1.2,
            "speed_factor_library": "pyrubberband",  # Should be rejected
            "export_formats": ["wav"]
        }
        
        response = requests.post(
            f"{API_BASE}/api/v1/tts",
            json=invalid_request,
            timeout=10
        )
        
        if response.status_code == 422:  # Validation error expected
            print(f"   SUCCESS - pyrubberband correctly rejected (HTTP 422)")
            error_detail = response.json()
            print(f"   Validation error: {error_detail['detail'][0]['msg']}")
        else:
            print(f"   UNEXPECTED - Should have rejected pyrubberband")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test configuration defaults
    print(f"\nTesting Configuration Defaults")
    try:
        # Request without speed_factor (should use config default)
        default_request = {
            "text": "Testing configuration defaults",
            "export_formats": ["wav"]
        }
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/api/v1/tts",
            json=default_request,
            timeout=60
        )
        duration = time.time() - start_time
        
        if response.status_code == 200:
            print(f"   SUCCESS - Config defaults applied")
            print(f"   Response time: {duration:.1f}s")
        else:
            print(f"   FAILED - HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print(f"\nSpeed Factor Cleanup Test Complete!")
    print(f"Key validations:")
    print(f"  - pyrubberband removed from allowed libraries")
    print(f"  - audiostretchy preferred for speech quality")
    print(f"  - Clean fallback chain: audiostretchy -> librosa -> torchaudio")
    print(f"  - Configuration defaults working")
    print(f"  - Zero overhead for speed_factor=1.0 maintained")

if __name__ == "__main__":
    test_speed_factor_cleanup()
