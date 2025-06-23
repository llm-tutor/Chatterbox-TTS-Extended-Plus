#!/usr/bin/env python3
"""
Documentation Link Checker
Validates all internal links within the API documentation structure
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Set, Dict
import argparse


class LinkChecker:
    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.checked_files: Set[Path] = set()
        
    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files in the documentation tree"""
        md_files = []
        for root, dirs, files in os.walk(self.docs_root):
            for file in files:
                if file.endswith('.md'):
                    md_files.append(Path(root) / file)
        return md_files
    
    def remove_code_blocks(self, content: str) -> str:
        """Remove all code blocks from content to avoid false link detection"""
        # Remove fenced code blocks (```...```)
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        # Remove indented code blocks (4+ spaces at start of line)
        lines = content.split('\n')
        filtered_lines = []
        in_indented_code = False
        
        for line in lines:
            if line.startswith('    ') or line.startswith('\t'):
                in_indented_code = True
                continue
            elif in_indented_code and line.strip() == '':
                continue  # Skip blank lines in code blocks
            else:
                in_indented_code = False
                # Remove inline code (`...`)
                line = re.sub(r'`[^`]*`', '', line)
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def extract_links(self, content: str) -> List[Tuple[str, str]]:
        """Extract markdown links from content, excluding code blocks"""
        # Remove code blocks first to avoid false positives
        clean_content = self.remove_code_blocks(content)
        
        # Match both [text](link) and [text]: link patterns
        link_patterns = [
            r'\[([^\]]+)\]\(([^)]+)\)',  # [text](link)
            r'^\[([^\]]+)\]:\s*([^\s]+)',  # [text]: link (reference style)
        ]
        
        links = []
        for pattern in link_patterns:
            matches = re.finditer(pattern, clean_content, re.MULTILINE)
            for match in matches:
                text, link = match.groups()
                # Additional filtering for suspicious content
                if self._is_valid_link_format(text, link):
                    links.append((text.strip(), link.strip()))
        
        return links
    
    def _is_valid_link_format(self, text: str, link: str) -> bool:
        """Check if the extracted text and link look like valid markdown links"""
        # Skip if link contains characters that suggest it's not a real link
        suspicious_chars = ['"', "'", '{', '}', '\\n', '\\t', '\\r']
        if any(char in link for char in suspicious_chars):
            return False
            
        # Skip if text is too short or looks like code
        if len(text.strip()) < 3:
            return False
            
        # Skip if it looks like a code variable or constant
        if text.isupper() and '_' in text:  # ALL_CAPS_WITH_UNDERSCORES
            return False
            
        return True
    
    def is_internal_link(self, link: str) -> bool:
        """Check if link is internal (relative path or anchor)"""
        # Skip external URLs
        if link.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
            return False
        # Skip anchors only
        if link.startswith('#'):
            return False
        return True
    
    def resolve_link_path(self, current_file: Path, link: str) -> Path:
        """Resolve relative link to absolute path"""
        # Remove anchor fragment
        if '#' in link:
            link = link.split('#')[0]
        
        # If empty after removing anchor, it's same file
        if not link:
            return current_file
            
        # Handle absolute paths from docs root
        if link.startswith('/'):
            return self.docs_root / link[1:]
            
        # Handle relative paths
        if link.startswith('./'):
            link = link[2:]
        
        # Handle parent directory references and all relative paths
        # Start from current file's directory and resolve step by step
        current_dir = current_file.parent
        parts = link.split('/')
        
        for part in parts:
            if part == '..':
                current_dir = current_dir.parent
            elif part == '.' or part == '':
                continue  # Skip current directory references and empty parts
            else:
                current_dir = current_dir / part
                
        return current_dir
    
    def check_file_links(self, file_path: Path) -> int:
        """Check all links in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"Failed to read {file_path}: {e}")
            return 0
            
        links = self.extract_links(content)
        error_count = 0
        
        for link_text, link_url in links:
            if not self.is_internal_link(link_url):
                continue
                
            target_path = self.resolve_link_path(file_path, link_url)
            
            # Check if target exists
            if not target_path.exists():
                self.errors.append(
                    f"Broken link in {file_path.relative_to(self.docs_root)}: "
                    f"'{link_text}' -> '{link_url}' (resolved to {target_path})"
                )
                error_count += 1
            elif target_path.is_file() and target_path.suffix not in ['.md', '.yaml', '.yml', '.json']:
                self.warnings.append(
                    f"Non-markdown link in {file_path.relative_to(self.docs_root)}: "
                    f"'{link_text}' -> '{link_url}'"
                )
        
        return error_count
    
    def check_all_links(self) -> Dict[str, int]:
        """Check links in all markdown files"""
        md_files = self.find_markdown_files()
        
        stats = {
            'files_checked': 0,
            'total_errors': 0,
            'total_warnings': 0
        }
        
        for file_path in md_files:
            print(f"Checking {file_path.relative_to(self.docs_root)}...")
            errors_in_file = self.check_file_links(file_path)
            stats['files_checked'] += 1
            stats['total_errors'] += errors_in_file
            
        stats['total_warnings'] = len(self.warnings)
        return stats
    
    def print_results(self, stats: Dict[str, int]):
        """Print check results"""
        print(f"\n=== Link Check Results ===")
        print(f"Files checked: {stats['files_checked']}")
        print(f"Errors found: {stats['total_errors']}")
        print(f"Warnings: {stats['total_warnings']}")
        
        if self.errors:
            print(f"\n=== ERRORS ({len(self.errors)}) ===")
            for error in self.errors:
                print(f"ERROR: {error}")
        
        if self.warnings:
            print(f"\n=== WARNINGS ({len(self.warnings)}) ===")
            for warning in self.warnings:
                print(f"WARNING: {warning}")
        
        if not self.errors and not self.warnings:
            print("\n[OK] All links are valid!")



def main():
    parser = argparse.ArgumentParser(description='Check internal links in API documentation')
    parser.add_argument('--docs-root', default='docs/api', 
                      help='Root directory of documentation (default: docs/api)')
    parser.add_argument('--strict', action='store_true',
                      help='Treat warnings as errors')
    
    args = parser.parse_args()
    
    # Resolve docs root path
    docs_root = Path(args.docs_root)
    if not docs_root.is_absolute():
        docs_root = Path.cwd() / docs_root
    
    if not docs_root.exists():
        print(f"ERROR: Documentation root not found: {docs_root}")
        sys.exit(1)
    
    # Run link checker
    checker = LinkChecker(docs_root)
    stats = checker.check_all_links()
    checker.print_results(stats)
    
    # Exit with error code if issues found
    total_issues = stats['total_errors']
    if args.strict:
        total_issues += stats['total_warnings']
    
    if total_issues > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
