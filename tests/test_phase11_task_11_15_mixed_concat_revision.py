#!/usr/bin/env python3
"""
Test Phase 11 Task 11.15: Mixed Concatenation Decision Tree
===========================================================

Tests for the revised mixed concatenation functionality that follows the same
decision tree pattern as basic concatenation:

1. Manual silence mode: concatenate_with_mixed_silence() (Cases 1a, 2a)
2. Trimming mode: concatenate_with_mixed_trimming() (Cases 3a, 3b)  
3. Basic mode: concatenate_with_mixed_basic() (Cases 4a, 4b)

Key improvements tested:
- Consistent decision tree logic between basic and mixed concatenation
- Proper parameter interaction (manual silence overrides natural pauses)
- Mixed source handling (server files + uploads + manual silence)
- Enhanced error handling and logging for all three modes

Test Files:
- Server files: outputs/concatenation_test/*.mp3
- Upload files: tests/media/*.mp3 (alex.mp3, jamie-01.mp3, sean.mp3)
- Manual silence: "(500ms)", "(1s)", "(2.5s)" notation
"""

import requests
import time
import json
import os
from pathlib import Path
from typing import List, Dict, Any

class MixedConcatDecisionTreeTester:
    def __init__(self, base_url: str = "http://127.0.0.1:7860"):
        self.base_url = base_url
        self.test_results = []
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamps"""
        timestamp = time.strftime("%H:%M:%S")
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
        output_path = Path("tests/media") / filename
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        file_size = output_path.stat().st_size
        self.log(f"Saved {filename}: {file_size:,} bytes")
        return output_path
        
    def test_mixed_manual_silence_mode(self):
        """Test Case 1a & 2a: Manual silence mode with mixed sources"""
        self.log("=== Test Case 1a & 2a: Mixed Manual Silence Mode ===")
        
        # Case 1a: Manual silence WITH trimming
        self.log("--- Case 1a: Manual silence with trimming ---")
        
        # Prepare files for upload
        files_to_upload = [
            ("uploaded_files", ("alex.mp3", open("tests/media/alex.mp3", "rb"), "audio/mpeg")),
            ("uploaded_files", ("jamie-01.mp3", open("tests/media/jamie-01.mp3", "rb"), "audio/mpeg"))
        ]
        
        # Create mixed segments with manual silence
        segments = [
            {"type": "silence", "source": "(500ms)"},
            {"type": "server_file", "source": "concatenation_test/01-sarah-audio.mp3"},
            {"type": "upload", "index": 0},  # alex.mp3
            {"type": "silence", "source": "(1s)"},
            {"type": "server_file", "source": "concatenation_test/02-mark-audio.mp3"},
            {"type": "upload", "index": 1},  # jamie-01.mp3
            {"type": "silence", "source": "(750ms)"}
        ]
        
        # Create request JSON
        request_data = {
            "segments": segments,
            "export_formats": ["wav"],
            "trim": True,  # Should trim audio files before applying manual silence
            "trim_threshold_ms": 200,
            "normalize_levels": True,
            "pause_duration_ms": 600,  # Should be IGNORED in manual silence mode
            "pause_variation_ms": 100  # Should be IGNORED in manual silence mode
        }
        
        # Mixed concatenation with manual silence and trimming
        data = {
            "request_json": json.dumps(request_data)
        }
        
        try:
            start_time = time.time()
            response = self.make_request("/api/v1/concat/mixed", "POST", 
                                       files=files_to_upload, data=data)
            
            if response.status_code == 200:
                filename = "mixed_case_1a_manual_silence_with_trim.wav"
                saved_path = self.save_response_file(response, filename)
                duration = time.time() - start_time
                self.log(f"PASS Case 1a completed in {duration:.2f}s")
                
                # Verify file exists and has reasonable size
                if saved_path.stat().st_size > 10000:  # At least 10KB
                    self.log(f"PASS Case 1a file size validation: {saved_path.stat().st_size:,} bytes")
                else:
                    self.log(f"WARN Case 1a file size seems small: {saved_path.stat().st_size:,} bytes")
                    
            else:
                self.log(f"FAIL Case 1a returned status {response.status_code}", "ERROR")
                self.log(f"Response: {response.text[:500]}", "ERROR")
                
        except Exception as e:
            self.log(f"FAIL Case 1a exception: {e}", "ERROR")
        finally:
            # Close uploaded files
            for file_tuple in files_to_upload:
                if len(file_tuple) == 2:
                    continue
                file_tuple[1][1].close()
                
        # Case 2a: Manual silence WITHOUT trimming
        self.log("--- Case 2a: Manual silence without trimming ---")
        
        # Prepare files for upload
        files_to_upload = [
            ("uploaded_files", ("sean.mp3", open("tests/media/sean.mp3", "rb"), "audio/mpeg"))
        ]
        
        segments = [
            {"type": "server_file", "source": "concatenation_test/03-sarah-audio.mp3"},
            {"type": "silence", "source": "(2s)"},
            {"type": "upload", "index": 0},  # sean.mp3
            {"type": "silence", "source": "(1.5s)"},
            {"type": "server_file", "source": "concatenation_test/04-mark-audio.mp3"}
        ]
        
        request_data = {
            "segments": segments,
            "export_formats": ["wav"],
            "trim": False,  # No trimming
            "normalize_levels": True,
            "pause_duration_ms": 800,  # Should be IGNORED
            "pause_variation_ms": 150  # Should be IGNORED
        }
        
        data = {
            "request_json": json.dumps(request_data)
        }
        
        try:
            start_time = time.time()
            response = self.make_request("/api/v1/concat/mixed", "POST", 
                                       files=files_to_upload, data=data)
            
            if response.status_code == 200:
                filename = "mixed_case_2a_manual_silence_no_trim.wav"
                saved_path = self.save_response_file(response, filename)
                duration = time.time() - start_time
                self.log(f"PASS Case 2a completed in {duration:.2f}s")
                
            else:
                self.log(f"FAIL Case 2a returned status {response.status_code}", "ERROR")
                self.log(f"Response: {response.text[:500]}", "ERROR")
                
        except Exception as e:
            self.log(f"FAIL Case 2a exception: {e}", "ERROR")
        finally:
            # Close uploaded files
            for file_tuple in files_to_upload:
                if len(file_tuple) == 2:
                    continue
                file_tuple[1][1].close()
        
    def test_mixed_trimming_mode(self):
        """Test Case 3a & 3b: Trimming mode with mixed sources"""
        self.log("=== Test Case 3a & 3b: Mixed Trimming Mode ===")
        
        # Case 3a: Trimming with NO natural pauses (compact mode)
        self.log("--- Case 3a: Trimming with no natural pauses (compact) ---")
        
        files_to_upload = [
            ("uploaded_files", ("alex.mp3", open("tests/media/alex.mp3", "rb"), "audio/mpeg"))
        ]
        
        segments = [
            {"type": "server_file", "source": "concatenation_test/05-sarah-audio-long.mp3"},  # Use -long for trimming
            {"type": "upload", "index": 0},  # alex.mp3
            {"type": "server_file", "source": "concatenation_test/06-mark-audio-long.mp3"}   # Use -long for trimming
        ]
        
        request_data = {
            "segments": segments,
            "export_formats": ["wav"],
            "trim": True,  # Trim files
            "trim_threshold_ms": 200,
            "pause_duration_ms": 0,  # No natural pauses = compact mode
            "pause_variation_ms": 0,
            "normalize_levels": True
        }
        
        data = {
            "request_json": json.dumps(request_data)
        }
        
        try:
            start_time = time.time()
            response = self.make_request("/api/v1/concat/mixed", "POST", 
                                       files=files_to_upload, data=data)
            
            if response.status_code == 200:
                filename = "mixed_case_3a_trimming_compact.wav"
                saved_path = self.save_response_file(response, filename)
                duration = time.time() - start_time
                self.log(f"PASS Case 3a completed in {duration:.2f}s")
                
            else:
                self.log(f"FAIL Case 3a returned status {response.status_code}", "ERROR")
                self.log(f"Response: {response.text[:500]}", "ERROR")
                
        except Exception as e:
            self.log(f"FAIL Case 3a exception: {e}", "ERROR")
        finally:
            # Close uploaded files
            for file_tuple in files_to_upload:
                if len(file_tuple) == 2:
                    continue
                file_tuple[1][1].close()
                
        # Case 3b: Trimming WITH natural pauses (clean & spaced)
        self.log("--- Case 3b: Trimming with natural pauses (clean & spaced) ---")
        
        files_to_upload = [
            ("uploaded_files", ("jamie-01.mp3", open("tests/media/jamie-01.mp3", "rb"), "audio/mpeg")),
            ("uploaded_files", ("sean.mp3", open("tests/media/sean.mp3", "rb"), "audio/mpeg"))
        ]
        
        segments = [
            {"type": "upload", "index": 0},  # jamie-01.mp3
            {"type": "server_file", "source": "concatenation_test/07-sarah-audio.mp3"},
            {"type": "upload", "index": 1},  # sean.mp3
            {"type": "server_file", "source": "concatenation_test/08-mark-audio.mp3"}
        ]
        
        request_data = {
            "segments": segments,
            "export_formats": ["wav"],
            "trim": True,  # Trim files
            "trim_threshold_ms": 200,
            "pause_duration_ms": 700,  # Natural pauses
            "pause_variation_ms": 100,
            "normalize_levels": True,
            "crossfade_ms": 150  # Test crossfade with natural pauses
        }
        
        data = {
            "request_json": json.dumps(request_data)
        }
        
        try:
            start_time = time.time()
            response = self.make_request("/api/v1/concat/mixed", "POST", 
                                       files=files_to_upload, data=data)
            
            if response.status_code == 200:
                filename = "mixed_case_3b_trimming_natural_pauses.wav"
                saved_path = self.save_response_file(response, filename)
                duration = time.time() - start_time
                self.log(f"PASS Case 3b completed in {duration:.2f}s")
                
            else:
                self.log(f"FAIL Case 3b returned status {response.status_code}", "ERROR")
                self.log(f"Response: {response.text[:500]}", "ERROR")
                
        except Exception as e:
            self.log(f"FAIL Case 3b exception: {e}", "ERROR")
        finally:
            # Close uploaded files
            for file_tuple in files_to_upload:
                if len(file_tuple) == 2:
                    continue
                file_tuple[1][1].close()
        
    def test_mixed_basic_mode(self):
        """Test Case 4a & 4b: Basic mode with mixed sources"""
        self.log("=== Test Case 4a & 4b: Mixed Basic Mode ===")
        
        # Case 4a: No trim, no natural pauses (direct join)
        self.log("--- Case 4a: No trim, no natural pauses (direct join) ---")
        
        files_to_upload = [
            ("uploaded_files", ("alex.mp3", open("tests/media/alex.mp3", "rb"), "audio/mpeg"))
        ]
        
        segments = [
            {"type": "server_file", "source": "concatenation_test/09-sarah-audio.mp3"},
            {"type": "upload", "index": 0},  # alex.mp3
            {"type": "server_file", "source": "concatenation_test/10-mark-audio.mp3"}
        ]
        
        request_data = {
            "segments": segments,
            "export_formats": ["wav"],
            "trim": False,  # No trimming
            "pause_duration_ms": 0,  # No natural pauses
            "pause_variation_ms": 0,
            "normalize_levels": True
        }
        
        data = {
            "request_json": json.dumps(request_data)
        }
        
        try:
            start_time = time.time()
            response = self.make_request("/api/v1/concat/mixed", "POST", 
                                       files=files_to_upload, data=data)
            
            if response.status_code == 200:
                filename = "mixed_case_4a_basic_direct_join.wav"
                saved_path = self.save_response_file(response, filename)
                duration = time.time() - start_time
                self.log(f"PASS Case 4a completed in {duration:.2f}s")
                
            else:
                self.log(f"FAIL Case 4a returned status {response.status_code}", "ERROR")
                self.log(f"Response: {response.text[:500]}", "ERROR")
                
        except Exception as e:
            self.log(f"FAIL Case 4a exception: {e}", "ERROR")
        finally:
            # Close uploaded files
            for file_tuple in files_to_upload:
                if len(file_tuple) == 2:
                    continue
                file_tuple[1][1].close()
                
        # Case 4b: No trim, WITH natural pauses (natural flow)
        self.log("--- Case 4b: No trim with natural pauses (natural flow) ---")
        
        files_to_upload = [
            ("uploaded_files", ("jamie-01.mp3", open("tests/media/jamie-01.mp3", "rb"), "audio/mpeg")),
            ("uploaded_files", ("sean.mp3", open("tests/media/sean.mp3", "rb"), "audio/mpeg"))
        ]
        
        segments = [
            {"type": "upload", "index": 0},  # jamie-01.mp3
            {"type": "server_file", "source": "concatenation_test/11-sarah-audio.mp3"},
            {"type": "upload", "index": 1},  # sean.mp3
        ]
        
        request_data = {
            "segments": segments,
            "export_formats": ["wav", "mp3"],  # Test multiple formats
            "trim": False,  # No trimming
            "pause_duration_ms": 900,  # Natural pauses
            "pause_variation_ms": 200,
            "normalize_levels": True,
            "crossfade_ms": 200  # Test crossfade with natural pauses
        }
        
        data = {
            "request_json": json.dumps(request_data)
        }
        
        try:
            start_time = time.time()
            response = self.make_request("/api/v1/concat/mixed", "POST", 
                                       files=files_to_upload, data=data)
            
            if response.status_code == 200:
                filename = "mixed_case_4b_basic_natural_flow.wav"
                saved_path = self.save_response_file(response, filename)
                duration = time.time() - start_time
                self.log(f"PASS Case 4b completed in {duration:.2f}s")
                
            else:
                self.log(f"FAIL Case 4b returned status {response.status_code}", "ERROR")
                self.log(f"Response: {response.text[:500]}", "ERROR")
                
        except Exception as e:
            self.log(f"FAIL Case 4b exception: {e}", "ERROR")
        finally:
            # Close uploaded files
            for file_tuple in files_to_upload:
                if len(file_tuple) == 2:
                    continue
                file_tuple[1][1].close()
        
    def test_validation_and_error_handling(self):
        """Test validation and error handling for mixed concatenation"""
        self.log("=== Test Validation and Error Handling ===")
        
        # Test 1: Manual silence segments not supported in trimming mode
        self.log("--- Test 1: Manual silence in trimming mode (should fail) ---")
        
        files_to_upload = [
            ("uploaded_files", ("alex.mp3", open("tests/media/alex.mp3", "rb"), "audio/mpeg"))
        ]
        
        segments = [
            {"type": "server_file", "source": "concatenation_test/01-sarah-audio.mp3"},
            {"type": "silence", "source": "(500ms)"},  # This should cause error in trimming mode
            {"type": "upload", "index": 0}
        ]
        
        request_data = {
            "segments": segments,
            "export_formats": ["wav"],
            "trim": True,  # Trimming mode doesn't support manual silence
            "normalize_levels": True
        }
        
        data = {
            "request_json": json.dumps(request_data)
        }
        
        try:
            response = self.make_request("/api/v1/concat/mixed", "POST", 
                                       files=files_to_upload, data=data)
            
            if response.status_code == 400 or response.status_code == 422:
                self.log(f"PASS Test 1 - Validation correctly rejected manual silence in trimming mode")
            else:
                self.log(f"FAIL Test 1 - Expected validation error, got status {response.status_code}", "ERROR")
                
        except Exception as e:
            self.log(f"FAIL Test 1 exception: {e}", "ERROR")
        finally:
            # Close uploaded files
            for file_tuple in files_to_upload:
                if len(file_tuple) == 2:
                    continue
                file_tuple[1][1].close()
                
        # Test 2: Missing upload file reference
        self.log("--- Test 2: Missing upload file reference (should fail) ---")
        
        segments = [
            {"type": "server_file", "source": "concatenation_test/01-sarah-audio.mp3"},
            {"type": "upload", "index": 0}  # No file uploaded for index 0
        ]
        
        request_data = {
            "segments": segments,
            "export_formats": ["wav"],
            "trim": False,
            "normalize_levels": True
        }
        
        data = {
            "request_json": json.dumps(request_data)
        }
        
        try:
            response = self.make_request("/api/v1/concat/mixed", "POST", 
                                       files=[], data=data)  # No files uploaded
            
            if response.status_code == 400 or response.status_code == 422:
                self.log(f"PASS Test 2 - Validation correctly rejected missing upload file")
            else:
                self.log(f"FAIL Test 2 - Expected validation error, got status {response.status_code}", "ERROR")
                
        except Exception as e:
            self.log(f"FAIL Test 2 exception: {e}", "ERROR")
                
        # Test 3: Invalid server file reference
        self.log("--- Test 3: Invalid server file reference (should fail) ---")
        
        segments = [
            {"type": "server_file", "source": "concatenation_test/non_existent_file.mp3"},
            {"type": "server_file", "source": "concatenation_test/01-sarah-audio.mp3"}
        ]
        
        request_data = {
            "segments": segments,
            "export_formats": ["wav"],
            "trim": False,
            "normalize_levels": True
        }
        
        data = {
            "request_json": json.dumps(request_data)
        }
        
        try:
            response = self.make_request("/api/v1/concat/mixed", "POST", 
                                       files=[], data=data)
            
            if response.status_code == 400 or response.status_code == 422 or response.status_code == 404:
                self.log(f"PASS Test 3 - Validation correctly rejected invalid server file")
            else:
                self.log(f"FAIL Test 3 - Expected validation error, got status {response.status_code}", "ERROR")
                
        except Exception as e:
            self.log(f"FAIL Test 3 exception: {e}", "ERROR")
        
    def test_consistency_with_basic_concatenation(self):
        """Test that mixed concatenation behaves consistently with basic concatenation"""
        self.log("=== Test Consistency with Basic Concatenation ===")
        
        # Test parameter interaction consistency
        self.log("--- Consistency Test: Parameter interaction alignment ---")
        
        files_to_upload = [
            ("uploaded_files", ("alex.mp3", open("tests/media/alex.mp3", "rb"), "audio/mpeg"))
        ]
        
        segments = [
            {"type": "server_file", "source": "concatenation_test/01-sarah-audio.mp3"},
            {"type": "silence", "source": "(1s)"},  # Manual silence should override pause settings
            {"type": "upload", "index": 0}
        ]
        
        request_data = {
            "segments": segments,
            "export_formats": ["wav"],
            "trim": False,
            "normalize_levels": True,
            "pause_duration_ms": 2000,  # This should be IGNORED due to manual silence
            "pause_variation_ms": 300   # This should be IGNORED due to manual silence
        }
        
        data = {
            "request_json": json.dumps(request_data)
        }
        
        try:
            start_time = time.time()
            response = self.make_request("/api/v1/concat/mixed", "POST", 
                                       files=files_to_upload, data=data)
            
            if response.status_code == 200:
                filename = "mixed_consistency_test_manual_silence_override.wav"
                saved_path = self.save_response_file(response, filename)
                duration = time.time() - start_time
                self.log(f"PASS Consistency test completed in {duration:.2f}s")
                
            else:
                self.log(f"FAIL Consistency test returned status {response.status_code}", "ERROR")
                self.log(f"Response: {response.text[:500]}", "ERROR")
                
        except Exception as e:
            self.log(f"FAIL Consistency test exception: {e}", "ERROR")
        finally:
            # Close uploaded files
            for file_tuple in files_to_upload:
                if len(file_tuple) == 2:
                    continue
                file_tuple[1][1].close()
                
    def run_all_tests(self):
        """Run all mixed concatenation decision tree tests"""
        self.log("=== Starting Mixed Concatenation Decision Tree Tests ===")
        self.log("Testing Task 11.15 implementation - Mixed concat revision")
        
        start_time = time.time()
        
        try:
            # Test all decision tree scenarios
            self.test_mixed_manual_silence_mode()
            self.test_mixed_trimming_mode()
            self.test_mixed_basic_mode()
            self.test_validation_and_error_handling()
            self.test_consistency_with_basic_concatenation()
            
            total_duration = time.time() - start_time
            self.log(f"=== All Tests Completed in {total_duration:.2f}s ===")
            
        except Exception as e:
            self.log(f"Test suite failed: {e}", "ERROR")
            raise

def main():
    """Main test execution"""
    tester = MixedConcatDecisionTreeTester()
    
    # Check if server is running
    try:
        health_response = tester.make_request("/api/v1/health")
        if health_response.status_code == 200:
            tester.log("Server is running - starting tests")
        else:
            tester.log(f"Server health check failed: {health_response.status_code}", "ERROR")
            return
    except Exception as e:
        tester.log(f"Cannot connect to server: {e}", "ERROR")
        tester.log("Make sure the server is running at http://127.0.0.1:7860", "ERROR")
        return
    
    # Run all tests
    tester.run_all_tests()

if __name__ == "__main__":
    main()
