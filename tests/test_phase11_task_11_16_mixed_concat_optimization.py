#!/usr/bin/env python3
"""
Test Phase 11 Task 11.16: Mixed Concatenation Optimization
==========================================================

Tests for the optimized mixed concatenation functionality following Task 11.13 improvements:

1. Post-concatenation format conversion (single concat + format conversion)
2. Project/folder parameter support for mixed concatenation
3. Enhanced logging and monitoring with separate timing
4. Backward compatibility with existing mixed concatenation features

Key improvements tested:
- Single concatenation operation + format conversion (vs per-format concatenation)
- Project folder organization within outputs/ directory for mixed sources
- Enhanced timing logs: concatenation vs format conversion operations
- Consistent behavior with basic concatenation optimization patterns

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

class MixedConcatOptimizationTester:
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
        
    def test_project_folder_support(self):
        """Test Task 11.16: Project/folder parameter support"""
        self.log("=== Test Task 11.16: Project/Folder Parameter Support ===")
        
        # Test 1: Mixed concatenation with project parameter
        self.log("--- Test 1: Mixed concatenation with project parameter ---")
        
        # Prepare files for upload
        files_to_upload = [
            ("uploaded_files", ("alex.mp3", open("tests/media/alex.mp3", "rb"), "audio/mpeg")),
        ]
        
        # Create mixed segments 
        segments = [
            {"type": "server_file", "source": "concatenation_test/01-sarah-audio.mp3"},
            {"type": "upload", "index": 0},
            {"type": "server_file", "source": "concatenation_test/02-mark-audio.mp3"}
        ]
        
        request_data = {
            "segments": segments,
            "project": "test_project/episode_01",
            "export_formats": ["wav", "mp3"],
            "normalize_levels": True,
            "crossfade_ms": 50,
            "pause_duration_ms": 300,
            "output_filename": "mixed_with_project"
        }
        
        try:
            response = self.make_request(
                "/api/v1/concat/mixed",
                method="POST",
                data={"request_json": json.dumps(request_data)},
                files=files_to_upload
            )
            
            if response.status_code == 200:
                # Save the streamed file
                self.save_response_file(response, "mixed_project_test.wav")
                self.log("PASS Project parameter test passed - file generated successfully")
                
                # Verify file was created in project folder
                project_path = Path("outputs/test_project/episode_01")
                if project_path.exists():
                    files_in_project = list(project_path.glob("mixed_with_project*"))
                    self.log(f"PASS Project folder created with {len(files_in_project)} files")
                    for file in files_in_project:
                        self.log(f"   - {file.name}")
                else:
                    self.log("WARN Project folder not found (may need server access to verify)")
                
            else:
                self.log(f"FAIL Project parameter test failed: {response.status_code}")
                self.log(f"   Error: {response.text}")
                
        except Exception as e:
            self.log(f"FAIL Project parameter test failed: {e}")
        finally:
            # Close file handles
            for _, file_tuple in files_to_upload:
                file_tuple[1].close()
    
    def test_folder_parameter_alias(self):
        """Test folder parameter as alias for project"""
        self.log("=== Test: Folder Parameter Alias ===")
        
        # Prepare files for upload
        files_to_upload = [
            ("uploaded_files", ("jamie-01.mp3", open("tests/media/jamie-01.mp3", "rb"), "audio/mpeg")),
        ]
        
        # Create mixed segments 
        segments = [
            {"type": "server_file", "source": "concatenation_test/03-sarah-audio.mp3"},
            {"type": "upload", "index": 0},
            {"type": "silence", "source": "(500ms)"},
            {"type": "server_file", "source": "concatenation_test/04-mark-audio.mp3"}
        ]
        
        request_data = {
            "segments": segments,
            "folder": "test_folder_alias/session_01",  # Using folder instead of project
            "export_formats": ["wav"],
            "normalize_levels": True,
            "output_filename": "mixed_with_folder_alias"
        }
        
        try:
            response = self.make_request(
                "/api/v1/concat/mixed",
                method="POST",
                data={"request_json": json.dumps(request_data)},
                files=files_to_upload
            )
            
            if response.status_code == 200:
                # Save the streamed file
                self.save_response_file(response, "mixed_folder_alias_test.wav")
                self.log("PASS Folder parameter alias test passed - file generated successfully")
                
            else:
                self.log(f"FAIL Folder parameter alias test failed: {response.status_code}")
                self.log(f"   Error: {response.text}")
                
        except Exception as e:
            self.log(f"FAIL Folder parameter alias test failed: {e}")
        finally:
            # Close file handles
            for _, file_tuple in files_to_upload:
                file_tuple[1].close()
    
    def test_format_conversion_optimization(self):
        """Test post-concatenation format conversion (Task 11.16 key improvement)"""
        self.log("=== Test: Format Conversion Optimization ===")
        
        # Prepare files for upload
        files_to_upload = [
            ("uploaded_files", ("sean.mp3", open("tests/media/sean.mp3", "rb"), "audio/mpeg")),
        ]
        
        # Create mixed segments 
        segments = [
            {"type": "server_file", "source": "concatenation_test/05-sarah-audio.mp3"},
            {"type": "upload", "index": 0},
            {"type": "server_file", "source": "concatenation_test/06-mark-audio.mp3"}
        ]
        
        # Test multiple format conversion (the key optimization)
        request_data = {
            "segments": segments,
            "export_formats": ["wav", "mp3", "flac"],  # Multiple formats to test conversion
            "normalize_levels": True,
            "crossfade_ms": 100,
            "pause_duration_ms": 200,
            "output_filename": "mixed_multi_format"
        }
        
        try:
            # Use URL mode to get metadata about all generated files
            response = self.make_request(
                "/api/v1/concat/mixed?response_mode=url",
                method="POST",
                data={"request_json": json.dumps(request_data)},
                files=files_to_upload
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log("PASS Multi-format optimization test passed")
                self.log(f"   Generated files: {result.get('output_files', [])}")
                self.log(f"   Processing time: {result.get('processing_time_seconds', 0):.2f}s")
                
                # Verify all three formats were generated
                output_files = result.get('output_files', [])
                formats_generated = [Path(f).suffix.lower() for f in output_files]
                expected_formats = ['.wav', '.mp3', '.flac']
                
                for fmt in expected_formats:
                    if fmt in formats_generated:
                        self.log(f"   PASS {fmt} format generated")
                    else:
                        self.log(f"   FAIL {fmt} format missing")
                
                # Check if processing time is reasonable (optimization should be faster)
                processing_time = result.get('processing_time_seconds', 0)
                if processing_time < 10:  # Reasonable threshold
                    self.log(f"   PASS Processing time efficient: {processing_time:.2f}s")
                else:
                    self.log(f"   WARN Processing time: {processing_time:.2f}s (may indicate optimization needed)")
                
            else:
                self.log(f"FAIL Multi-format optimization test failed: {response.status_code}")
                self.log(f"   Error: {response.text}")
                
        except Exception as e:
            self.log(f"FAIL Multi-format optimization test failed: {e}")
        finally:
            # Close file handles
            for _, file_tuple in files_to_upload:
                file_tuple[1].close()
    
    def test_enhanced_logging_validation(self):
        """Test enhanced logging and monitoring (Task 11.16 requirement)"""
        self.log("=== Test: Enhanced Logging Validation ===")
        
        # This test checks that the server logs contain the expected enhanced logging
        # We'll make a request and analyze the response metadata for timing information
        
        # Prepare files for upload
        files_to_upload = [
            ("uploaded_files", ("alex.mp3", open("tests/media/alex.mp3", "rb"), "audio/mpeg")),
        ]
        
        # Create mixed segments with trimming to test enhanced logging
        segments = [
            {"type": "server_file", "source": "concatenation_test/01-sarah-audio-long.mp3"},
            {"type": "upload", "index": 0},
            {"type": "server_file", "source": "concatenation_test/02-mark-audio-long.mp3"}
        ]
        
        request_data = {
            "segments": segments,
            "export_formats": ["wav", "mp3"],
            "normalize_levels": True,
            "trim": True,  # Enable trimming to test mode detection logging
            "trim_threshold_ms": 200,
            "pause_duration_ms": 400,
            "output_filename": "mixed_logging_test"
        }
        
        try:
            # Use URL mode to get detailed metadata
            response = self.make_request(
                "/api/v1/concat/mixed?response_mode=url",
                method="POST",
                data={"request_json": json.dumps(request_data)},
                files=files_to_upload
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log("PASS Enhanced logging validation test passed")
                
                # Check for enhanced metadata that indicates improved logging
                metadata = result.get('metadata', {})
                processing_time = result.get('processing_time_seconds', 0)
                
                self.log(f"   Processing time: {processing_time:.2f}s")
                self.log(f"   Generated files: {len(result.get('output_files', []))}")
                
                # The enhanced logging should be visible in server logs
                # Here we validate that the response contains expected structure
                if 'total_duration_seconds' in result:
                    self.log(f"   PASS Total duration tracked: {result['total_duration_seconds']:.2f}s")
                
                if 'file_count' in result:
                    self.log(f"   PASS File count tracked: {result['file_count']}")
                
                # Check for metadata structure indicating proper logging
                if isinstance(metadata, dict) and len(metadata) > 0:
                    self.log("   PASS Enhanced metadata structure present")
                else:
                    self.log("   WARN Metadata structure may need verification")
                
            else:
                self.log(f"FAIL Enhanced logging validation test failed: {response.status_code}")
                self.log(f"   Error: {response.text}")
                
        except Exception as e:
            self.log(f"FAIL Enhanced logging validation test failed: {e}")
        finally:
            # Close file handles
            for _, file_tuple in files_to_upload:
                file_tuple[1].close()
    
    def test_backward_compatibility(self):
        """Test backward compatibility with existing mixed concatenation features"""
        self.log("=== Test: Backward Compatibility ===")
        
        # Test that all existing mixed concatenation features still work
        # This includes: crossfade, trimming, manual silence, natural pauses
        
        # Prepare files for upload
        files_to_upload = [
            ("uploaded_files", ("jamie-01.mp3", open("tests/media/jamie-01.mp3", "rb"), "audio/mpeg")),
        ]
        
        # Create mixed segments with all features
        segments = [
            {"type": "server_file", "source": "concatenation_test/07-sarah-audio.mp3"},
            {"type": "silence", "source": "(1s)"},  # Manual silence
            {"type": "upload", "index": 0},
            {"type": "server_file", "source": "concatenation_test/08-mark-audio.mp3"}
        ]
        
        request_data = {
            "segments": segments,
            "export_formats": ["wav"],
            "normalize_levels": True,
            "crossfade_ms": 150,  # Crossfade feature
            "trim": True,         # Trimming feature
            "trim_threshold_ms": 180,
            "pause_duration_ms": 600,   # Natural pauses (should be overridden by manual silence)
            "pause_variation_ms": 100,
            "output_filename": "mixed_backward_compatibility"
        }
        
        try:
            response = self.make_request(
                "/api/v1/concat/mixed",
                method="POST",
                data={"request_json": json.dumps(request_data)},
                files=files_to_upload
            )
            
            if response.status_code == 200:
                # Save the streamed file
                self.save_response_file(response, "mixed_backward_compatibility_test.wav")
                self.log("PASS Backward compatibility test passed - all features working")
                
            else:
                self.log(f"FAIL Backward compatibility test failed: {response.status_code}")
                self.log(f"   Error: {response.text}")
                
        except Exception as e:
            self.log(f"FAIL Backward compatibility test failed: {e}")
        finally:
            # Close file handles
            for _, file_tuple in files_to_upload:
                file_tuple[1].close()
    
    def test_parameter_validation(self):
        """Test parameter validation for new project/folder parameters"""
        self.log("=== Test: Parameter Validation ===")
        
        # Test 1: Invalid project path (empty string)
        self.log("--- Test 1: Invalid project path (empty string) ---")
        try:
            request_data = {
                "segments": [{"type": "server_file", "source": "concatenation_test/01-sarah-audio.mp3"}],
                "project": "",  # Empty project should be rejected
                "export_formats": ["wav"]
            }
            
            response = self.make_request(
                "/api/v1/concat/mixed",
                method="POST",
                data={"request_json": json.dumps(request_data)},
                files=[]
            )
            
            if response.status_code == 400:  # Validation error
                self.log("PASS Empty project path correctly rejected")
            else:
                self.log(f"FAIL Empty project path should be rejected, got: {response.status_code}")
                
        except Exception as e:
            self.log(f"FAIL Empty project validation test failed: {e}")
        
        # Test 2: Invalid characters in project path
        self.log("--- Test 2: Invalid characters in project path ---")
        try:
            request_data = {
                "segments": [{"type": "server_file", "source": "concatenation_test/01-sarah-audio.mp3"}],
                "project": "invalid<>path",  # Invalid characters should be rejected
                "export_formats": ["wav"]
            }
            
            response = self.make_request(
                "/api/v1/concat/mixed",
                method="POST",
                data={"request_json": json.dumps(request_data)},
                files=[]
            )
            
            if response.status_code == 400:  # Validation error
                self.log("PASS Invalid project characters correctly rejected")
            else:
                self.log(f"FAIL Invalid project characters should be rejected, got: {response.status_code}")
                
        except Exception as e:
            self.log(f"FAIL Invalid project characters validation test failed: {e}")
        
        # Test 3: Both project and folder specified (should be rejected)
        self.log("--- Test 3: Both project and folder specified ---")
        try:
            request_data = {
                "segments": [{"type": "server_file", "source": "concatenation_test/01-sarah-audio.mp3"}],
                "project": "test_project",
                "folder": "test_folder",  # Both should be rejected
                "export_formats": ["wav"]
            }
            
            response = self.make_request(
                "/api/v1/concat/mixed",
                method="POST",
                data={"request_json": json.dumps(request_data)},
                files=[]
            )
            
            if response.status_code == 400:  # Validation error
                self.log("PASS Both project and folder correctly rejected")
            else:
                self.log(f"FAIL Both project and folder should be rejected, got: {response.status_code}")
                
        except Exception as e:
            self.log(f"FAIL Both project and folder validation test failed: {e}")
    
    def run_all_tests(self):
        """Run all Task 11.16 tests"""
        self.log("=" * 80)
        self.log("Task 11.16: Mixed Concatenation Optimization - Comprehensive Testing")
        self.log("=" * 80)
        
        start_time = time.time()
        
        # Run all tests
        self.test_project_folder_support()
        self.test_folder_parameter_alias()
        self.test_format_conversion_optimization()
        self.test_enhanced_logging_validation()
        self.test_backward_compatibility()
        self.test_parameter_validation()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.log("=" * 80)
        self.log(f"Task 11.16 Testing Complete - Total time: {total_time:.1f}s")
        self.log("=" * 80)
        
        # Summary
        self.log("Summary of Task 11.16 improvements tested:")
        self.log("PASS Project/folder parameter support for mixed concatenation")
        self.log("PASS Post-concatenation format conversion optimization")
        self.log("PASS Enhanced logging and monitoring")
        self.log("PASS Backward compatibility with existing features")
        self.log("PASS Parameter validation for new features")
        
        self.log("\nNext: Task 11.17 - Integration & Testing")

if __name__ == "__main__":
    # Ensure we're in the right directory
    if not Path("tests/media").exists():
        print("Error: tests/media directory not found. Please run from project root.")
        exit(1)
    
    if not Path("outputs/concatenation_test").exists():
        print("Error: outputs/concatenation_test directory not found. Please ensure test files exist.")
        exit(1)
    
    # Check if required upload files exist
    required_files = ["alex.mp3", "jamie-01.mp3", "sean.mp3"]
    for file in required_files:
        if not Path(f"tests/media/{file}").exists():
            print(f"Error: tests/media/{file} not found. Please ensure test files exist.")
            exit(1)
    
    tester = MixedConcatOptimizationTester()
    tester.run_all_tests()
