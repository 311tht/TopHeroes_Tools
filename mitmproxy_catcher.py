#!/usr/bin/env python3
"""
TopHeroes API Catcher - Simple Version
Sử dụng mitmproxy để bắt API calls
"""

import json
import time
from datetime import datetime
from mitmproxy import http
import os

class TopHeroesCatcher:
    def __init__(self):
        self.api_calls = []
        self.start_time = datetime.now()
        
    def request(self, flow: http.HTTPFlow) -> None:
        """Bắt HTTP request"""
        url = flow.request.url.lower()
        
        # Kiểm tra xem có phải TopHeroes API không
        if self.is_topheroes_api(url, flow.request.headers):
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
    
    def response(self, flow: http.HTTPFlow) -> None:
        """Bắt HTTP response"""
        url = flow.request.url.lower()
        
        if self.is_topheroes_api(url, flow.request.headers):
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
    
    def is_topheroes_api(self, url: str, headers: dict) -> bool:
        """Kiểm tra xem có phải TopHeroes API không"""
        topheroes_domains = [
            'topheroes', 'topwar', 'topwarapp', 'game', 'api',
            'login', 'user', 'player', 'battle', 'mission',
            'quest', 'reward', 'item', 'shop', 'guild'
        ]
        
        # Kiểm tra URL
        for domain in topheroes_domains:
            if domain in url:
                return True
        
        # Kiểm tra User-Agent
        user_agent = headers.get('User-Agent', '').lower()
        for domain in topheroes_domains:
            if domain in user_agent:
                return True
        
        # Kiểm tra Referer
        referer = headers.get('Referer', '').lower()
        for domain in topheroes_domains:
            if domain in referer:
                return True
                
        return False
    
    def print_request(self, api_data: dict):
        """In thông tin request"""
        print(f"\n🔍 [{api_data['timestamp']}] {api_data['method']} {api_data['url']}")
        
        # In headers quan trọng
        important_headers = ['Authorization', 'X-API-Key', 'Content-Type', 'User-Agent', 'Cookie']
        for header in important_headers:
            if header in api_data['headers']:
                value = api_data['headers'][header]
                if header == 'Authorization' and len(value) > 50:
                    value = value[:50] + "..."
                print(f"   📋 {header}: {value}")
        
        # In body nếu có
        if api_data['body']:
            try:
                body_json = json.loads(api_data['body'])
                print(f"   📦 Body: {json.dumps(body_json, indent=2)[:300]}...")
            except:
                print(f"   📦 Body: {api_data['body'][:200]}...")
    
    def print_response(self, response_data: dict):
        """In thông tin response"""
        print(f"   📥 Response: {response_data['status_code']}")
        
        if response_data['body']:
            try:
                body_json = json.loads(response_data['body'])
                print(f"   📦 Response Body: {json.dumps(body_json, indent=2)[:300]}...")
            except:
                print(f"   📦 Response Body: {response_data['body'][:200]}...")
    
    def save_results(self):
        """Lưu kết quả"""
        if not self.api_calls:
            print("ℹ️  No API calls captured")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"topheroes_api_calls_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.api_calls, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Saved {len(self.api_calls)} API calls to {filename}")
            
            # Tạo summary
            self.create_summary(filename)
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
    
    def create_summary(self, filename: str):
        """Tạo file tóm tắt"""
        summary_filename = filename.replace('.json', '_summary.txt')
        
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
            
            print(f"📊 Summary saved to {summary_filename}")
            
        except Exception as e:
            print(f"⚠️ Error creating summary: {e}")

# Tạo instance global
catcher = TopHeroesCatcher()

# Export functions cho mitmproxy
def request(flow: http.HTTPFlow) -> None:
    catcher.request(flow)

def response(flow: http.HTTPFlow) -> None:
    catcher.response(flow)

def done():
    """Được gọi khi mitmproxy dừng"""
    catcher.save_results()
    print("👋 TopHeroes API Catcher stopped!")
