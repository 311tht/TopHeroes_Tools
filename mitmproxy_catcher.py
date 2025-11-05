#!/usr/bin/env python3
"""
TopHeroes API Catcher - Simple Version
Uses mitmproxy to capture API calls
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from mitmproxy import http
from pathlib import Path

# Common modules
from common.filters import is_topheroes_api
from common.config import OUTPUT_DIR, OUTPUT_FILE_PREFIX, OUTPUT_FILE_SUFFIX, SUMMARY_FILE_SUFFIX
from common.utils import safe_json_parse, truncate_string
from common.logger import setup_logger

logger = setup_logger(__name__)


class TopHeroesCatcher:
    def __init__(self):
        self.api_calls = []
        self.start_time = datetime.now()
        logger.info("TopHeroes API Catcher initialized")
        
    def request(self, flow: http.HTTPFlow) -> None:
        """Capture HTTP request"""
        url = flow.request.url.lower()
        
        # Check if it's TopHeroes API
        if is_topheroes_api(url, dict(flow.request.headers)):
            api_data = {
                "timestamp": datetime.now().isoformat(),
                "method": flow.request.method,
                "url": flow.request.url,
                "headers": dict(flow.request.headers),
                "body": flow.request.content.decode('utf-8', errors='ignore') if flow.request.content else None,
                "client_address": getattr(flow.client_conn, 'address', 'unknown')
            }
            
            self.api_calls.append(api_data)
            self.print_request(api_data)
            logger.debug(f"Captured request: {api_data['method']} {api_data['url']}")
    
    def response(self, flow: http.HTTPFlow) -> None:
        """Capture HTTP response"""
        url = flow.request.url.lower()
        
        if is_topheroes_api(url, dict(flow.request.headers)):
            response_data = {
                "timestamp": datetime.now().isoformat(),
                "status_code": flow.response.status_code,
                "headers": dict(flow.response.headers),
                "body": flow.response.content.decode('utf-8', errors='ignore') if flow.response.content else None,
                "url": flow.request.url
            }
            
            self.print_response(response_data)
            
            # Lưu response vào API call tương ứng
            for api_call in reversed(self.api_calls):
                if api_call["url"] == flow.request.url:
                    api_call["response"] = response_data
                    break
    
    def print_request(self, api_data: Dict[str, Any]) -> None:
        """Print request information"""
        print(f"\n🔍 [{api_data['timestamp']}] {api_data['method']} {api_data['url']}")
        
        # Print important headers
        important_headers = ['Authorization', 'X-API-Key', 'Content-Type', 'User-Agent', 'Cookie']
        for header in important_headers:
            if header in api_data['headers']:
                value = api_data['headers'][header]
                if header == 'Authorization':
                    value = truncate_string(value, 50)
                print(f"   📋 {header}: {value}")
        
        # Print body if exists
        if api_data.get('body'):
            body_json = safe_json_parse(api_data['body'])
            if body_json:
                print(f"   📦 Body: {truncate_string(json.dumps(body_json, indent=2), 300)}")
            else:
                print(f"   📦 Body: {truncate_string(api_data['body'], 200)}")
    
    def print_response(self, response_data: Dict[str, Any]) -> None:
        """Print response information"""
        print(f"   📥 Response: {response_data['status_code']}")
        
        if response_data.get('body'):
            body_json = safe_json_parse(response_data['body'])
            if body_json:
                print(f"   📦 Response Body: {truncate_string(json.dumps(body_json, indent=2), 300)}")
            else:
                print(f"   📦 Response Body: {truncate_string(response_data['body'], 200)}")
    
    def save_results(self) -> None:
        """Save captured API calls to file"""
        if not self.api_calls:
            logger.info("No API calls captured")
            print("ℹ️  No API calls captured")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = OUTPUT_DIR / f"{OUTPUT_FILE_PREFIX}_{timestamp}{OUTPUT_FILE_SUFFIX}"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.api_calls, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(self.api_calls)} API calls to {filename}")
            print(f"\n💾 Saved {len(self.api_calls)} API calls to {filename}")
            
            # Create summary
            self.create_summary(filename)
            
        except (IOError, OSError) as e:
            logger.error(f"Error saving results: {e}", exc_info=True)
            print(f"❌ Error saving results: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving results: {e}", exc_info=True)
            raise
    
    def create_summary(self, filename: Path) -> None:
        """Create summary file"""
        summary_filename = filename.with_suffix(SUMMARY_FILE_SUFFIX.replace('_', ''))
        
        try:
            with open(summary_filename, 'w', encoding='utf-8') as f:
                f.write("TopHeroes API Calls Summary\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Total API calls captured: {len(self.api_calls)}\n")
                f.write(f"Capture time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Thống kê methods
                methods = {}
                for call in self.api_calls:
                    method = call['method']
                    methods[method] = methods.get(method, 0) + 1
                
                f.write("HTTP Methods used:\n")
                for method, count in methods.items():
                    f.write(f"  {method}: {count} calls\n")
                
                # Thống kê URLs
                f.write("\nUnique URLs found:\n")
                urls = set(call['url'] for call in self.api_calls)
                for url in sorted(urls):
                    f.write(f"  {url}\n")
                
                # Thống kê headers
                f.write("\nImportant Headers Found:\n")
                all_headers = set()
                for call in self.api_calls:
                    all_headers.update(call['headers'].keys())
                
                important_headers = ['Authorization', 'X-API-Key', 'Content-Type', 'User-Agent', 'Cookie', 'Referer']
                for header in important_headers:
                    if header in all_headers:
                        f.write(f"  ✓ {header}\n")
                
                # Thống kê response codes
                f.write("\nResponse Status Codes:\n")
                status_codes = {}
                for call in self.api_calls:
                    if 'response' in call:
                        status = call['response']['status_code']
                        status_codes[status] = status_codes.get(status, 0) + 1
                
                for status, count in status_codes.items():
                    f.write(f"  {status}: {count} responses\n")
            
            logger.info(f"Summary saved to {summary_filename}")
            print(f"📊 Summary saved to {summary_filename}")
            
        except (IOError, OSError) as e:
            logger.error(f"Error creating summary: {e}", exc_info=True)
            print(f"⚠️ Error creating summary: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating summary: {e}", exc_info=True)
            raise

# Tạo instance global
catcher = TopHeroesCatcher()

# Export functions cho mitmproxy
def request(flow: http.HTTPFlow) -> None:
    catcher.request(flow)

def response(flow: http.HTTPFlow) -> None:
    catcher.response(flow)

def done() -> None:
    """Called when mitmproxy stops"""
    logger.info("Stopping TopHeroes API Catcher")
    catcher.save_results()
    print("👋 TopHeroes API Catcher stopped!")
