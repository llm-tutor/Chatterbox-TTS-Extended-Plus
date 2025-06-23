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
    
    def extract_links(self, content: str) -> List[Tuple[str, str]]:
        """Extract markdown links from content"""
        # Match both [text](link) and [text]: link patterns
        link_patterns = [
            r'\[([^\]]+)\]\(([^)]+)\)',  # [text](link)
            r'\[([^\]]+)\]:\s*([^\s]+)',  # [text]: link
        ]
        
        links = []
        for pattern in link_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                text, link = match.groups()
                links.append((text.strip(), link.strip()))
        
        return links
    
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
            
        # Resolve relative to current file's directory
        if link.startswith('./'):
            link = link[2:]
        elif link.startswith('../'):
            # Handle parent directory references
            parts = link.split('/')
            current_dir = current_file.parent
            for part in parts:
                if part == '..':
                    current_dir = current_dir.parent
                elif part and part != '.':
                    current_dir = current_dir / part
            return current_dir
        
        # Relative to current file's directory
        return current_file.parent / link    
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
            elif target_path.is_file() and not target_path.suffix == '.md':
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
