#!/usr/bin/env python3
"""
API Documentation Examples Test Runner
Tests all examples from the reorganized API documentation

This test suite validates that the code examples in our documentation
actually work with the current API implementation.
"""

import sys
import os
import time
import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# API Configuration with server reload considerations
API_BASE = "http://localhost:7860"
INITIAL_TIMEOUT = 30  # Extended timeout for first request (server reload)
NORMAL_TIMEOUT = 15   # Normal timeout for subsequent requests
CHUNK_SIZE = 8192

class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.success = False
        self.error = None
        self.duration = 0
        self.notes = []

class APITester:
    def __init__(self):
        self.base_url = API_BASE
        self.results = []
        self.server_warmed_up = False
        self.session = requests.Session()
        
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def warm_up_server(self) -> bool:
        """Warm up server with a simple health check to handle reload."""
        self.log("Warming up server (handling potential reload)...")
        
        try:
            start_time = time.time()
            response = self.session.get(
                f"{self.base_url}/api/v1/health", 
                timeout=INITIAL_TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log(f"Server ready (took {duration:.2f}s)")
                self.server_warmed_up = True
                return True
            else:
                self.log(f"Server returned {response.status_code}", "ERROR")
                return False
                
        except requests.exceptions.Timeout:
            self.log("Server warm-up timeout - server may not be running", "ERROR")
            return False
        except Exception as e:
            self.log(f"Server warm-up failed: {e}", "ERROR")
            return False
    
    def run_test(self, test_name: str, test_func) -> TestResult:
        """Run a single test with error handling and timing."""
        result = TestResult(test_name)
        self.log(f"Running: {test_name}")
        
        start_time = time.time()
        try:
            test_func(result)
            result.success = True
            self.log(f"PASSED: {test_name}")
        except Exception as e:
            result.error = str(e)
            result.success = False
            self.log(f"FAILED: {test_name} - {e}", "ERROR")
        
        result.duration = time.time() - start_time
        self.results.append(result)
        return result
    
    def generate_report(self):
        """Generate test report."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*60)
        print(f"TEST REPORT - API Documentation Examples")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} [OK]")
        print(f"Failed: {failed_tests} [FAIL]")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("Failed Tests:")
            for result in self.results:
                if not result.success:
                    print(f"  [FAIL] {result.name}: {result.error}")
            print()
        
        print("Test Details:")
        for result in self.results:
            status = "[OK]" if result.success else "[FAIL]"
            print(f"  {status} {result.name} ({result.duration:.2f}s)")
            for note in result.notes:
                print(f"    NOTE: {note}")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = APITester()
    
    # Check if server is running
    if not tester.warm_up_server():
        print("\n❌ Cannot connect to API server. Please ensure:")
        print("   1. Server is running on http://localhost:7860")
        print("   2. All dependencies are installed")
        print("   3. Virtual environment is activated")
        sys.exit(1)
    
    print(f"\n📋 Starting API Documentation Examples Test Suite")
    print(f"   Server: {API_BASE}")
    print(f"   Test Directory: {Path(__file__).parent}")
    
    # Import and run test modules
    # (We'll add these in the next files)
    
    success = tester.generate_report()
    sys.exit(0 if success else 1)
