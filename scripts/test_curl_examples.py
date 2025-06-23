#!/usr/bin/env python3
"""
cURL Examples Tester
Tests all cURL command examples in the API documentation by converting them to Python requests
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


class CurlExampleTester:
    def __init__(self, api_base: str = "http://localhost:7860", timeout: int = 90):
        self.api_base = api_base.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.results: List[Dict[str, Any]] = []
        
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
            
            # Extract URL - look for the first argument after curl that looks like a URL
            url_pattern = r'curl\s+(?:[^h\s]+\s+)*?(https?://[^\s]+|/[^\s]*)'
            url_match = re.search(url_pattern, curl_cmd)
            if not url_match:
                return None
            
            url = url_match.group(1).strip('\'"')
            
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
    def test_curl_command(self, curl_cmd: str, source_file: str, cmd_index: int) -> Dict[str, Any]:
        """Test a single cURL command"""
        result = {
            'source_file': source_file,
            'command_index': cmd_index,
            'curl_command': curl_cmd,
            'success': False,
            'error': None,
            'status_code': None,
            'execution_time': 0
        }
        
        # Parse curl command
        parsed = self.parse_curl_command(curl_cmd)
        if not parsed:
            result['error'] = "Failed to parse cURL command"
            return result
        
        try:
            start_time = time.time()
            
            # Make request
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
            else:
                result['error'] = f"HTTP {response.status_code}: {response.text[:200]}"
                
        except Exception as e:
            result['execution_time'] = time.time() - start_time
            result['error'] = str(e)
            
        return result    
    def test_file_examples(self, file_path: Path) -> List[Dict[str, Any]]:
        """Test all cURL examples in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return [{
                'source_file': str(file_path),
                'command_index': 0,
                'curl_command': '',
                'success': False,
                'error': f"Failed to read file: {e}",
                'status_code': None,
                'execution_time': 0
            }]
        
        curl_commands = self.extract_curl_commands(content)
        results = []
        
        for cmd in curl_commands:
            print(f"Testing {file_path.name} cURL command {cmd['index']}...")
            result = self.test_curl_command(
                cmd['command'], 
                str(file_path.relative_to(Path.cwd())), 
                cmd['index']
            )
            results.append(result)
            
        return results
    
    def test_all_examples(self, docs_root: Path) -> Dict[str, Any]:
        """Test cURL examples in all relevant files"""
        # Find files with cURL examples
        example_files = []
        for root, dirs, files in os.walk(docs_root):
            for file in files:
                if ('curl' in file.lower() or 'example' in file.lower()) and file.endswith('.md'):
                    example_files.append(Path(root) / file)
        
        all_results = []
        stats = {
            'files_tested': 0,
            'commands_tested': 0,
            'commands_passed': 0,
            'commands_failed': 0
        }
        
        for file_path in example_files:
            file_results = self.test_file_examples(file_path)
            all_results.extend(file_results)
            
            if file_results:
                stats['files_tested'] += 1
                
        stats['commands_tested'] = len(all_results)
        stats['commands_passed'] = sum(1 for r in all_results if r['success'])
        stats['commands_failed'] = stats['commands_tested'] - stats['commands_passed']
        
        self.results = all_results
        return stats    
    def print_results(self, stats: Dict[str, Any]):
        """Print test results"""
        print(f"\n=== cURL Examples Test Results ===")
        print(f"Files tested: {stats['files_tested']}")
        print(f"Commands tested: {stats['commands_tested']}")
        print(f"Commands passed: {stats['commands_passed']}")
        print(f"Commands failed: {stats['commands_failed']}")
        
        if stats['commands_failed'] > 0:
            print(f"\n=== FAILURES ({stats['commands_failed']}) ===")
            for result in self.results:
                if not result['success']:
                    print(f"\nFAILED: {result['source_file']} command {result['command_index']}")
                    print(f"Command: {result['curl_command'][:100]}...")
                    print(f"Error: {result['error']}")
                    if result['status_code']:
                        print(f"Status Code: {result['status_code']}")
        
        if stats['commands_failed'] == 0 and stats['commands_tested'] > 0:
            print("\n✅ All cURL examples passed!")
        elif stats['commands_tested'] == 0:
            print("\n⚠️  No cURL examples found")


def main():
    parser = argparse.ArgumentParser(description='Test cURL command examples in API documentation')
    parser.add_argument('--docs-root', default='docs/api', 
                      help='Root directory of documentation (default: docs/api)')
    parser.add_argument('--api-base', default='http://localhost:7860',
                      help='API base URL (default: http://localhost:7860)')
    parser.add_argument('--timeout', type=int, default=90,
                      help='Request timeout in seconds (default: 90)')
    
    args = parser.parse_args()
    
    # Resolve docs root path
    docs_root = Path(args.docs_root)
    if not docs_root.is_absolute():
        docs_root = Path.cwd() / docs_root
    
    if not docs_root.exists():
        print(f"ERROR: Documentation root not found: {docs_root}")
        sys.exit(1)
    
    # Run cURL tester
    tester = CurlExampleTester(args.api_base, args.timeout)
    stats = tester.test_all_examples(docs_root)
    tester.print_results(stats)
    
    # Exit with error code if failures
    if stats['commands_failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
