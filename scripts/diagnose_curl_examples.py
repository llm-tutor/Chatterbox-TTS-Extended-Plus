#!/usr/bin/env python3
"""
Diagnostic script for cURL examples - just parsing and categorization
"""

import json
from pathlib import Path
from test_curl_examples import CurlExampleTester


def diagnose_examples():
    """Analyze cURL examples without making requests"""
    
    tester = CurlExampleTester()
    curl_file = Path('docs/api/schemas/examples/curl-examples.md')
    
    if not curl_file.exists():
        print(f"ERROR: {curl_file} not found")
        return
    
    content = curl_file.read_text(encoding='utf-8')
    commands = tester.extract_curl_commands(content)
    
    print(f"=== cURL Examples Analysis ===")
    print(f"Total commands found: {len(commands)}")
    print()
    
    # Categorize commands
    categories = {
        'health': [],
        'tts': [],
        'vc': [],
        'voice_mgmt': [],
        'file_ops': [],
        'error_demos': [],
        'other': []
    }
    
    for i, cmd_info in enumerate(commands):
        cmd = cmd_info['command']
        parsed = tester.parse_curl_command(cmd)
        
        # Categorize
        if '/health' in cmd:
            categories['health'].append(i)
        elif '/tts' in cmd:
            categories['tts'].append(i)
        elif '/vc' in cmd:
            categories['vc'].append(i)
        elif '/voice' in cmd:
            categories['voice_mgmt'].append(i)
        elif '/outputs' in cmd or 'outputs/' in cmd:
            categories['file_ops'].append(i)
        elif parsed is None or 'temperature":2.0' in cmd or 'nonexistent' in cmd:
            categories['error_demos'].append(i)
        else:
            categories['other'].append(i)
    
    # Print categorization
    for category, indices in categories.items():
        if indices:
            print(f"=== {category.upper()} ({len(indices)} commands) ===")
            for idx in indices:
                cmd = commands[idx]['command']
                parsed = tester.parse_curl_command(cmd)
                status = "PARSABLE" if parsed else "PARSE_ERROR"
                print(f"  {idx}: {status} - {cmd[:60]}...")
            print()
    
    # Check for specific issues
    print("=== POTENTIAL ISSUES ===")
    
    parse_errors = 0
    file_ref_issues = 0
    
    for i, cmd_info in enumerate(commands):
        cmd = cmd_info['command']
        parsed = tester.parse_curl_command(cmd)
        
        if not parsed:
            parse_errors += 1
            print(f"Parse error #{parse_errors}: Command {i}")
            print(f"  {cmd[:80]}...")
            
        elif parsed and parsed.get('data'):
            # Check for file references
            data_str = json.dumps(parsed['data']) if isinstance(parsed['data'], dict) else str(parsed['data'])
            if any(ref in data_str for ref in ['speaker1/', 'speaker2/', 'my_recording.wav', 'long_speech.wav']):
                file_ref_issues += 1
                print(f"File reference issue #{file_ref_issues}: Command {i}")
                print(f"  References non-existent files")
    
    print(f"\nSUMMARY:")
    print(f"- Parse errors: {parse_errors}")
    print(f"- File reference issues: {file_ref_issues}")
    print(f"- Expected working commands: ~{len(categories['health']) + len(categories['file_ops'])}")
    print(f"- Expected slow commands (TTS/VC): ~{len(categories['tts']) + len(categories['vc'])}")
    print(f"- Expected error demos: ~{len(categories['error_demos'])}")


if __name__ == '__main__':
    diagnose_examples()
