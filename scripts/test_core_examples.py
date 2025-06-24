#!/usr/bin/env python3
"""
Core Examples Test Script
Tier 1 Testing: Quick validation during implementation phase closing

Purpose: Validate essential functionality in 2-3 minutes maximum
Scope: Universal examples that work on any setup without specific voice file requirements
Usage: Routine development validation, implementation protocol, CI/CD integration
"""

import requests
import sys
import time
import json


def print_progress(message, prefix="[CORE]"):
    """Print progress message with consistent formatting (no Unicode emojis)"""
    print(f"{prefix} {message}")


def format_duration(seconds):
    """Format duration for display"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"


def test_core_examples():
    """
    Execute core validation tests
    Target: 2-3 minutes maximum execution time
    """
    api_base = "http://127.0.0.1:7860"  # Updated to match your server
    results = []
    total_start_time = time.time()
    
    print_progress("Starting Core Validation (Tier 1 Testing)")
    print_progress("Target completion time: 2-3 minutes")
    print(f"API Base: {api_base}")
    print("-" * 60)
    
    # Core tests - designed for universal compatibility
    core_tests = [
        # === Instant responses (non-generative) ===
        {
            "name": "Health Check",
            "description": "API health and readiness",
            "method": "GET",
            "url": f"{api_base}/api/v1/health",
            "expected_status": 200,
            "timeout": 10,
            "category": "health"
        },
        {
            "name": "List Voices",
            "description": "Available reference voices",
            "method": "GET", 
            "url": f"{api_base}/api/v1/voices",
            "expected_status": 200,
            "timeout": 10,
            "category": "listing"
        },
        {
            "name": "List Outputs",
            "description": "Generated audio files",
            "method": "GET",
            "url": f"{api_base}/api/v1/outputs", 
            "expected_status": 200,
            "timeout": 10,
            "category": "listing"
        },
        
        # === Generation tests (no specific voice file requirements) ===
        {
            "name": "Basic TTS",
            "description": "Text-to-speech without reference voice",
            "method": "POST",
            "url": f"{api_base}/api/v1/tts",
            "json": {
                "text": "Hello, this is a core validation test for the Chatterbox TTS system.",
                "export_formats": ["wav"]
            },
            "expected_status": 200,
            "timeout": 60,  # TTS generation takes time
            "category": "generation"
        },
        {
            "name": "Basic VC",
            "description": "Voice conversion using existing project files",
            "method": "POST",
            "url": f"{api_base}/api/v1/vc",
            "json": {
                "input_audio_source": "test_inputs/chatterbox-hello_quick_brown.wav",
                "target_voice_source": "test_voices/linda_johnson_01.mp3",
                "export_formats": ["wav"]
            },
            "expected_status": 200,
            "timeout": 60,  # VC generation takes time
            "category": "generation"
        },
        
        # === Error demonstration ===
        {
            "name": "Error Demo",
            "description": "Non-existent endpoint handling",
            "method": "GET",
            "url": f"{api_base}/api/v1/nonexistent",
            "expected_status": 404,  # Not found
            "timeout": 10,
            "category": "error_handling"
        }
    ]
    
    # Execute tests
    for i, test in enumerate(core_tests, 1):
        progress_msg = f"[{i}/{len(core_tests)}] {test['name']}"
        print_progress(progress_msg)
        print(f"    {test['description']}")
        
        try:
            start_time = time.time()
            
            # Make request based on method
            if test['method'] == 'GET':
                response = requests.get(
                    test['url'], 
                    timeout=test['timeout']
                )
            elif test['method'] == 'POST':
                response = requests.post(
                    test['url'],
                    json=test['json'],
                    timeout=test['timeout']
                )
            
            elapsed = time.time() - start_time
            
            # Check result
            if response.status_code == test['expected_status']:
                print(f"    [PASS] ({response.status_code}) - {format_duration(elapsed)}")
                
                # Parse response if JSON (avoid detailed output for core validation)
                try:
                    response_data = response.json()
                    if test['category'] == 'generation' and 'message' in response_data:
                        print(f"    Generated: {response_data.get('message', 'Audio file')}")
                    elif test['category'] == 'listing' and isinstance(response_data, list):
                        print(f"    Found: {len(response_data)} items")
                except:
                    pass  # Not JSON or parsing failed, continue
                
                results.append(True)
            else:
                print(f"    [FAIL] ({response.status_code}) - {format_duration(elapsed)}")
                print(f"    Error: {response.text[:100]}...")
                results.append(False)
                
        except requests.exceptions.Timeout:
            print(f"    [TIMEOUT] - Request exceeded {test['timeout']}s timeout")
            results.append(False)
        except requests.exceptions.ConnectionError:
            print(f"    [CONNECTION ERROR] - Cannot reach API server")
            print(f"    Check if server is running at {api_base}")
            results.append(False)
        except Exception as e:
            print(f"    [ERROR]: {e}")
            results.append(False)
        
        print()  # Empty line for readability
    
    # Summary
    total_elapsed = time.time() - total_start_time
    passed = sum(results)
    total = len(results)
    
    print("=" * 60)
    print_progress("CORE VALIDATION SUMMARY")
    print(f"Total Time: {format_duration(total_elapsed)}")
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    # Time target validation
    if total_elapsed <= 180:  # 3 minutes
        print_progress("Time Target: ACHIEVED (within 3 minutes)")
    else:
        print_progress(f"Time Target: EXCEEDED by {format_duration(total_elapsed - 180)}")
    
    # Final result
    if passed == total:
        print_progress("RESULT: ALL CORE TESTS PASSED")
        if total_elapsed <= 180:
            print_progress("Core validation ready for implementation protocol use")
        return 0
    else:
        print_progress(f"RESULT: {total - passed} TESTS FAILED")
        print_progress("Core validation issues detected - investigate before proceeding")
        return 1


def main():
    """Main entry point with argument handling"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print(__doc__)
        print("\nUsage:")
        print("  python test_core_examples.py")
        print("\nExit codes:")
        print("  0 - All tests passed")
        print("  1 - Some tests failed")
        return 0
    
    return test_core_examples()


if __name__ == '__main__':
    sys.exit(main())
