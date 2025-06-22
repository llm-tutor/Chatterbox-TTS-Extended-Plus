#!/usr/bin/env python3
"""
Test suite for Phase 10 Task 10.4: Generated Files Listing
Tests the generated files listing functionality including pagination, search, and filtering.
"""

import requests
import json
from pathlib import Path
import time

# API Configuration
API_BASE_URL = "http://127.0.0.1:7860"
TEST_TIMEOUT = 30

def test_generated_files_listing():
    """Test the generated files listing endpoint functionality"""
    print("=== Testing Phase 10 Task 10.4: Generated Files Listing ===")
    
    # Test 1: Basic file listing
    print("\n1. Testing basic file listing...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/outputs",
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   SUCCESS: Found {result['total_files']} total files")
            print(f"   Page info: Page {result['page']}/{result['total_pages']}, showing {result['count']} files")
            
            # Show first few files
            if result['files']:
                print("   Sample files:")
                for file_meta in result['files'][:3]:
                    print(f"   - {file_meta['filename']} ({file_meta['generation_type']}) - {file_meta.get('duration_seconds', 'Unknown')}s")
        else:
            print(f"   FAILED: File listing failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 2: Pagination
    print("\n2. Testing pagination...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/outputs?page=1&page_size=5",
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   SUCCESS: Pagination working - Page {result['page']}, showing {result['count']} of {result['total_files']} files")
            print(f"   Has next: {result['has_next']}, Has previous: {result['has_previous']}")
        else:
            print(f"   FAILED: Pagination failed with status {response.status_code}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 3: Generation type filtering
    print("\n3. Testing generation type filtering...")
    
    for gen_type in ['tts', 'vc', 'concat']:
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/outputs?generation_type={gen_type}",
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   {gen_type.upper()}: {result['total_files']} files")
                
                # Verify all returned files match the filter
                all_match = all(file_meta['generation_type'] == gen_type for file_meta in result['files'])
                if all_match:
                    print(f"   SUCCESS: All files are {gen_type} type")
                else:
                    print(f"   WARNING: Some files don't match {gen_type} filter")
            else:
                print(f"   FAILED: {gen_type} filtering failed with status {response.status_code}")
                
        except Exception as e:
            print(f"   ERROR filtering {gen_type}: {e}")
    
    # Test 4: Search functionality
    print("\n4. Testing search functionality...")
    
    try:
        # Search for files containing "test" (might match our uploaded test files)
        response = requests.get(
            f"{API_BASE_URL}/api/v1/outputs?search=test",
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   SUCCESS: Search for 'test' found {result['total_files']} files")
            
            # Verify search results
            if result['files']:
                for file_meta in result['files'][:2]:
                    if 'test' in file_meta['filename'].lower():
                        print(f"   - Found: {file_meta['filename']}")
        else:
            print(f"   FAILED: Search failed with status {response.status_code}")
            
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n=== Phase 10 Task 10.4 Generated Files Listing Tests Complete ===")


if __name__ == "__main__":
    test_generated_files_listing()
