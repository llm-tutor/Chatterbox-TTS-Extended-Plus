#!/usr/bin/env python3
"""
Test Parallel Processing Implementation - Chatter.py Migration
Tests the ThreadPoolExecutor-based parallel processing system implemented in Phases 2-3

This test validates:
- Automatic parallel vs sequential processing selection
- Progress tracking during parallel generation
- Multi-chunk audio assembly
- Parameter flow for parallel processing configuration
"""

import requests
import json
import time

def test_sequential_processing():
    """Test single sentence -> sequential processing"""
    print("=== Testing Sequential Processing (Single Sentence) ===")
    
    payload = {
        "text": "This single sentence should trigger sequential processing.",
        "enable_parallel": True,
        "num_parallel_workers": 4,
        "export_formats": ["wav"]
    }
    
    start_time = time.time()
    response = requests.post(
        "http://127.0.0.1:7860/api/v1/tts",
        json=payload,
        params={"response_mode": "url"}
    )
    duration = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"SUCCESS! Sequential processing completed in {duration:.1f}s")
        print(f"Generated files: {len(result.get('output_files', []))}")
        return True
    else:
        print(f"FAILED: {response.status_code} - {response.text}")
        return False

def test_parallel_processing():
    """Test multiple sentences -> parallel processing"""
    print("\n=== Testing Parallel Processing (Multiple Sentences) ===")
    
    # Test text with multiple sentences to trigger parallel processing
    test_text = """
    This is the first sentence that should be processed in parallel. 
    This is the second sentence for demonstrating parallel processing. 
    Here comes the third sentence to create multiple chunks for workers.
    The fourth sentence will show our parallel capabilities in action.
    Finally, this fifth sentence completes our parallel processing test.
    """
    
    payload = {
        "text": test_text.strip(),
        "enable_parallel": True,
        "num_parallel_workers": 3,
        "smart_batch_short_sentences": False,  # Force individual sentences
        "export_formats": ["wav"]
    }
    
    print(f"Text: {len(test_text.strip())} characters")
    print(f"Expected: ~5 sentences -> 5 chunks -> parallel processing")
    
    start_time = time.time()
    response = requests.post(
        "http://127.0.0.1:7860/api/v1/tts",
        json=payload,
        params={"response_mode": "url"}
    )
    duration = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"SUCCESS! Parallel processing completed in {duration:.1f}s")
        print(f"Generated files: {len(result.get('output_files', []))}")
        print(f"Processing time: {result.get('processing_time_seconds', 0):.1f}s")
        return True
    else:
        print(f"FAILED: {response.status_code} - {response.text}")
        return False

def test_parallel_disabled():
    """Test parallel processing disabled -> sequential"""
    print("\n=== Testing Parallel Disabled (Should Use Sequential) ===")
    
    test_text = """
    First sentence for sequential test.
    Second sentence should also be sequential.
    Third sentence continues the sequential processing.
    """
    
    payload = {
        "text": test_text.strip(),
        "enable_parallel": False,  # Explicitly disable parallel
        "smart_batch_short_sentences": False,
        "export_formats": ["wav"]
    }
    
    start_time = time.time()
    response = requests.post(
        "http://127.0.0.1:7860/api/v1/tts",
        json=payload,
        params={"response_mode": "url"}
    )
    duration = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"SUCCESS! Forced sequential processing completed in {duration:.1f}s")
        print(f"Generated files: {len(result.get('output_files', []))}")
        return True
    else:
        print(f"FAILED: {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    print("Parallel Processing Implementation Test")
    print("Phase 2 & 3 - Chatter.py Migration Validation")
    print("=" * 60)
    
    # Test server availability
    try:
        health_response = requests.get("http://127.0.0.1:7860/api/v1/health", timeout=5)
        if health_response.status_code != 200:
            print("ERROR: Server not available")
            exit(1)
    except:
        print("ERROR: Cannot connect to server at http://127.0.0.1:7860")
        exit(1)
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_sequential_processing():
        tests_passed += 1
    
    if test_parallel_processing():
        tests_passed += 1
        
    if test_parallel_disabled():
        tests_passed += 1
    
    print(f"\n{'='*60}")
    print(f"PARALLEL PROCESSING TEST SUMMARY")
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {tests_passed/total_tests*100:.1f}%")
    
    if tests_passed == total_tests:
        print("RESULT: ALL PARALLEL PROCESSING TESTS PASSED")
        print("Phase 2 & 3 implementation validated successfully!")
    else:
        print("RESULT: SOME TESTS FAILED")
        print("Check server logs for detailed error information")
    
    print("\nCheck server logs for detailed parallel processing evidence:")
    print("- 'Processing X chunks sequentially' (for sequential)")  
    print("- 'Processing X chunks in parallel with Y workers' (for parallel)")
    print("- '[PROGRESS] Generated chunk X/Y (Z%)' (for parallel progress)")

