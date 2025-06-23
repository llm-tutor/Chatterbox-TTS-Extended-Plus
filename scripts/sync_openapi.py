#!/usr/bin/env python3
"""
OpenAPI Sync Checker
Verifies that OpenAPI spec matches the actual API implementation
"""

import json
import sys
import requests
from pathlib import Path
from typing import Dict, Any, List, Set
import argparse
import yaml


class OpenAPISyncChecker:
    def __init__(self, api_base: str = "http://localhost:7860", openapi_file: str = "docs/api/openapi.yaml"):
        self.api_base = api_base.rstrip('/')
        self.openapi_file = Path(openapi_file)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def load_openapi_spec(self) -> Dict[str, Any]:
        """Load OpenAPI specification from file"""
        try:
            with open(self.openapi_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.errors.append(f"Failed to load OpenAPI spec: {e}")
            return {}
    
    def get_live_openapi(self) -> Dict[str, Any]:
        """Get OpenAPI spec from running server"""
        try:
            response = requests.get(f"{self.api_base}/openapi.json", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.errors.append(f"Failed to get live OpenAPI spec: {e}")
            return {}
    
    def extract_endpoints(self, spec: Dict[str, Any]) -> Set[str]:
        """Extract endpoint paths and methods from OpenAPI spec"""
        endpoints = set()
        
        if 'paths' not in spec:
            return endpoints
            
        for path, methods in spec['paths'].items():
            for method in methods.keys():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    endpoints.add(f"{method.upper()} {path}")
        
        return endpoints
    
    def compare_endpoints(self, file_spec: Dict[str, Any], live_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Compare endpoints between file and live specs"""
        file_endpoints = self.extract_endpoints(file_spec)
        live_endpoints = self.extract_endpoints(live_spec)
        
        missing_in_file = live_endpoints - file_endpoints
        missing_in_live = file_endpoints - live_endpoints
        common_endpoints = file_endpoints & live_endpoints
        
        return {
            'file_endpoints': file_endpoints,
            'live_endpoints': live_endpoints,
            'missing_in_file': missing_in_file,
            'missing_in_live': missing_in_live,
            'common_endpoints': common_endpoints
        }    
    def compare_schemas(self, file_spec: Dict[str, Any], live_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Compare schema definitions between specs"""
        file_schemas = set()
        live_schemas = set()
        
        if 'components' in file_spec and 'schemas' in file_spec['components']:
            file_schemas = set(file_spec['components']['schemas'].keys())
            
        if 'components' in live_spec and 'schemas' in live_spec['components']:
            live_schemas = set(live_spec['components']['schemas'].keys())
        
        return {
            'file_schemas': file_schemas,
            'live_schemas': live_schemas,
            'missing_in_file': live_schemas - file_schemas,
            'missing_in_live': file_schemas - live_schemas,
            'common_schemas': file_schemas & live_schemas
        }
    
    def check_sync(self) -> Dict[str, Any]:
        """Check synchronization between file and live OpenAPI specs"""
        file_spec = self.load_openapi_spec()
        live_spec = self.get_live_openapi()
        
        if not file_spec or not live_spec:
            return {}
        
        endpoint_comparison = self.compare_endpoints(file_spec, live_spec)
        schema_comparison = self.compare_schemas(file_spec, live_spec)
        
        # Generate warnings for discrepancies
        if endpoint_comparison['missing_in_file']:
            for endpoint in sorted(endpoint_comparison['missing_in_file']):
                self.warnings.append(f"Endpoint in live API but not in file: {endpoint}")
        
        if endpoint_comparison['missing_in_live']:
            for endpoint in sorted(endpoint_comparison['missing_in_live']):
                self.errors.append(f"Endpoint in file but not in live API: {endpoint}")
        
        if schema_comparison['missing_in_file']:
            for schema in sorted(schema_comparison['missing_in_file']):
                self.warnings.append(f"Schema in live API but not in file: {schema}")
        
        if schema_comparison['missing_in_live']:
            for schema in sorted(schema_comparison['missing_in_live']):
                self.warnings.append(f"Schema in file but not in live API: {schema}")
        
        return {
            'file_spec_version': file_spec.get('info', {}).get('version', 'unknown'),
            'live_spec_version': live_spec.get('info', {}).get('version', 'unknown'),
            'endpoints': endpoint_comparison,
            'schemas': schema_comparison,
            'sync_status': 'synced' if not self.errors and not self.warnings else 'out_of_sync'
        }    
    def print_results(self, results: Dict[str, Any]):
        """Print synchronization check results"""
        print(f"\n=== OpenAPI Synchronization Check ===")
        
        if not results:
            print("[ERROR] Failed to perform sync check - see errors above")
            return
        
        print(f"File spec version: {results['file_spec_version']}")
        print(f"Live spec version: {results['live_spec_version']}")
        print(f"Sync status: {results['sync_status']}")
        
        endpoints = results['endpoints']
        schemas = results['schemas']
        
        print(f"\nEndpoint Summary:")
        print(f"  File endpoints: {len(endpoints['file_endpoints'])}")
        print(f"  Live endpoints: {len(endpoints['live_endpoints'])}")
        print(f"  Common endpoints: {len(endpoints['common_endpoints'])}")
        
        print(f"\nSchema Summary:")
        print(f"  File schemas: {len(schemas['file_schemas'])}")
        print(f"  Live schemas: {len(schemas['live_schemas'])}")
        print(f"  Common schemas: {len(schemas['common_schemas'])}")
        
        if self.errors:
            print(f"\n=== ERRORS ({len(self.errors)}) ===")
            for error in self.errors:
                print(f"ERROR: {error}")
        
        if self.warnings:
            print(f"\n=== WARNINGS ({len(self.warnings)}) ===")
            for warning in self.warnings:
                print(f"WARNING: {warning}")
        
        if results['sync_status'] == 'synced':
            print("\n[OK] OpenAPI spec is synchronized!")
        else:
            print("\n[WARNING] OpenAPI spec is out of sync")


def main():
    parser = argparse.ArgumentParser(description='Check OpenAPI spec synchronization with live API')
    parser.add_argument('--api-base', default='http://localhost:7860',
                      help='API base URL (default: http://localhost:7860)')
    parser.add_argument('--openapi-file', default='docs/api/openapi.yaml',
                      help='OpenAPI spec file path (default: docs/api/openapi.yaml)')
    parser.add_argument('--strict', action='store_true',
                      help='Treat warnings as errors')
    
    args = parser.parse_args()
    
    # Check if OpenAPI file exists
    openapi_path = Path(args.openapi_file)
    if not openapi_path.exists():
        print(f"ERROR: OpenAPI file not found: {openapi_path}")
        sys.exit(1)
    
    # Run sync checker
    checker = OpenAPISyncChecker(args.api_base, args.openapi_file)
    results = checker.check_sync()
    checker.print_results(results)
    
    # Exit with error code if issues found
    total_issues = len(checker.errors)
    if args.strict:
        total_issues += len(checker.warnings)
    
    if total_issues > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
