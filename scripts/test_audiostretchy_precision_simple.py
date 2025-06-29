#!/usr/bin/env python3
"""
Test script for Task 11.11: Verify audiostretchy maintains 32-bit float precision

This test verifies that the speed factor processing with audiostretchy
maintains float32 precision instead of generating 64-bit audio files.
"""

import sys
import numpy as np
import torch
import tempfile
import soundfile as sf
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.audio.processing import apply_speed_factor

def test_audiostretchy_precision():
    """Test that audiostretchy maintains float32 precision"""
    print("Testing audiostretchy precision fix (Task 11.11)")
    print("=" * 60)
    
    # Create test audio (simple sine wave)
    duration = 1.0  # 1 second
    sample_rate = 22050
    frequency = 440  # A4 note
    
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    audio_np = 0.5 * np.sin(2 * np.pi * frequency * t).astype(np.float32)
    audio_tensor = torch.from_numpy(audio_np)
    
    print(f"Created test audio:")
    print(f"   Duration: {duration}s")
    print(f"   Sample rate: {sample_rate} Hz")
    print(f"   Original dtype: {audio_tensor.dtype}")
    print(f"   Original shape: {audio_tensor.shape}")
    
    # Test different speed factors
    speed_factors = [0.8, 1.2, 1.5]
    
    for speed_factor in speed_factors:
        print(f"\nTesting speed factor: {speed_factor}x")
        
        try:
            # Apply speed factor with audiostretchy
            processed_audio = apply_speed_factor(
                audio_tensor, 
                sample_rate, 
                speed_factor,
                preferred_library="audiostretchy"
            )
            
            print(f"Processing successful:")
            print(f"   Output dtype: {processed_audio.dtype}")
            print(f"   Output shape: {processed_audio.shape}")
            print(f"   Expected duration: {len(processed_audio) / sample_rate:.2f}s")
            
            # Check if dtype is float32
            if processed_audio.dtype == torch.float32:
                print(f"   [PASS] Correct precision: float32")
            else:
                print(f"   [FAIL] Wrong precision: {processed_audio.dtype} (expected float32)")
            
            # Check if the length changed appropriately
            expected_length = int(len(audio_tensor) / speed_factor)
            actual_length = len(processed_audio)
            length_ratio = actual_length / expected_length
            
            if 0.95 <= length_ratio <= 1.05:  # Allow 5% tolerance
                print(f"   [PASS] Length correct: {actual_length} samples (ratio: {length_ratio:.3f})")
            else:
                print(f"   [WARN] Length unexpected: {actual_length} samples (expected ~{expected_length}, ratio: {length_ratio:.3f})")
            
        except Exception as e:
            print(f"   [FAIL] Processing failed: {e}")
    
    # Test that audiostretchy is available
    try:
        import audiostretchy
        print(f"\n[INFO] audiostretchy library is available")
    except ImportError:
        print(f"\n[WARN] audiostretchy library not available - test results may not be representative")
    
    print(f"\nPrecision test complete!")

def test_write_read_precision():
    """Test soundfile write/read precision specifically"""
    print(f"\nTesting soundfile precision handling")
    print("-" * 40)
    
    # Create test audio
    audio_np = np.random.random(1000).astype(np.float32) * 0.5
    sample_rate = 22050
    
    print(f"Original audio dtype: {audio_np.dtype}")
    
    # Test writing and reading with different parameters
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Write with explicit float subtype
        sf.write(temp_path, audio_np, sample_rate, subtype='FLOAT')
        
        # Read back
        audio_read, _ = sf.read(temp_path, dtype='float32')
        
        print(f"After write/read dtype: {audio_read.dtype}")
        print(f"Data preserved: {np.allclose(audio_np, audio_read)}")
        
        if audio_read.dtype == np.float32:
            print(f"[PASS] soundfile maintains float32 precision")
        else:
            print(f"[FAIL] soundfile changed precision to {audio_read.dtype}")
    
    finally:
        import os
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == "__main__":
    test_audiostretchy_precision()
    test_write_read_precision()
