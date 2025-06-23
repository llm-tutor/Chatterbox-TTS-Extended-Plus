#!/usr/bin/env python3
"""
Python API Examples Tester
Tests all Python code examples in the API documentation
"""

import asyncio
import json
import re
import sys
import time
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse


class PythonExampleTester:
    def __init__(self, api_base: str = "http://localhost:7860", timeout: int = 90):
        self.api_base = api_base.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.results: List[Dict[str, Any]] = []
        
    def extract_python_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Extract Python code blocks from markdown content"""
        # Match ```python blocks
        pattern = r'```python\n(.*?)\n```'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        code_blocks = []
        for i, match in enumerate(matches):
            code = match.group(1).strip()
            # Skip if it's just imports or class definitions without actual calls
            if ('def ' in code and 'print(' not in code and 
                'response =' not in code and '.json()' not in code):
                continue
            
            code_blocks.append({
                'index': i,
                'code': code,
                'line_start': content[:match.start()].count('\n') + 1
            })
        
        return code_blocks
    
    def is_executable_example(self, code: str) -> bool:
        """Check if code block is an executable example"""
        # Skip pure class/function definitions
        if code.strip().startswith(('class ', 'def ')) and 'if __name__' not in code:
            return False
        
        # Skip imports only
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        non_import_lines = [line for line in lines if not line.startswith(('import ', 'from '))]
        if len(non_import_lines) < 2:
            return False
            
        # Must have actual API calls or examples
        api_indicators = [
            'requests.', '.get(', '.post(', '.json()', 
            'ChatterboxClient', 'check_health', 'generate_tts'
        ]
        
        return any(indicator in code for indicator in api_indicators)
    
    def prepare_test_environment(self) -> str:
        """Prepare test environment code"""
        return '''
import requests
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

# Test configuration
API_BASE = "{api_base}"
API_TIMEOUT = {timeout}

class ChatterboxClient:
    def __init__(self, base_url: str = API_BASE, timeout: int = API_TIMEOUT):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling."""
        url = f"{{self.base_url}}{{endpoint}}"
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {{e}}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {{e.response.status_code}}")
                print(f"Response body: {{e.response.text}}")
            raise

# Initialize client for examples
client = ChatterboxClient()
'''.format(api_base=self.api_base, timeout=self.timeout)    
    def test_code_block(self, code: str, source_file: str, block_index: int) -> Dict[str, Any]:
        """Test a single code block"""
        result = {
            'source_file': source_file,
            'block_index': block_index,
            'success': False,
            'error': None,
            'output': None,
            'execution_time': 0
        }
        
        # Prepare full code with environment
        full_code = self.prepare_test_environment() + '\n\n' + code
        
        # Create isolated namespace
        test_globals = {}
        
        try:
            start_time = time.time()
            exec(full_code, test_globals)
            result['execution_time'] = time.time() - start_time
            result['success'] = True
            result['output'] = "Code executed successfully"
            
        except Exception as e:
            result['error'] = str(e)
            result['execution_time'] = time.time() - start_time
            
        return result    
    def test_file_examples(self, file_path: Path) -> List[Dict[str, Any]]:
        """Test all examples in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return [{
                'source_file': str(file_path),
                'block_index': 0,
                'success': False,
                'error': f"Failed to read file: {e}",
                'output': None,
                'execution_time': 0
            }]
        
        code_blocks = self.extract_python_code_blocks(content)
        results = []
        
        for block in code_blocks:
            if not self.is_executable_example(block['code']):
                continue
                
            print(f"Testing {file_path.name} block {block['index']}...")
            result = self.test_code_block(
                block['code'], 
                str(file_path.relative_to(Path.cwd())), 
                block['index']
            )
            results.append(result)
            
        return results    
    def test_all_examples(self, docs_root: Path) -> Dict[str, Any]:
        """Test examples in all Python example files"""
        # Find Python example files
        example_files = []
        for root, dirs, files in os.walk(docs_root):
            for file in files:
                if 'python' in file.lower() and file.endswith('.md'):
                    example_files.append(Path(root) / file)
        
        all_results = []
        stats = {
            'files_tested': 0,
            'examples_tested': 0,
            'examples_passed': 0,
            'examples_failed': 0
        }
        
        for file_path in example_files:
            file_results = self.test_file_examples(file_path)
            all_results.extend(file_results)
            
            if file_results:  # Only count if file had testable examples
                stats['files_tested'] += 1
                
        stats['examples_tested'] = len(all_results)
        stats['examples_passed'] = sum(1 for r in all_results if r['success'])
        stats['examples_failed'] = stats['examples_tested'] - stats['examples_passed']
        
        self.results = all_results
        return stats    
    def print_results(self, stats: Dict[str, Any]):
        """Print test results"""
        print(f"\n=== Python Examples Test Results ===")
        print(f"Files tested: {stats['files_tested']}")
        print(f"Examples tested: {stats['examples_tested']}")
        print(f"Examples passed: {stats['examples_passed']}")
        print(f"Examples failed: {stats['examples_failed']}")
        
        if stats['examples_failed'] > 0:
            print(f"\n=== FAILURES ({stats['examples_failed']}) ===")
            for result in self.results:
                if not result['success']:
                    print(f"\nFAILED: {result['source_file']} block {result['block_index']}")
                    print(f"Error: {result['error']}")
        
        if stats['examples_failed'] == 0 and stats['examples_tested'] > 0:
            print("\n✅ All Python examples passed!")
        elif stats['examples_tested'] == 0:
            print("\n⚠️  No executable Python examples found")


def main():
    parser = argparse.ArgumentParser(description='Test Python code examples in API documentation')
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
    
    # Run example tester
    tester = PythonExampleTester(args.api_base, args.timeout)
    stats = tester.test_all_examples(docs_root)
    tester.print_results(stats)
    
    # Exit with error code if failures
    if stats['examples_failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
