#!/usr/bin/env python3
"""
Test script for comparing TTS generation performance across different reference audio files
Systematically measures generation time for different reference audio content
"""

import requests
import time
import json
import argparse
from datetime import datetime
from pathlib import Path

# Test configuration
API_BASE = "http://127.0.0.1:7860"

# Two test texts of approximately half the length of the original
TEST_TEXTS = [
    "In a village of La Mancha, the name of which I have no desire to call to mind, there lived not long since one of those gentlemen that keep a lance in the lance-rack.",
    "It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity."
]

# Single test sentence
TEST_TEXT = "Second test: The quick brown fox jumps over the lazy dog, displaying the grace of nature's eternal dance."

# Three different reference audio files
REFERENCE_AUDIO_FILES = {
    "alt_voice": "speaker_en/Jamie01.mp3",  # 16s
    "native_voice": "speaker_en/jamie_vc_to_david-2.wav",  # 20s
    "non_native_voice": "speaker_en/DAVID-2.mp3",  # 1m 23s
    "linda_johnson": "test_voices/linda_johnson_01.wav",  # 49s
}

# Speed factors to test
SPEED_FACTORS = [0.85, 0.95, 1.05]

def format_duration(seconds):
    """Format duration in a human-readable way"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.2f}s"

def make_tts_request(text, speed_factor, reference_audio_file, test_name):
    """Make a single TTS request and measure response time"""
    print(f"    Testing: {test_name}")
    
    request_data = {
        "text": text,
        "speed_factor": speed_factor,
        "speed_factor_library": "audiostretchy",
        "export_formats": ["wav"],
        "reference_audio_filename": reference_audio_file
    }
    
    start_time = time.time()
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/tts?response_mode=url",
            json=request_data,
            timeout=480
        )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            # Check response type
            content_type = response.headers.get('content-type', '')
            if 'application/octet-stream' in content_type:
                file_size = len(response.content)
                print(f"      ✓ SUCCESS - Duration: {format_duration(duration)}, Size: {file_size:,} bytes")
                return duration, True, f"Success ({file_size:,} bytes)"
            else:
                # JSON response
                result = response.json()
                if result.get('success'):
                    print(f"      ✓ SUCCESS - Duration: {format_duration(duration)}")
                    return duration, True, "Success (JSON)"
                else:
                    error_msg = result.get('message', 'Unknown error')
                    print(f"      ✗ FAILED - {error_msg}")
                    return duration, False, error_msg
        else:
            try:
                error_detail = response.json()
                error_msg = f"HTTP {response.status_code}: {error_detail}"
            except:
                error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
            print(f"      ✗ FAILED - {error_msg}")
            return duration, False, error_msg
            
    except requests.exceptions.Timeout:
        print(f"      ✗ TIMEOUT after 480 seconds")
        return 480.0, False, "Timeout"
    except Exception as e:
        print(f"      ✗ ERROR: {e}")
        return 0.0, False, str(e)

def run_reference_file_comparison_test():
    """Run the complete reference file comparison test"""
    
    print("TTS Reference Audio File Performance Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Base: {API_BASE}")
    print(f"Speed factors: {SPEED_FACTORS}")
    print(f"Reference files: {list(REFERENCE_AUDIO_FILES.keys())}")
    print(f"Test text: {TEST_TEXT}")
    print()
    
    # Store all results
    results = {}
    
    # Test each speed factor
    for speed_idx, speed_factor in enumerate(SPEED_FACTORS, 1):
        print(f"Testing Speed Factor {speed_factor}x ({speed_idx}/{len(SPEED_FACTORS)})")
        print("-" * 40)
        
        speed_results = {}
        
        # Test each reference file
        for ref_name, audio_file in REFERENCE_AUDIO_FILES.items():
            test_name = f"Speed {speed_factor}x, Reference {ref_name}"
            
            duration, success, status = make_tts_request(
                TEST_TEXT, speed_factor, audio_file, test_name
            )
            
            speed_results[ref_name] = {
                'duration': duration,
                'success': success,
                'status': status
            }
        
        results[speed_factor] = speed_results
        print()
    
    return results

def generate_markdown_report(results, output_file):
    """Generate a markdown report with the test results"""
    
    report_lines = []
    
    # Header
    report_lines.extend([
        "# TTS Reference Audio File Performance Test Results",
        "",
        f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**API Endpoint:** {API_BASE}",
        "",
        "## Test Configuration",
        "",
        f"- **Speed Factors:** {', '.join(f'{sf}x' for sf in SPEED_FACTORS)}",
        f"- **Reference Audio Files:** {len(REFERENCE_AUDIO_FILES)} different files",
        "",
        "### Test Text Used:",
        "",
        f'"{TEST_TEXT}"',
        "",
        "### Reference Audio Files:",
        ""
    ])
    
    for ref_name, file_path in REFERENCE_AUDIO_FILES.items():
        report_lines.append(f"- **{ref_name}:** {file_path}")
    
    report_lines.extend(["", "## Results Summary", ""])
    
    # Generate tables for each speed factor
    for speed_factor in SPEED_FACTORS:
        speed_results = results[speed_factor]
        
        report_lines.extend([
            f"### Speed Factor: {speed_factor}x",
            "",
            "| Reference File | Duration | Status |",
            "|----------------|----------|--------|"
        ])
        
        for ref_name in REFERENCE_AUDIO_FILES.keys():
            if ref_name in speed_results:
                result = speed_results[ref_name]
                if result['success']:
                    duration_str = f"{result['duration']:.2f}s"
                    status_str = "✅ Success"
                else:
                    duration_str = "FAILED"
                    status_str = f"❌ {result['status']}"
                
                report_lines.append(f"| {ref_name} | {duration_str} | {status_str} |")
            else:
                report_lines.append(f"| {ref_name} | N/A | N/A |")
        
        report_lines.append("")
    
    # Add comparison table
    report_lines.extend([
        "## Performance Comparison Across All Speed Factors",
        "",
        "| Reference File | 0.85x | 0.95x | 1.05x | Average |",
        "|----------------|-------|-------|-------|---------|"
    ])
    
    for ref_name in REFERENCE_AUDIO_FILES.keys():
        row_data = [ref_name]
        durations = []
        
        for speed_factor in SPEED_FACTORS:
            if (speed_factor in results and 
                ref_name in results[speed_factor] and 
                results[speed_factor][ref_name]['success']):
                duration = results[speed_factor][ref_name]['duration']
                row_data.append(f"{duration:.2f}s")
                durations.append(duration)
            else:
                row_data.append("FAILED")
        
        # Calculate average
        if durations:
            avg_duration = sum(durations) / len(durations)
            row_data.append(f"**{avg_duration:.2f}s**")
        else:
            row_data.append("**N/A**")
        
        report_lines.append("| " + " | ".join(row_data) + " |")
    
    report_lines.append("")
    
    # Add detailed results section
    report_lines.extend([
        "## Detailed Results",
        ""
    ])
    
    for speed_factor in SPEED_FACTORS:
        speed_results = results[speed_factor]
        report_lines.extend([
            f"### Speed Factor {speed_factor}x - Detailed Results",
            ""
        ])
        
        for ref_name in REFERENCE_AUDIO_FILES.keys():
            if ref_name in speed_results:
                result = speed_results[ref_name]
                status_icon = "✅" if result['success'] else "❌"
                report_lines.append(f"- **{ref_name}:** {status_icon} {result['duration']:.2f}s - {result['status']}")
        
        report_lines.append("")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"Markdown report saved to: {output_file}")

def display_summary_tables(results):
    """Display summary tables in the console"""
    
    print("=" * 60)
    print("SUMMARY TABLES")
    print("=" * 60)
    
    for speed_factor in SPEED_FACTORS:
        speed_results = results[speed_factor]
        
        print(f"\nSpeed Factor: {speed_factor}x")
        print("-" * 50)
        print(f"{'Reference File':<20} {'Duration':<12} {'Status':<15}")
        print("-" * 50)
        
        for ref_name in REFERENCE_AUDIO_FILES.keys():
            if ref_name in speed_results:
                result = speed_results[ref_name]
                if result['success']:
                    duration_str = f"{result['duration']:.2f}s"
                    status_str = "Success"
                else:
                    duration_str = "FAILED"
                    status_str = "Failed"
            else:
                duration_str = "N/A"
                status_str = "N/A"
            
            print(f"{ref_name:<20} {duration_str:<12} {status_str:<15}")
    
    # Overall comparison table
    print(f"\nOverall Performance Comparison")
    print("-" * 60)
    print(f"{'Reference File':<20} {'0.85x':<10} {'0.95x':<10} {'1.05x':<10} {'Average':<10}")
    print("-" * 60)
    
    for ref_name in REFERENCE_AUDIO_FILES.keys():
        row_data = [ref_name]
        durations = []
        
        for speed_factor in SPEED_FACTORS:
            if (speed_factor in results and 
                ref_name in results[speed_factor] and 
                results[speed_factor][ref_name]['success']):
                duration = results[speed_factor][ref_name]['duration']
                row_data.append(f"{duration:.2f}s")
                durations.append(duration)
            else:
                row_data.append("FAILED")
        
        # Calculate average
        if durations:
            avg_duration = sum(durations) / len(durations)
            row_data.append(f"{avg_duration:.2f}s")
        else:
            row_data.append("N/A")
        
        print(f"{row_data[0]:<20} {row_data[1]:<10} {row_data[2]:<10} {row_data[3]:<10} {row_data[4]:<10}")

def main():
    """Main function with argument parsing"""
    
    parser = argparse.ArgumentParser(
        description="Test TTS generation performance across different reference audio files"
    )
    parser.add_argument(
        "-o", "--output",
        default="2025-06-29 test_speed_reference_audio_file-B.md",
        help="Output filename for markdown report (default: 2025-06-29 test_speed_reference_audio_file-B.md)"
    )
    
    args = parser.parse_args()
    
    # Verify reference audio files exist
    # missing_files = []
    # for ref_name, file_path in REFERENCE_AUDIO_FILES.items():
    #     if not Path(file_path).exists():
    #         missing_files.append(f"{ref_name}: {file_path}")
    #
    # if missing_files:
    #     print("ERROR: Missing reference audio files:")
    #     for file in missing_files:
    #         print(f"  - {file}")
    #     print("\nPlease ensure all reference audio files are available before running the test.")
    #     print("Note: You may need to update the REFERENCE_AUDIO_FILES dictionary with your actual file paths.")
    #     return 1
    
    # Run the test
    start_time = time.time()
    results = run_reference_file_comparison_test()
    total_duration = time.time() - start_time
    
    print(f"Test completed in {format_duration(total_duration)}")
    print()
    
    # Display summary tables
    display_summary_tables(results)
    
    # Generate markdown report
    print(f"\nGenerating markdown report...")
    generate_markdown_report(results, args.output)
    
    print(f"\nTest Summary:")
    print(f"  - Total duration: {format_duration(total_duration)}")
    print(f"  - Speed factors tested: {len(SPEED_FACTORS)}")
    print(f"  - Reference files tested: {len(REFERENCE_AUDIO_FILES)}")
    print(f"  - Total requests: {len(SPEED_FACTORS) * len(REFERENCE_AUDIO_FILES)}")
    print(f"  - Report saved to: {args.output}")
    
    return 0

if __name__ == "__main__":
    exit(main())
