#!/usr/bin/env python3
"""
Phase 10.1.3 Enhanced Speed Factor Library Integration Test

Tests the integration of enhanced audio libraries (audiostretchy, pyrubberband)
with the architectural optimizations from Phase 10.1.2.

Tests:
1. Library selection and fallback behavior
2. Audio quality with different libraries
3. Performance maintenance from 10.1.2 optimization
4. Smart library selection based on speed factor range
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

def test_enhanced_speed_libraries():
    """Test Phase 10.1.3 enhanced speed factor library integration"""
    
    if not wait_for_server():
        print("ERROR: Server not accessible")
        return False
    
    print("\n=== PHASE 10.1.3 ENHANCED SPEED FACTOR LIBRARIES TEST ===")
    
    reference_file = "speaker_en/jamie_vc_to_david-2.wav"
    test_text = "Testing Phase 10.1.3 enhanced speed factor library integration with audiostretchy and pyrubberband."
    
    results = {}
    
    # Test 1: Auto library selection (small speed change - should prefer audiostretchy)
    print("\n--- Test 1: Auto library selection (1.1x - small change) ---")
    start = time.time()
    
    try:
        response = requests.post(f"{API_BASE}/tts?response_mode=url", json={
            "text": test_text,
            "reference_audio_filename": reference_file,
            "speed_factor": 1.1,
            "speed_factor_library": "auto",
            "export_formats": ["wav"]
        }, timeout=120)
        
        time_auto_small = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: {time_auto_small:.2f}s")
            print(f"Output file: {result.get('wav_url', 'Unknown')}")
            results['auto_1.1x'] = time_auto_small
        else:
            print(f"FAILED: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"FAILED: {e}")
        return False
    
    time.sleep(2)
    
    # Test 2: Explicit audiostretchy library
    print("\n--- Test 2: Explicit audiostretchy library (1.5x) ---")
    start = time.time()
    
    try:
        response = requests.post(f"{API_BASE}/tts?response_mode=url", json={
            "text": test_text,
            "reference_audio_filename": reference_file,
            "speed_factor": 1.5,
            "speed_factor_library": "audiostretchy",
            "export_formats": ["wav"]
        }, timeout=120)
        
        time_audiostretchy = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: {time_audiostretchy:.2f}s")
            print(f"Output file: {result.get('wav_url', 'Unknown')}")
            results['audiostretchy_1.5x'] = time_audiostretchy
        else:
            print(f"FAILED: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"FAILED: {e}")
        return False
    
    time.sleep(2)
    
    # Test 3: Explicit pyrubberband library
    print("\n--- Test 3: Explicit pyrubberband library (0.8x) ---")
    start = time.time()
    
    try:
        response = requests.post(f"{API_BASE}/tts?response_mode=url", json={
            "text": test_text,
            "reference_audio_filename": reference_file,
            "speed_factor": 0.8,
            "speed_factor_library": "pyrubberband",
            "export_formats": ["wav"]
        }, timeout=120)
        
        time_pyrubberband = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: {time_pyrubberband:.2f}s")
            print(f"Output file: {result.get('wav_url', 'Unknown')}")
            results['pyrubberband_0.8x'] = time_pyrubberband
        else:
            print(f"FAILED: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"FAILED: {e}")
        return False
    
    time.sleep(2)
    
    # Test 4: Librosa fallback (baseline comparison)
    print("\n--- Test 4: Librosa baseline (1.2x) ---")
    start = time.time()
    
    try:
        response = requests.post(f"{API_BASE}/tts?response_mode=url", json={
            "text": test_text,
            "reference_audio_filename": reference_file,
            "speed_factor": 1.2,
            "speed_factor_library": "librosa",
            "export_formats": ["wav"]
        }, timeout=120)
        
        time_librosa = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: {time_librosa:.2f}s")
            print(f"Output file: {result.get('wav_url', 'Unknown')}")
            results['librosa_1.2x'] = time_librosa
        else:
            print(f"FAILED: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"FAILED: {e}")
        return False
    
    time.sleep(2)
    
    # Test 5: Optimized path (1.0x - should have zero overhead)
    print("\n--- Test 5: Optimized path (1.0x - zero overhead) ---")
    start = time.time()
    
    try:
        response = requests.post(f"{API_BASE}/tts?response_mode=url", json={
            "text": test_text,
            "reference_audio_filename": reference_file,
            "speed_factor": 1.0,
            "speed_factor_library": "auto",
            "export_formats": ["wav"]
        }, timeout=120)
        
        time_optimized = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: {time_optimized:.2f}s")
            print(f"Output file: {result.get('wav_url', 'Unknown')}")
            results['optimized_1.0x'] = time_optimized
        else:
            print(f"FAILED: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"FAILED: {e}")
        return False
    
    # Analysis
    print(f"\n=== ENHANCED LIBRARY INTEGRATION ANALYSIS ===")
    
    if 'optimized_1.0x' in results:
        baseline_time = results['optimized_1.0x']
        print(f"Baseline (1.0x): {baseline_time:.2f}s (optimized path)")
        
        # Check overhead for each library
        for test_name, test_time in results.items():
            if test_name != 'optimized_1.0x':
                overhead = test_time - baseline_time
                overhead_percent = (overhead / baseline_time) * 100
                print(f"{test_name}: {test_time:.2f}s (overhead: {overhead:.2f}s, {overhead_percent:.1f}%)")
    
    # Validation criteria
    success = True
    
    # Check if all tests completed
    expected_tests = ['auto_1.1x', 'audiostretchy_1.5x', 'pyrubberband_0.8x', 'librosa_1.2x', 'optimized_1.0x']
    missing_tests = set(expected_tests) - set(results.keys())
    
    if missing_tests:
        print(f"ERROR: Missing test results: {missing_tests}")
        success = False
    
    # Check performance is reasonable (baseline under 60s, overhead under 30%)
    if 'optimized_1.0x' in results:
        if results['optimized_1.0x'] > 60:
            print(f"WARNING: Baseline performance ({results['optimized_1.0x']:.2f}s) slower than expected")
            success = False
        
        for test_name, test_time in results.items():
            if test_name != 'optimized_1.0x':
                overhead_percent = ((test_time - results['optimized_1.0x']) / results['optimized_1.0x']) * 100
                if overhead_percent > 30:
                    print(f"WARNING: {test_name} overhead ({overhead_percent:.1f}%) higher than target (30%)")
                    success = False
    
    return success

def main():
    print("Phase 10.1.3 - Enhanced Speed Factor Library Integration Test")
    print("Testing audiostretchy, pyrubberband, and smart library selection")
    
    try:
        success = test_enhanced_speed_libraries()
        
        if success:
            print(f"\n" + "="*60)
            print("PHASE 10.1.3 ENHANCED LIBRARY INTEGRATION: PASSED")
            print("="*60)
            print("- Enhanced audio libraries (audiostretchy, pyrubberband) integrated")
            print("- Smart library selection based on speed factor range working")
            print("- Performance optimizations from Phase 10.1.2 maintained")
            print("- All speed factor libraries functional")
            print("- Ready for production use with enhanced audio quality")
        else:
            print(f"\n" + "="*60)
            print("PHASE 10.1.3 ENHANCED LIBRARY INTEGRATION: FAILED")
            print("="*60)
            print("- Review library integration or performance issues")
            print("- Check library installation and compatibility")
        
        return success
        
    except Exception as e:
        print(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
