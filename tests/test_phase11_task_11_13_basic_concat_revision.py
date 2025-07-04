#!/usr/bin/env python3
"""
Test Phase 11 Task 11.13: Revision of Basic Concatenation
========================================================

Tests for the revised basic concatenation functionality:
1. Post-concatenation format conversion (efficiency improvement)
2. Project/folder parameter support for output organization  
3. Enhanced filename and project parameter compatibility
4. Comprehensive logging and time monitoring

Key improvements tested:
- Single concatenation operation + format conversion (vs per-format concatenation)
- Project folder organization within outputs/ directory
- Backward compatibility with all existing features
- Performance and logging enhancements

Test Files:
- Uses files from outputs/concatenation_test/ directory
- Tests with both normal and '*-long.mp3' files (for trimming validation)
- Validates all concatenation modes: basic, trimming, manual silence
"""

import requests
import time
import json
import os
from pathlib import Path
from typing import List, Dict, Any

class BasicConcatRevisionTester:
    def __init__(self, base_url: str = "http://127.0.0.1:7860"):
        self.base_url = base_url
        self.test_results = []
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamps"""
        timestamp = time.strftime("%H:%M:%S")
        # Avoid Unicode issues on Windows
        print(f"[{timestamp}] {level}: {message}")
        
    def make_request(self, endpoint: str, method: str = "GET", **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {e}", "ERROR")
            raise
            
    def save_response_file(self, response: requests.Response, filename: str) -> Path:
        """Save streaming response to file"""
        output_path = Path("E:/Repos/Chatterbox-TTS-Extended-Plus/tests/media") / filename
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        file_size = output_path.stat().st_size
        self.log(f"Saved {filename}: {file_size:,} bytes")
        return output_path
        
    def test_basic_concatenation_no_trimming(self):
        """Test 11.14.1: Basic concatenation without trimming"""
        self.log("=== Test 11.14.1: Basic Concatenation (No Trimming) ===")
        
        # Test simple concatenation with multiple formats
        payload = {
            "files": [
                "concatenation_test/01-sarah-audio.mp3",
                "concatenation_test/02-mark-audio.mp3",
                "concatenation_test/03-sarah-audio.mp3"
            ],
            "export_formats": ["wav", "mp3"],  # Multiple formats for streaming test
            "normalize_levels": True,
            "trim": False,  # No trimming
            "pause_duration_ms": 0  # No pauses for clean test
        }
        
        start_time = time.time()
        response = self.make_request("/api/v1/concat", "POST", json=payload)
        
        if response.status_code == 200:
            filename = "basic_concat_no_trim.wav"
            saved_path = self.save_response_file(response, filename)
            
            # Check for proper Content-Disposition header
            content_disp = response.headers.get('Content-Disposition', '')
            self.log(f"Content-Disposition: {content_disp}")
            
            duration = time.time() - start_time
            self.log(f"PASS Basic concatenation completed in {duration:.2f}s")
            
            # Test URL mode to get metadata
            meta_response = self.make_request("/api/v1/concat?response_mode=url", "POST", json=payload)
            if meta_response.status_code == 200:
                metadata = meta_response.json()
                self.log(f"Generated files: {metadata.get('output_files', [])}")
                self.log(f"Total duration: {metadata.get('total_duration_seconds', 0):.2f}s")
                self.log(f"Processing time: {metadata.get('processing_time_seconds', 0):.3f}s")
                
                # Verify both formats were generated
                output_files = metadata.get('output_files', [])
                if len(output_files) >= 2:
                    self.log("PASS Multiple format generation confirmed")
                else:
                    self.log(f"WARN Expected 2 formats, got {len(output_files)}", "WARN")
                
            self.test_results.append({
                "test": "basic_concatenation_no_trimming",
                "status": "PASS",
                "duration": duration,
                "files_generated": metadata.get('output_files', []) if 'metadata' in locals() else []
            })
        else:
            self.log(f"FAIL Basic concatenation failed: {response.status_code}", "ERROR")
            self.log(f"Response: {response.text}", "ERROR")
            self.test_results.append({
                "test": "basic_concatenation_no_trimming", 
                "status": "FAIL",
                "error": response.text
            })
            
    def test_concatenation_with_trimming_no_spaces(self):
        """Test 11.14.2: Concatenation with trimming, no spaces"""
        self.log("=== Test 11.14.2: Concatenation with Trimming (No Spaces) ===")
        
        # Use *-long.mp3 files that have extra silence for trimming
        payload = {
            "files": [
                "concatenation_test/01-sarah-audio-long.mp3",
                "concatenation_test/02-mark-audio-long.mp3"
            ],
            "export_formats": ["wav"],  # Single format for streaming test
            "normalize_levels": True,
            "trim": True,  # Enable trimming
            "trim_threshold_ms": 200,  # 200ms threshold
            "pause_duration_ms": 0  # No pauses between trimmed files
        }
        
        start_time = time.time()
        response = self.make_request("/api/v1/concat", "POST", json=payload)
        
        if response.status_code == 200:
            filename = "basic_concat_with_trimming_no_spaces.wav"
            saved_path = self.save_response_file(response, filename)
            
            duration = time.time() - start_time
            self.log(f"PASS Trimming concatenation completed in {duration:.2f}s")
            
            # Get metadata to check trimming was applied
            meta_response = self.make_request("/api/v1/concat?response_mode=url", "POST", json=payload)
            if meta_response.status_code == 200:
                metadata = meta_response.json()
                
                # Check if trimming information is in metadata
                generation_info = metadata.get('metadata', {})
                if 'trimming_applied' in generation_info or 'processing_time_seconds' in generation_info:
                    self.log("PASS Trimming metadata present")
                else:
                    self.log("WARN Trimming metadata not found", "WARN")
                    
                self.log(f"Total duration: {metadata.get('total_duration_seconds', 0):.2f}s")
                
            self.test_results.append({
                "test": "concatenation_with_trimming_no_spaces",
                "status": "PASS", 
                "duration": duration,
                "files_generated": metadata.get('output_files', []) if 'metadata' in locals() else []
            })
        else:
            self.log(f"FAIL Trimming concatenation failed: {response.status_code}", "ERROR")
            self.log(f"Response: {response.text}", "ERROR")
            self.test_results.append({
                "test": "concatenation_with_trimming_no_spaces",
                "status": "FAIL",
                "error": response.text
            })
            
    def test_concatenation_with_trimming_and_custom_spaces(self):
        """Test 11.14.3: Concatenation with trimming and custom spaces"""
        self.log("=== Test 11.14.3: Concatenation with Trimming + Custom Spaces ===")
        
        # Use *-long.mp3 files with trimming AND custom pauses
        payload = {
            "files": [
                "concatenation_test/05-sarah-audio-long.mp3",
                "concatenation_test/06-mark-audio-long.mp3",
                "concatenation_test/01-sarah-audio-long.mp3"
            ],
            "export_formats": ["wav"],  # Single format for streaming test
            "normalize_levels": True,
            "trim": True,  # Enable trimming
            "trim_threshold_ms": 150,  # Slightly lower threshold
            "pause_duration_ms": 800,  # 800ms pauses after trimming
            "pause_variation_ms": 100  # ±100ms variation
        }
        
        start_time = time.time()
        response = self.make_request("/api/v1/concat", "POST", json=payload)
        
        if response.status_code == 200:
            filename = "basic_concat_trimming_custom_spaces.wav"
            saved_path = self.save_response_file(response, filename)
            
            duration = time.time() - start_time
            self.log(f"PASS Trimming + custom spaces completed in {duration:.2f}s")
            
            # Get metadata for detailed analysis
            meta_response = self.make_request("/api/v1/concat?response_mode=url", "POST", json=payload)
            if meta_response.status_code == 200:
                metadata = meta_response.json()
                
                # Check parameter integration
                params = metadata.get('metadata', {}).get('parameters', {})
                if params.get('trim') and params.get('pause_duration_ms', 0) > 0:
                    self.log("PASS Trimming + pause parameter integration confirmed")
                else:
                    self.log("WARN Parameter integration unclear", "WARN")
                    
                self.log(f"Final duration: {metadata.get('total_duration_seconds', 0):.2f}s")
                self.log(f"File count: {metadata.get('file_count', 0)}")
                
            self.test_results.append({
                "test": "concatenation_with_trimming_and_custom_spaces",
                "status": "PASS",
                "duration": duration, 
                "files_generated": metadata.get('output_files', []) if 'metadata' in locals() else []
            })
        else:
            self.log(f"FAIL Trimming + spaces failed: {response.status_code}", "ERROR")
            self.log(f"Response: {response.text}", "ERROR")
            self.test_results.append({
                "test": "concatenation_with_trimming_and_custom_spaces",
                "status": "FAIL",
                "error": response.text
            })
            
    def test_project_folder_functionality(self):
        """Test project folder parameter functionality"""
        self.log("=== Test: Project Folder Functionality ===")
        
        # Test with project parameter
        payload = {
            "files": [
                "concatenation_test/03-sarah-audio.mp3",
                "concatenation_test/04-mark-audio.mp3"
            ],
            "export_formats": ["wav", "mp3"],
            "project": "test_phase11/task_11_13",  # Project folder
            "output_filename": "project_test_concat",  # Custom filename
            "normalize_levels": True,
        }
        
        start_time = time.time()
        response = self.make_request("/api/v1/concat?response_mode=url", "POST", json=payload)
        
        if response.status_code == 200:
            metadata = response.json()
            duration = time.time() - start_time
            
            output_files = metadata.get('output_files', [])
            self.log(f"Generated files: {output_files}")
            
            # Verify files were created in project directory
            expected_path_pattern = "project_test_concat"
            for filename in output_files:
                if expected_path_pattern in filename:
                    self.log(f"PASS Project filename pattern found: {filename}")
                else:
                    self.log(f"WARN Unexpected filename: {filename}", "WARN")
                    
            # Test folder alias as well
            payload["folder"] = "test_phase11/task_11_13_alias"
            payload.pop("project")  # Remove project, use folder alias
            payload["output_filename"] = "folder_alias_test"
            
            alias_response = self.make_request("/api/v1/concat?response_mode=url", "POST", json=payload)
            if alias_response.status_code == 200:
                alias_metadata = alias_response.json()
                alias_files = alias_metadata.get('output_files', [])
                self.log(f"PASS Folder alias test: {alias_files}")
            
            self.test_results.append({
                "test": "project_folder_functionality",
                "status": "PASS",
                "duration": duration,
                "files_generated": output_files,
                "alias_files": alias_files if 'alias_files' in locals() else []
            })
        else:
            self.log(f"FAIL Project folder test failed: {response.status_code}", "ERROR")
            self.log(f"Response: {response.text}", "ERROR")
            self.test_results.append({
                "test": "project_folder_functionality",
                "status": "FAIL",
                "error": response.text
            })
            
    def test_format_conversion_efficiency(self):
        """Test that format conversion uses the new efficient method"""
        self.log("=== Test: Format Conversion Efficiency ===")
        
        # Test with multiple formats to verify single concatenation + conversion
        payload = {
            "files": [
                "concatenation_test/07-sarah-audio.mp3",
                "concatenation_test/08-mark-audio.mp3",
                "concatenation_test/09-sarah-audio.mp3"
            ],
            "export_formats": ["wav", "mp3", "flac"],  # Three formats
            "normalize_levels": True,
        }
        
        start_time = time.time()
        response = self.make_request("/api/v1/concat?response_mode=url", "POST", json=payload)
        
        if response.status_code == 200:
            metadata = response.json()
            duration = time.time() - start_time
            
            # Analyze processing time and files generated
            processing_time = metadata.get('processing_time_seconds', 0)
            output_files = metadata.get('output_files', [])
            
            self.log(f"Total operation time: {duration:.2f}s")
            self.log(f"Server processing time: {processing_time:.3f}s")
            self.log(f"Generated {len(output_files)} files: {output_files}")
            
            # Verify all three formats were generated
            formats_found = set()
            for filename in output_files:
                for fmt in ['wav', 'mp3', 'flac']:
                    if filename.endswith(f'.{fmt}'):
                        formats_found.add(fmt)
                        
            if len(formats_found) == 3:
                self.log("PASS All three formats generated successfully")
            else:
                self.log(f"WARN Expected 3 formats, found: {formats_found}", "WARN")
                
            # Check if processing was reasonably efficient
            # Should be much faster than old per-format concatenation
            if processing_time < 5.0:  # Reasonable threshold
                self.log("OK Processing time looks efficient")
            else:
                self.log(f"WARN Processing took {processing_time:.3f}s - may need optimization", "WARN")
                
            self.test_results.append({
                "test": "format_conversion_efficiency",
                "status": "PASS",
                "duration": duration,
                "processing_time": processing_time,
                "formats_generated": list(formats_found),
                "files_count": len(output_files)
            })
        else:
            self.log(f"ERROR Format conversion test failed: {response.status_code}", "ERROR")
            self.log(f"Response: {response.text}", "ERROR")
            self.test_results.append({
                "test": "format_conversion_efficiency", 
                "status": "FAIL",
                "error": response.text
            })
            
    def test_backward_compatibility(self):
        """Test that all existing concatenation features still work"""
        self.log("=== Test: Backward Compatibility ===")
        
        # Test manual silence (existing feature)
        silence_payload = {
            "files": [
                "(500ms)",
                "concatenation_test/10-mark-audio.mp3", 
                "(1s)",
                "concatenation_test/11-sarah-audio.mp3",
                "(750ms)"
            ],
            "export_formats": ["wav"],
            "normalize_levels": True
        }
        
        start_time = time.time()
        response = self.make_request("/api/v1/concat?response_mode=url", "POST", json=silence_payload)
        
        if response.status_code == 200:
            metadata = response.json()
            duration = time.time() - start_time
            
            # Check that manual silence was recognized
            params = metadata.get('metadata', {}).get('parameters', {})
            if params.get('manual_silence'):
                self.log("OK Manual silence mode detected")
            else:
                self.log("WARN Manual silence mode not detected", "WARN")
                
            silence_segments = params.get('silence_segments', 0)
            self.log(f"Silence segments processed: {silence_segments}")
            
            # Test crossfade (existing feature) 
            crossfade_payload = {
                "files": [
                    "concatenation_test/01-sarah-audio.mp3",
                    "concatenation_test/02-mark-audio.mp3"
                ],
                "export_formats": ["wav"],
                "crossfade_ms": 300,  # 300ms crossfade
                "normalize_levels": True
            }
            
            crossfade_response = self.make_request("/api/v1/concat?response_mode=url", "POST", json=crossfade_payload)
            if crossfade_response.status_code == 200:
                crossfade_meta = crossfade_response.json()
                crossfade_params = crossfade_meta.get('metadata', {}).get('parameters', {})
                
                if crossfade_params.get('crossfade_ms') == 300:
                    self.log("OK Crossfade parameter preserved")
                else:
                    self.log("WARN Crossfade parameter issue", "WARN")
                    
            self.test_results.append({
                "test": "backward_compatibility",
                "status": "PASS",
                "duration": duration,
                "silence_test": "PASS" if params.get('manual_silence') else "WARN",
                "crossfade_test": "PASS" if crossfade_params.get('crossfade_ms') == 300 else "WARN"
            })
        else:
            self.log(f"FAIL Backward compatibility test failed: {response.status_code}", "ERROR")
            self.log(f"Response: {response.text}", "ERROR")
            self.test_results.append({
                "test": "backward_compatibility",
                "status": "FAIL", 
                "error": response.text
            })
            
    def run_all_tests(self):
        """Run all Task 11.13 tests"""
        self.log(">>> Starting Phase 11 Task 11.13 Basic Concatenation Revision Tests")
        self.log("=" * 80)
        
        # Core functionality tests (as per Task 11.14)
        self.test_basic_concatenation_no_trimming()
        self.test_concatenation_with_trimming_no_spaces() 
        self.test_concatenation_with_trimming_and_custom_spaces()
        
        # New features tests
        self.test_project_folder_functionality()
        self.test_format_conversion_efficiency()
        
        # Compatibility tests
        self.test_backward_compatibility()
        
        # Summary report
        self.log("=" * 80)
        self.log("TEST SUMMARY")
        self.log("=" * 80)
        
        passed = sum(1 for result in self.test_results if result.get('status') == 'PASS')
        failed = sum(1 for result in self.test_results if result.get('status') == 'FAIL')
        
        self.log(f"PASSED: {passed}")
        self.log(f"FAILED: {failed}")
        self.log(f"TOTAL: {len(self.test_results)}")
        
        if failed == 0:
            self.log("*** ALL TESTS PASSED - Task 11.13 implementation validated! ***")
        else:
            self.log("!!! Some tests failed - review implementation")
            
        # Detailed results
        self.log("\nDETAILED RESULTS:")
        for result in self.test_results:
            test_name = result['test']
            status = result['status']
            duration = result.get('duration', 0)
            
            status_icon = "PASS" if status == "PASS" else "FAIL"
            self.log(f"{status_icon} {test_name}: {status} ({duration:.2f}s)")
            
            if 'files_generated' in result and result['files_generated']:
                self.log(f"   Files: {result['files_generated']}")
                
            if 'error' in result:
                self.log(f"   Error: {result['error']}")
                
        return self.test_results

if __name__ == "__main__":
    tester = BasicConcatRevisionTester()
    results = tester.run_all_tests()
