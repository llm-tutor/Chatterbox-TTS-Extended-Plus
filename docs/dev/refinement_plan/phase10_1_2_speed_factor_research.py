#!/usr/bin/env python3
"""
Phase 10.1.2 Performance Optimization Implementation

Based on investigation results:
1. Current librosa implementation is stable (no progressive degradation)
2. Performance is ~20% slower than optimal (20-25 it/s vs 28-30 it/s)
3. Need to optimize without introducing the heavy library overhead

Strategy: Optimize the current librosa implementation rather than 
replacing it with heavier libraries that caused 10x slowdown.
"""

import torch
import numpy as np
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def apply_speed_factor_optimized(
    audio_tensor: torch.Tensor, 
    sample_rate: int, 
    speed_factor: float
) -> torch.Tensor:
    """
    Optimized speed factor implementation focusing on performance
    
    Optimizations:
    1. Early return for speed_factor=1.0 (most common case)
    2. Minimize library imports and overhead
    3. Cache imports at module level
    4. Streamlined tensor operations
    
    Args:
        audio_tensor: Input audio tensor (1D or 2D)
        sample_rate: Audio sample rate  
        speed_factor: Speed multiplier (0.5x to 2.0x)
    
    Returns:
        Speed-adjusted audio tensor
    """
    # CRITICAL: Return immediately for 1.0 before any processing
    if speed_factor == 1.0:
        return audio_tensor
    
    try:
        # Use cached import (imported at module level below)
        # Convert tensor to numpy array (minimize conversions)
        if isinstance(audio_tensor, torch.Tensor):
            audio_np = audio_tensor.detach().cpu().numpy()
            original_device = audio_tensor.device
        else:
            audio_np = audio_tensor
            original_device = None
        
        # Handle different tensor shapes efficiently
        if audio_np.ndim == 2:
            # Multi-channel audio - process each channel
            processed_channels = []
            for channel in range(audio_np.shape[0]):
                # Use cached librosa function
                processed_channel = _cached_librosa_time_stretch(
                    audio_np[channel], 
                    rate=speed_factor
                )
                processed_channels.append(processed_channel)
            processed_audio = np.stack(processed_channels, axis=0)
        else:
            # Single channel audio - direct processing
            processed_audio = _cached_librosa_time_stretch(
                audio_np, 
                rate=speed_factor
            )
        
        # Convert back to tensor efficiently
        if original_device is not None:
            return torch.from_numpy(processed_audio).to(original_device)
        else:
            return torch.from_numpy(processed_audio)
            
    except ImportError:
        logger.warning("librosa not available, falling back to torchaudio")
        return _apply_speed_factor_fallback_optimized(audio_tensor, sample_rate, speed_factor)
    except Exception as e:
        logger.error(f"Optimized speed factor failed: {e}")
        logger.warning("Returning original audio without speed adjustment")
        return audio_tensor


def _apply_speed_factor_fallback_optimized(
    audio_tensor: torch.Tensor, 
    sample_rate: int, 
    speed_factor: float
) -> torch.Tensor:
    """
    Optimized fallback using torchaudio (affects pitch but lightweight)
    """
    try:
        # Use cached import
        # Calculate new sample rate for speed adjustment
        new_sample_rate = int(sample_rate * speed_factor)
        
        # Resample to achieve speed change (will affect pitch)
        resampled = _cached_torchaudio_resample(
            audio_tensor,
            orig_freq=sample_rate,
            new_freq=new_sample_rate
        )
        
        return resampled
        
    except Exception as e:
        logger.error(f"Fallback speed factor failed: {e}")
        return audio_tensor


# Module-level imports and caching for performance
_librosa_available = None
_torchaudio_available = None
_cached_librosa_time_stretch = None
_cached_torchaudio_resample = None

def _initialize_speed_factor_libraries():
    """Initialize libraries once at module import time"""
    global _librosa_available, _torchaudio_available
    global _cached_librosa_time_stretch, _cached_torchaudio_resample
    
    # Try librosa import
    try:
        import librosa.effects
        _librosa_available = True
        _cached_librosa_time_stretch = librosa.effects.time_stretch
        logger.info("Speed factor: librosa available")
    except ImportError:
        _librosa_available = False
        logger.warning("Speed factor: librosa not available")
    
    # Try torchaudio import  
    try:
        import torchaudio.functional
        _torchaudio_available = True
        _cached_torchaudio_resample = torchaudio.functional.resample
        logger.info("Speed factor: torchaudio available")
    except ImportError:
        _torchaudio_available = False
        logger.warning("Speed factor: torchaudio not available")

# Initialize libraries when module is imported
_initialize_speed_factor_libraries()

# Alternative implementation: Pre-load libraries in a separate process
def apply_speed_factor_process_optimized(
    audio_tensor: torch.Tensor,
    sample_rate: int, 
    speed_factor: float,
    use_subprocess: bool = False
) -> torch.Tensor:
    """
    Process-optimized speed factor that can optionally use subprocess
    to isolate heavy library operations
    
    This is for future investigation if the main optimization isn't sufficient
    """
    if speed_factor == 1.0:
        return audio_tensor
    
    if use_subprocess:
        # TODO: Implement subprocess-based processing for isolation
        # This would prevent any library side effects from affecting main process
        logger.info("Subprocess speed factor not yet implemented, using main process")
    
    return apply_speed_factor_optimized(audio_tensor, sample_rate, speed_factor)


# Performance monitoring utilities
def benchmark_speed_factor_performance():
    """
    Benchmark function to test speed factor performance
    """
    print("=== SPEED FACTOR PERFORMANCE BENCHMARK ===")
    
    # Create test audio
    sample_rate = 22050
    duration = 3.0  # 3 seconds
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples)
    test_audio = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
    audio_tensor = torch.from_numpy(test_audio).float()
    
    # Test cases
    test_cases = [
        ("1.0x (no-op)", 1.0),
        ("1.5x speed", 1.5), 
        ("0.8x speed", 0.8),
        ("2.0x speed", 2.0),
        ("0.5x speed", 0.5),
    ]
    
    results = []
    
    for name, speed in test_cases:
        print(f"\nTesting {name}...")
        
        # Warm up
        _ = apply_speed_factor_optimized(audio_tensor, sample_rate, speed)
        
        # Benchmark
        times = []
        for i in range(5):  # 5 runs
            start = time.time()
            result = apply_speed_factor_optimized(audio_tensor, sample_rate, speed)
            end = time.time()
            times.append(end - start)
        
        avg_time = np.mean(times)
        min_time = np.min(times)
        max_time = np.max(times)
        
        results.append({
            'name': name,
            'speed_factor': speed,
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'output_samples': len(result)
        })
        
        print(f"  Average: {avg_time*1000:.2f}ms")
        print(f"  Range: {min_time*1000:.2f}-{max_time*1000:.2f}ms")
        print(f"  Output: {len(result)} samples")
    
    print(f"\n=== BENCHMARK SUMMARY ===")
    for r in results:
        print(f"{r['name']:15} {r['avg_time']*1000:6.2f}ms avg")
    
    return results


if __name__ == "__main__":
    import time
    
    print("Testing optimized speed factor implementation...")
    
    # Run benchmark
    results = benchmark_speed_factor_performance()
    
    # Save results
    import json
    with open("speed_factor_benchmark.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\nBenchmark results saved to speed_factor_benchmark.json")
