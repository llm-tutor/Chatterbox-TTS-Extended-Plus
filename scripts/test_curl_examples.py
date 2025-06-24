#!/usr/bin/env python3
"""
Comprehensive cURL Examples Tester
Tier 2 Testing: Complete validation for documentation releases and developer reference

Purpose: Validate ALL documented examples for releases and major API changes
Scope: All cURL examples including advanced features requiring specific setup
Usage: Documentation releases, major API changes, developer onboarding
Time: 8-15 minutes (comprehensive validation)
"""

import json
import os
import re
import sys
import time
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
import shlex


def print_progress(message, prefix="[COMPREHENSIVE]"):
    """Print progress message with consistent formatting (no Unicode emojis)"""
    print(f"{prefix} {message}")


def format_duration(seconds):
    """Format duration for display"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"


class CurlExampleTester:
    def __init__(self, api_base: str = "http://127.0.0.1:7860", timeout: int = 90):
        self.api_base = api_base.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.results: List[Dict[str, Any]] = []
        self.start_time = None
        
    def warm_up_server(self):
        """Make a quick health check to ensure server is ready after any reloads"""
        print_progress("Warming up server (ensuring reload completion)...")
        try:
            start_time = time.time()
            response = self.session.get(f"{self.api_base}/api/v1/health", timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                print_progress(f"Server ready - {format_duration(elapsed)}")
                return True
            else:
                print_progress(f"Server health check failed: {response.status_code}")
                return False
        except Exception as e:
            print_progress(f"Server warm-up failed: {e}")
            return False
    
    def categorize_command(self, curl_cmd: str) -> str:
        """Categorize the type of API command for progress reporting"""
        if '/health' in curl_cmd:
            return 'health'
        elif '/voices' in curl_cmd:
            return 'listing'
        elif '/outputs' in curl_cmd:
            return 'listing'
        elif '/tts' in curl_cmd:
            return 'tts'
        elif '/vc' in curl_cmd:
            return 'vc'
        else:
            return 'other'
    
    def estimate_command_time(self, category: str) -> int:
        """Estimate execution time for different command categories"""
        estimates = {
            'health': 1,
            'listing': 5,
            'tts': 30,
            'vc': 30,
            'other': 10
        }
        return estimates.get(category, 10)
        
    def extract_curl_commands(self, content: str) -> List[Dict[str, str]]:
        """Extract cURL commands from markdown content"""
        # Match ```bash blocks that contain curl commands
        pattern = r'```bash\n(.*?)\n```'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        curl_commands = []
        for i, match in enumerate(matches):
            block_content = match.group(1).strip()
            
            # Handle complete curl command blocks including multiline JSON
            if 'curl ' in block_content:
                # Clean up the command - remove line breaks and extra spaces
                curl_command = block_content
                
                # Remove backslashes used for line continuation
                curl_command = re.sub(r'\s*\\\s*\n\s*', ' ', curl_command)
                
                # Clean up multiple spaces
                curl_command = re.sub(r'\s+', ' ', curl_command)
                
                # Only add if it contains a proper curl command
                if curl_command.strip().startswith('curl '):
                    curl_commands.append({
                        'index': len(curl_commands),
                        'command': curl_command.strip(),
                        'line_start': content[:match.start()].count('\n') + 1
                    })
        
        return curl_commands    
    def parse_curl_command(self, curl_cmd: str) -> Optional[Dict[str, Any]]:
        """Parse a cURL command into requests parameters"""
        try:
            # Simple parsing - handle basic curl patterns
            if not curl_cmd.strip().startswith('curl'):
                return None
            
            # Extract URL - improved pattern to handle quoted URLs with query parameters
            # Pattern matches: curl "URL" or curl URL or curl [options] URL
            url_patterns = [
                r'curl\s+(?:[^"\'h\s]+\s+)*?"([^"]+)"',  # quoted URL
                r'curl\s+(?:[^"\'h\s]+\s+)*?\'([^\']+)\'',  # single quoted URL
                r'curl\s+(?:[^h\s]+\s+)*?(https?://[^\s]+)',  # unquoted http URL
                r'curl\s+(?:[^/\s]+\s+)*?(/[^\s]*)'  # unquoted path URL
            ]
            
            url = None
            for pattern in url_patterns:
                url_match = re.search(pattern, curl_cmd)
                if url_match:
                    url = url_match.group(1).strip()
                    break
            
            if not url:
                return None
            
            # Replace localhost variations with our API base
            if url.startswith('http://localhost:7860'):
                url = url.replace('http://localhost:7860', self.api_base)
            elif not url.startswith('http'):
                url = f"{self.api_base}{url}"
            
            # Extract method
            method = 'GET'
            if '-X POST' in curl_cmd or '--request POST' in curl_cmd:
                method = 'POST'
            elif '-X PUT' in curl_cmd or '--request PUT' in curl_cmd:
                method = 'PUT'
            elif '-X DELETE' in curl_cmd or '--request DELETE' in curl_cmd:
                method = 'DELETE'
            
            # Extract headers
            headers = {}
            header_matches = re.finditer(r'-H\s+["\']([^"\']+)["\']', curl_cmd)
            for match in header_matches:
                header = match.group(1)
                if ':' in header:
                    key, value = header.split(':', 1)
                    headers[key.strip()] = value.strip()
            
            # Extract JSON data from -d parameter
            data = None
            # Look for -d followed by a JSON object
            data_match = re.search(r'-d\s+["\']({.*?})["\']', curl_cmd, re.DOTALL)
            if data_match:
                data_str = data_match.group(1)
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError as e:
                    # Try to fix common JSON issues
                    # Remove any trailing commas
                    data_str = re.sub(r',(\s*[}\]])', r'\1', data_str)
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        data = data_str
            
            return {
                'method': method,
                'url': url,
                'headers': headers,
                'data': data
            }
            
        except Exception as e:
            return None    
    def test_curl_command(self, curl_cmd: str, source_file: str, cmd_index: int, 
                         current_cmd: int, total_cmds: int) -> Dict[str, Any]:
        """Test a single cURL command with enhanced progress reporting"""
        category = self.categorize_command(curl_cmd)
        estimated_time = self.estimate_command_time(category)
        
        # Enhanced progress message
        progress_msg = f"[{current_cmd}/{total_cmds}] {category.upper()} - Est: {estimated_time}s"
        print_progress(progress_msg)
        print(f"    File: {source_file}")
        print(f"    Command: {curl_cmd[:80]}...")
        
        result = {
            'source_file': source_file,
            'command_index': cmd_index,
            'curl_command': curl_cmd,
            'category': category,
            'success': False,
            'error': None,
            'status_code': None,
            'execution_time': 0,
            'timeout_occurred': False
        }
        
        # Parse curl command
        parsed = self.parse_curl_command(curl_cmd)
        if not parsed:
            result['error'] = "Failed to parse cURL command"
            print(f"    [PARSE ERROR] Failed to parse cURL command")
            return result
        
        try:
            start_time = time.time()
            
            # Make request with timeout handling
            response = self.session.request(
                method=parsed['method'],
                url=parsed['url'],
                headers=parsed['headers'],
                json=parsed['data'] if isinstance(parsed['data'], dict) else None,
                data=parsed['data'] if isinstance(parsed['data'], str) else None,
                timeout=self.timeout
            )
            
            result['execution_time'] = time.time() - start_time
            result['status_code'] = response.status_code
            
            # Consider 2xx responses as success
            if 200 <= response.status_code < 300:
                result['success'] = True
                print(f"    [PASS] ({response.status_code}) - {format_duration(result['execution_time'])}")
                
                # Parse response for additional info
                try:
                    response_data = response.json()
                    if category in ['tts', 'vc'] and 'message' in response_data:
                        print(f"    Generated: {response_data.get('message', 'Audio file')}")
                    elif category == 'listing' and isinstance(response_data, list):
                        print(f"    Found: {len(response_data)} items")
                except:
                    pass  # Not JSON or parsing failed, continue
            else:
                result['error'] = f"HTTP {response.status_code}: {response.text[:200]}"
                print(f"    [FAIL] ({response.status_code}) - {format_duration(result['execution_time'])}")
                if len(response.text) > 0:
                    print(f"    Error: {response.text[:100]}...")
                
        except requests.exceptions.Timeout:
            result['execution_time'] = time.time() - start_time
            result['timeout_occurred'] = True
            result['error'] = f"Request timeout after {self.timeout}s"
            print(f"    [TIMEOUT] - Request exceeded {self.timeout}s timeout")
        except requests.exceptions.ConnectionError:
            result['execution_time'] = time.time() - start_time
            result['error'] = "Connection error - server may be down"
            print(f"    [CONNECTION ERROR] - Cannot reach API server")
        except Exception as e:
            result['execution_time'] = time.time() - start_time
            result['error'] = str(e)
            print(f"    [ERROR] {e}")
            
        print()  # Empty line for readability
        return result    
    def test_file_examples(self, file_path: Path, current_file: int, total_files: int) -> List[Dict[str, Any]]:
        """Test all cURL examples in a single file"""
        print_progress(f"Testing file {current_file}/{total_files}: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            error_result = {
                'source_file': str(file_path),
                'command_index': 0,
                'curl_command': '',
                'category': 'file_error',
                'success': False,
                'error': f"Failed to read file: {e}",
                'status_code': None,
                'execution_time': 0,
                'timeout_occurred': False
            }
            print(f"    [FILE ERROR] {e}")
            return [error_result]
        
        curl_commands = self.extract_curl_commands(content)
        
        if not curl_commands:
            print(f"    No cURL commands found in {file_path.name}")
            return []
        
        print(f"    Found {len(curl_commands)} cURL command(s)")
        results = []
        
        # Calculate total commands for progress tracking
        total_commands_so_far = sum(len(self.results) for result in [self.results] if self.results)
        
        for cmd in curl_commands:
            result = self.test_curl_command(
                cmd['command'], 
                str(file_path.relative_to(Path.cwd())), 
                cmd['index'],
                total_commands_so_far + len(results) + 1,
                self.total_commands_estimate
            )
            results.append(result)
            
        return results
    
    def test_all_examples(self, docs_root: Path, skip_categories: List[str] = None) -> Dict[str, Any]:
        """Test cURL examples in all relevant files with enhanced progress tracking"""
        self.start_time = time.time()
        skip_categories = skip_categories or []
        
        print_progress("Starting Comprehensive Validation (Tier 2 Testing)")
        print_progress("Expected duration: 8-15 minutes")
        print(f"API Base: {self.api_base}")
        print(f"Timeout per request: {self.timeout}s")
        print("-" * 60)
        
        # Warm up server first
        if not self.warm_up_server():
            print_progress("WARNING: Server warm-up failed, proceeding anyway...")
        
        print()
        
        # Find files with cURL examples
        example_files = []
        for root, dirs, files in os.walk(docs_root):
            for file in files:
                if ('curl' in file.lower() or 'example' in file.lower()) and file.endswith('.md'):
                    example_files.append(Path(root) / file)
        
        if not example_files:
            print_progress("No example files found!")
            return {
                'files_tested': 0,
                'commands_tested': 0,
                'commands_passed': 0,
                'commands_failed': 0,
                'commands_timeout': 0,
                'total_time': 0
            }
        
        # Quick scan to estimate total commands
        self.total_commands_estimate = 0
        for file_path in example_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                curl_commands = self.extract_curl_commands(content)
                self.total_commands_estimate += len(curl_commands)
            except:
                pass
        
        print_progress(f"Found {len(example_files)} file(s) with ~{self.total_commands_estimate} command(s)")
        print()
        
        all_results = []
        stats = {
            'files_tested': 0,
            'commands_tested': 0,
            'commands_passed': 0,
            'commands_failed': 0,
            'commands_timeout': 0
        }
        
        for i, file_path in enumerate(example_files, 1):
            file_results = self.test_file_examples(file_path, i, len(example_files))
            
            if file_results:
                # Filter by categories if specified
                if skip_categories:
                    file_results = [r for r in file_results if r.get('category', '') not in skip_categories]
                
                all_results.extend(file_results)
                stats['files_tested'] += 1
                
        stats['commands_tested'] = len(all_results)
        stats['commands_passed'] = sum(1 for r in all_results if r['success'])
        stats['commands_failed'] = stats['commands_tested'] - stats['commands_passed']
        stats['commands_timeout'] = sum(1 for r in all_results if r.get('timeout_occurred', False))
        stats['total_time'] = time.time() - self.start_time
        
        self.results = all_results
        return stats    
    def print_results(self, stats: Dict[str, Any]):
        """Print comprehensive test results with timing breakdown"""
        print("=" * 60)
        print_progress("COMPREHENSIVE VALIDATION SUMMARY")
        print(f"Total Time: {format_duration(stats['total_time'])}")
        print(f"Files tested: {stats['files_tested']}")
        print(f"Commands tested: {stats['commands_tested']}")
        print(f"Commands passed: {stats['commands_passed']}")
        print(f"Commands failed: {stats['commands_failed']}")
        if stats.get('commands_timeout', 0) > 0:
            print(f"Commands timed out: {stats['commands_timeout']}")
        
        if stats['commands_tested'] > 0:
            success_rate = (stats['commands_passed'] / stats['commands_tested']) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        # Timing breakdown by category
        if self.results:
            print(f"\n=== TIMING BREAKDOWN ===")
            category_times = {}
            category_counts = {}
            
            for result in self.results:
                category = result.get('category', 'unknown')
                if category not in category_times:
                    category_times[category] = 0
                    category_counts[category] = 0
                category_times[category] += result['execution_time']
                category_counts[category] += 1
            
            for category in sorted(category_times.keys()):
                avg_time = category_times[category] / category_counts[category]
                total_time = category_times[category]
                count = category_counts[category]
                print(f"{category.upper()}: {count} commands, {format_duration(total_time)} total, {format_duration(avg_time)} avg")
        
        # Show failures with detailed context
        if stats['commands_failed'] > 0:
            print(f"\n=== FAILURES ({stats['commands_failed']}) ===")
            for result in self.results:
                if not result['success']:
                    print(f"\nFAILED: {result['source_file']} command {result['command_index']} ({result.get('category', 'unknown')})")
                    print(f"Command: {result['curl_command'][:100]}...")
                    print(f"Error: {result['error']}")
                    if result['status_code']:
                        print(f"Status Code: {result['status_code']}")
                    if result.get('timeout_occurred', False):
                        print(f"TIMEOUT: Request exceeded {self.timeout}s limit")
        
        # Final assessment
        if stats['commands_failed'] == 0 and stats['commands_tested'] > 0:
            print_progress("RESULT: ALL COMPREHENSIVE TESTS PASSED")
            print_progress("Documentation examples are ready for release")
        elif stats['commands_tested'] == 0:
            print_progress("RESULT: NO TESTS FOUND")
            print_progress("No cURL examples found in documentation")
        else:
            print_progress(f"RESULT: {stats['commands_failed']} TESTS FAILED")
            print_progress("Review failures before documentation release")


def main():
    parser = argparse.ArgumentParser(description='Test cURL command examples in API documentation (Comprehensive Tier 2)')
    parser.add_argument('--docs-root', default='docs/api', 
                      help='Root directory of documentation (default: docs/api)')
    parser.add_argument('--api-base', default='http://127.0.0.1:7860',
                      help='API base URL (default: http://127.0.0.1:7860)')
    parser.add_argument('--timeout', type=int, default=90,
                      help='Request timeout in seconds (default: 90)')
    parser.add_argument('--skip-categories', nargs='*', choices=['tts', 'vc', 'health', 'listing', 'other'],
                      help='Skip specific test categories')
    
    args = parser.parse_args()
    
    # Resolve docs root path
    docs_root = Path(args.docs_root)
    if not docs_root.is_absolute():
        docs_root = Path.cwd() / docs_root
    
    if not docs_root.exists():
        print(f"ERROR: Documentation root not found: {docs_root}")
        sys.exit(1)
    
    # Run comprehensive cURL tester
    tester = CurlExampleTester(args.api_base, args.timeout)
    stats = tester.test_all_examples(docs_root, args.skip_categories)
    tester.print_results(stats)
    
    # Exit with error code if failures
    if stats['commands_failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
