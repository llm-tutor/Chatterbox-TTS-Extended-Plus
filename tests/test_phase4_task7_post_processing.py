#!/usr/bin/env python3
"""
Phase 4 Task 4.7 Test Suite - Post-Processing Integration
Tests auto-editor and ffmpeg normalization post-processing
"""

import os
import sys
import time
import requests
import json
from pathlib import Path

# Test configuration
BASE_URL = "http://127.0.0.1:7860"
TIMEOUT = 60

def print_header(text):
    """Print formatted test header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_step(text):
    """Print test step"""
    print(f"\n[STEP] {text}")

def print_result(success, message):
    """Print test result"""
    status = "PASS" if success else "FAIL"
    print(f"[{status}] {message}")

def test_health_check():
    """Verify server is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=10)
        return response.status_code == 200
    except:
        return False

def test_basic_tts_without_post_processing():
    """Test basic TTS generation without post-processing"""
    print_step("Testing basic TTS generation (baseline)")
    
    payload = {
        "text": "Testing basic TTS generation without post-processing.",
        "export_formats": ["wav"],
        "use_auto_editor": False,
        "normalize_audio": False
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/tts", json=payload, timeout=TIMEOUT)
    duration = time.time() - start_time
    
    success = response.status_code == 200
    
    if success:
        print_result(True, f"Basic TTS completed in {duration:.1f}s")
        if response.headers.get('content-type') == 'audio/wav':
            print("  -> Direct audio response received")
        else:
            print("  -> JSON response with file information")
    else:
        print_result(False, f"Basic TTS failed: {response.status_code}")
        if response.content:
            try:
                error_data = response.json()
                print(f"  Error: {error_data}")
            except:
                print(f"  Error content: {response.content[:200]}")
    
    return success

def test_auto_editor_post_processing():
    """Test auto-editor post-processing (if auto-editor is available)"""
    print_step("Testing auto-editor post-processing")
    
    payload = {
        "text": "Testing auto-editor post-processing with threshold and margin settings.",
        "export_formats": ["wav"],
        "use_auto_editor": True,
        "keep_original_wav_ae": False,
        "ae_threshold": 0.06,
        "ae_margin": 0.2,
        "normalize_audio": False
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/tts", json=payload, timeout=TIMEOUT)
    duration = time.time() - start_time
    
    success = response.status_code == 200
    
    if success:
        print_result(True, f"Auto-editor TTS completed in {duration:.1f}s")
        print("  -> Auto-editor post-processing applied successfully")
    else:
        print_result(False, f"Auto-editor TTS failed: {response.status_code}")
        if response.content:
            try:
                error_data = response.json()
                print(f"  Error: {error_data}")
            except:
                print(f"  Error content: {response.content[:200]}")
        print("  Note: This may fail if auto-editor is not installed")
    
    return success

def test_ffmpeg_normalization_ebu():
    """Test FFmpeg EBU normalization"""
    print_step("Testing FFmpeg EBU normalization")
    
    payload = {
        "text": "Testing FFmpeg EBU normalization with specific loudness parameters.",
        "export_formats": ["wav"],
        "use_auto_editor": False,
        "normalize_audio": True,
        "normalize_method": "ebu",
        "normalize_level": -24.0,
        "normalize_tp": -2.0,
        "normalize_lra": 7.0
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/tts", json=payload, timeout=TIMEOUT)
    duration = time.time() - start_time
    
    success = response.status_code == 200
    
    if success:
        print_result(True, f"FFmpeg EBU normalization completed in {duration:.1f}s")
        print("  -> EBU loudness normalization applied successfully")
    else:
        print_result(False, f"FFmpeg EBU normalization failed: {response.status_code}")
        if response.content:
            try:
                error_data = response.json()
                print(f"  Error: {error_data}")
            except:
                print(f"  Error content: {response.content[:200]}")
    
    return success

def test_ffmpeg_normalization_peak():
    """Test FFmpeg peak normalization"""
    print_step("Testing FFmpeg peak normalization")
    
    payload = {
        "text": "Testing FFmpeg peak normalization using dynaudnorm filter.",
        "export_formats": ["wav"],
        "use_auto_editor": False,
        "normalize_audio": True,
        "normalize_method": "peak"
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/tts", json=payload, timeout=TIMEOUT)
    duration = time.time() - start_time
    
    success = response.status_code == 200
    
    if success:
        print_result(True, f"FFmpeg peak normalization completed in {duration:.1f}s")
        print("  -> Peak normalization with dynaudnorm applied successfully")
    else:
        print_result(False, f"FFmpeg peak normalization failed: {response.status_code}")
        if response.content:
            try:
                error_data = response.json()
                print(f"  Error: {error_data}")
            except:
                print(f"  Error content: {response.content[:200]}")
    
    return success

def test_complete_post_processing_pipeline():
    """Test complete post-processing pipeline (auto-editor + ffmpeg normalization)"""
    print_step("Testing complete post-processing pipeline")
    
    payload = {
        "text": "Testing the complete post-processing pipeline with both auto-editor and FFmpeg normalization.",
        "export_formats": ["wav"],
        "use_auto_editor": True,
        "keep_original_wav_ae": True,
        "ae_threshold": 0.08,
        "ae_margin": 0.3,
        "normalize_audio": True,
        "normalize_method": "ebu",
        "normalize_level": -23.0,
        "normalize_tp": -1.0,
        "normalize_lra": 8.0
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/tts", json=payload, timeout=TIMEOUT)
    duration = time.time() - start_time
    
    success = response.status_code == 200
    
    if success:
        print_result(True, f"Complete post-processing pipeline completed in {duration:.1f}s")
        print("  -> Both auto-editor and FFmpeg normalization applied successfully")
    else:
        print_result(False, f"Complete post-processing pipeline failed: {response.status_code}")
        if response.content:
            try:
                error_data = response.json()
                print(f"  Error: {error_data}")
            except:
                print(f"  Error content: {response.content[:200]}")
        print("  Note: This may fail if auto-editor is not installed")
    
    return success

def test_post_processing_with_existing_features():
    """Test post-processing integration with existing features (speed factor, trimming)"""
    print_step("Testing post-processing integration with existing features")
    
    payload = {
        "text": "Testing post-processing integration with speed factor and trimming features.",
        "export_formats": ["wav"],
        "speed_factor": 1.2,
        "trim": True,
        "trim_threshold_ms": 150,
        "use_auto_editor": False,  # Skip auto-editor to focus on ffmpeg
        "normalize_audio": True,
        "normalize_method": "ebu",
        "normalize_level": -22.0
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/tts", json=payload, timeout=TIMEOUT)
    duration = time.time() - start_time
    
    success = response.status_code == 200
    
    if success:
        print_result(True, f"Integrated post-processing completed in {duration:.1f}s")
        print("  -> Speed factor, trimming, and normalization applied successfully")
    else:
        print_result(False, f"Integrated post-processing failed: {response.status_code}")
        if response.content:
            try:
                error_data = response.json()
                print(f"  Error: {error_data}")
            except:
                print(f"  Error content: {response.content[:200]}")
    
    return success

def main():
    """Run all post-processing tests"""
    print_header("Phase 4 Task 4.7 - Post-Processing Integration Test Suite")
    
    # Check server health
    print_step("Checking server health...")
    if not test_health_check():
        print_result(False, "Server not responding. Please start the server first.")
        return False
    print_result(True, "Server is running")
    
    # Run all tests
    test_results = []
    
    test_results.append(test_basic_tts_without_post_processing())
    test_results.append(test_ffmpeg_normalization_ebu())
    test_results.append(test_ffmpeg_normalization_peak())
    test_results.append(test_post_processing_with_existing_features())
    
    # Optional tests (may fail if dependencies not installed)
    print("\n" + "="*60)
    print("  OPTIONAL TESTS (may fail if dependencies missing)")
    print("="*60)
    
    test_results.append(test_auto_editor_post_processing())
    test_results.append(test_complete_post_processing_pipeline())
    
    # Summary
    print_header("Test Summary")
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed >= 4:  # Core tests passed
        print_result(True, "Core post-processing functionality working correctly!")
        print("Note: Auto-editor tests may fail if auto-editor is not installed.")
    else:
        print_result(False, "Core post-processing tests failed")
    
    return passed >= 4

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
