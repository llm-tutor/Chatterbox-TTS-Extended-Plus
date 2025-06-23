#!/usr/bin/env python3
"""
Complete API Documentation Examples Test Suite
Runs all tests to validate documentation examples
"""

import sys
from pathlib import Path

# Import our test modules
from test_runner import APITester
from test_curl_examples import run_curl_tests
from test_python_examples import run_python_tests

def main():
    """Run complete test suite."""
    print("API Documentation Examples Test Suite")
    print("=" * 60)
    
    tester = APITester()
    
    # Warm up server first
    if not tester.warm_up_server():
        print("\nERROR: Cannot connect to API server. Please ensure:")
        print("   1. Server is running: python main_api.py")
        print("   2. Virtual environment is activated: .venv\\Scripts\\activate")
        print("   3. All dependencies installed: pip install -r requirements.txt")
        return False
    
    print(f"\nTesting examples against: {tester.base_url}")
    print(f"Temporary files in: {Path(__file__).parent / 'temp_files'}")
    
    # Run cURL tests
    print("\nTesting cURL Examples...")
    run_curl_tests(tester)
    
    # Run Python tests
    print("\nTesting Python Examples...")
    run_python_tests(tester)
    
    # Generate final report
    print("\n" + "="*60)
    success = tester.generate_report()
    
    if success:
        print("\nSUCCESS: All documentation examples are working correctly!")
        print("   The reorganized API documentation is validated and ready.")
    else:
        print("\nWARNING: Some examples failed - documentation may need updates.")
        print("   Check the failed tests above for details.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
