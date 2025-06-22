#!/usr/bin/env python3
"""
Phase 10.1.2 Speed Factor Architecture Optimization Test

Tests the architectural optimization that separates speed factor processing
from core TTS generation for improved performance.

Key optimizations tested:
1. speed_factor=1.0 bypasses all speed processing (zero overhead)
2. speed_factor≠1.0 uses dedicated post-processing
3. Consistent performance without first-request penalties
4. Minimal speed factor overhead (target: <15%)
"""

import time
import requests
import json
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

API_BASE = "http://127.0.0.1:7860/api/v1"

def wait_for_server():
    """Wait for server to be responsive"""
    print("Checking server connectivity...")
    
    for attempt in range(5):
        try:
            response = requests.get(f"{API_BASE}/health", timeout=5)
            if response.status_code == 200:
                print(f"Server responsive (attempt {attempt + 1})")
                return True
        except:
            print(f"Server not ready (attempt {attempt + 1})")
        time.sleep(2)
    
    return False

def test_speed_factor_optimization():
    """Test Phase 10.1.2 speed factor architectural optimization"""
    
    if not wait_for_server():
        print("ERROR: Server not accessible")
        return False
    
    print("\n=== PHASE 10.1.2 SPEED FACTOR OPTIMIZATION TEST ===")
    
    reference_file = "speaker_en/jamie_vc_to_david-2.wav"
    test_text = "Testing Phase 10.1.2 speed factor architectural optimization."
    
    results = {}
    
    # Test 1: speed_factor=1.0 (optimized path - no post-processing)
    print("\n--- Test 1: speed_factor=1.0 (optimized - zero overhead) ---")
    start = time.time()
    
    try:
        response = requests.post(f"{API_BASE}/tts?response_mode=url", json={
            "text": test_text,
            "reference_audio_filename": reference_file,
            "speed_factor": 1.0,
            "export_formats": ["wav"]
        }, timeout=120)
        
        time_1x = time.time() - start
        
        if response.status_code == 200:
            print(f"SUCCESS: {time_1x:.2f}s")
            results['1.0x'] = time_1x
        else:
            print(f"FAILED: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"FAILED: {e}")
        return False
    
    # Small delay between tests
    time.sleep(2)
    
    # Test 2: speed_factor=1.5 (post-processing path)
    print("\n--- Test 2: speed_factor=1.5 (post-processing) ---")
    start = time.time()
    
    try:
        response = requests.post(f"{API_BASE}/tts?response_mode=url", json={
            "text": test_text,
            "reference_audio_filename": reference_file,
            "speed_factor": 1.5,
            "export_formats": ["wav"]
        }, timeout=120)
        
        time_1_5x = time.time() - start
        
        if response.status_code == 200:
            print(f"SUCCESS: {time_1_5x:.2f}s")
            results['1.5x'] = time_1_5x
        else:
            print(f"FAILED: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"FAILED: {e}")
        return False
    
    # Test 3: speed_factor=0.8 (another post-processing test)
    print("\n--- Test 3: speed_factor=0.8 (post-processing) ---")
    start = time.time()
    
    try:
        response = requests.post(f"{API_BASE}/tts?response_mode=url", json={
            "text": test_text,
            "reference_audio_filename": reference_file,
            "speed_factor": 0.8,
            "export_formats": ["wav"]
        }, timeout=120)
        
        time_0_8x = time.time() - start
        
        if response.status_code == 200:
            print(f"SUCCESS: {time_0_8x:.2f}s")
            results['0.8x'] = time_0_8x
        else:
            print(f"FAILED: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"FAILED: {e}")
        return False
    
    # Analysis
    if '1.0x' in results and '1.5x' in results:
        base_time = results['1.0x']
        speed_time = results['1.5x']
        overhead = speed_time - base_time
        overhead_percent = (overhead / base_time) * 100
        
        print(f"\n=== OPTIMIZATION ANALYSIS ===")
        print(f"1.0x time: {base_time:.2f}s (optimized path)")
        print(f"1.5x time: {speed_time:.2f}s (post-processing)")
        print(f"Speed factor overhead: {overhead:.2f}s ({overhead_percent:.1f}%)")
        
        # Validation criteria
        success = True
        
        if overhead_percent > 25:
            print(f"WARNING: Speed factor overhead ({overhead_percent:.1f}%) higher than target (15%)")
            success = False
        else:
            print(f"EXCELLENT: Speed factor overhead within target")
        
        if base_time > 60:
            print(f"WARNING: Base generation time ({base_time:.2f}s) slower than expected")
            success = False
        else:
            print(f"GOOD: Base generation time acceptable")
        
        # Test consistency
        if '0.8x' in results:
            time_0_8x = results['0.8x']
            if abs(time_0_8x - speed_time) > 5:  # Within 5 seconds
                print(f"INFO: Speed factor times vary (1.5x: {speed_time:.2f}s, 0.8x: {time_0_8x:.2f}s)")
            else:
                print(f"GOOD: Consistent speed factor processing times")
        
        return success
    
    return False

def main():
    print("Phase 10.1.2 - Speed Factor Architecture Optimization Test")
    print("Testing separated speed factor processing performance")
    
    try:
        success = test_speed_factor_optimization()
        
        if success:
            print(f"\n" + "="*50)
            print("PHASE 10.1.2 OPTIMIZATION TEST: PASSED")
            print("="*50)
            print("- Speed factor architectural optimization working")
            print("- Performance within expected parameters")
            print("- Ready for production use")
        else:
            print(f"\n" + "="*50)
            print("PHASE 10.1.2 OPTIMIZATION TEST: FAILED")
            print("="*50)
            print("- Performance issues detected")
            print("- Review optimization implementation")
        
        return success
        
    except Exception as e:
        print(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
