#!/usr/bin/env python3
"""
TopHeroes API Catcher Tool
Bắt và phân tích API calls từ game TopHeroes
"""

import json
import time
import threading
import requests
import socket
from datetime import datetime
from typing import Dict, List, Any
import os
import sys

class TopHeroesAPICatcher:
    def __init__(self, port: int = 8080):
        self.port = port
        self.api_calls = []
        self.running = False
        self.server_socket = None
        self.clients = []
        
    def start_proxy_server(self):
        """Khởi động proxy server để bắt traffic"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('127.0.0.1', self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"🚀 Proxy server started on port {self.port}")
            print(f"📱 Configure your device/emulator to use proxy: 127.0.0.1:{self.port}")
            print("🎮 Now start TopHeroes game and perform actions...")
            print("⏹️  Press Ctrl+C to stop and save results")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client, 
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.error:
                    break
                    
        except Exception as e:
            print(f"❌ Error starting proxy server: {e}")
    
    def handle_client(self, client_socket, address):
        """Xử lý client connection"""
        try:
            request_data = client_socket.recv(4096).decode('utf-8')
            if request_data:
                self.parse_request(request_data, address)
                
                # Forward request to actual server
                response = self.forward_request(request_data)
                if response:
                    client_socket.send(response)
                    
        except Exception as e:
            print(f"⚠️ Error handling client {address}: {e}")
        finally:
            client_socket.close()
    
    def parse_request(self, request_data: str, address):
        """Phân tích HTTP request"""
        try:
            lines = request_data.split('\n')
            if not lines:
                return
                
            # Parse request line
            request_line = lines[0]
            method, url, protocol = request_line.split(' ', 2)
            
            # Parse headers
            headers = {}
            body_start = 0
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '':
                    body_start = i + 1
                    break
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
            
            # Parse body
            body = '\n'.join(lines[body_start:]) if body_start < len(lines) else ''
            
            # Check if it's TopHeroes related
            if self.is_topheroes_request(url, headers):
                api_call = {
                    "timestamp": datetime.now().isoformat(),
                    "method": method,
                    "url": url,
                    "headers": headers,
                    "body": body,
                    "client_address": address[0]
                }
                
                self.api_calls.append(api_call)
                self.print_api_call(api_call)
                
        except Exception as e:
            print(f"⚠️ Error parsing request: {e}")
    
    def is_topheroes_request(self, url: str, headers: Dict[str, str]) -> bool:
        """Kiểm tra xem request có phải từ TopHeroes không"""
        topheroes_keywords = [
            'topheroes', 'topwar', 'topwarapp', 'game', 'api',
            'login', 'user', 'player', 'battle', 'mission',
            'quest', 'reward', 'item', 'shop', 'guild'
        ]
        
        url_lower = url.lower()
        user_agent = headers.get('User-Agent', '').lower()
        
        # Check URL
        for keyword in topheroes_keywords:
            if keyword in url_lower:
                return True
        
        # Check User-Agent
        for keyword in topheroes_keywords:
            if keyword in user_agent:
                return True
                
        return False
    
    def print_api_call(self, api_call: Dict[str, Any]):
        """In thông tin API call"""
        print(f"\n🔍 [{api_call['timestamp']}] {api_call['method']} {api_call['url']}")
        
        # Print important headers
        important_headers = ['Authorization', 'X-API-Key', 'Content-Type', 'User-Agent']
        for header in important_headers:
            if header in api_call['headers']:
                print(f"   📋 {header}: {api_call['headers'][header]}")
        
        # Print body if exists
        if api_call['body']:
            try:
                body_json = json.loads(api_call['body'])
                print(f"   📦 Body: {json.dumps(body_json, indent=2)[:200]}...")
            except:
                print(f"   📦 Body: {api_call['body'][:100]}...")
    
    def forward_request(self, request_data: str) -> bytes:
        """Forward request to actual server"""
        try:
            lines = request_data.split('\n')
            request_line = lines[0]
            method, url, protocol = request_line.split(' ', 2)
            
            # Extract host from URL or Host header
            host = None
            for line in lines[1:]:
                if line.lower().startswith('host:'):
                    host = line.split(':', 1)[1].strip()
                    break
            
            if not host:
                return b"HTTP/1.1 400 Bad Request\r\n\r\n"
            
            # Forward request
            response = requests.request(
                method=method,
                url=f"http://{host}{url}",
                headers=self.parse_headers(request_data),
                data=self.parse_body(request_data),
                timeout=10
            )
            
            return response.content
            
        except Exception as e:
            print(f"⚠️ Error forwarding request: {e}")
            return b"HTTP/1.1 500 Internal Server Error\r\n\r\n"
    
    def parse_headers(self, request_data: str) -> Dict[str, str]:
        """Parse headers from request"""
        headers = {}
        lines = request_data.split('\n')
        
        for line in lines[1:]:
            if line.strip() == '':
                break
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        
        return headers
    
    def parse_body(self, request_data: str) -> str:
        """Parse body from request"""
        lines = request_data.split('\n')
        body_start = 0
        
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '':
                body_start = i + 1
                break
        
        return '\n'.join(lines[body_start:]) if body_start < len(lines) else ''
    
    def save_results(self, filename: str = None):
        """Lưu kết quả vào file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"topheroes_api_calls_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.api_calls, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Saved {len(self.api_calls)} API calls to {filename}")
            
            # Create summary
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
                f.write(f"Capture time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Group by method
                methods = {}
                for call in self.api_calls:
                    method = call['method']
                    methods[method] = methods.get(method, 0) + 1
                
                f.write("Methods used:\n")
                for method, count in methods.items():
                    f.write(f"  {method}: {count} calls\n")
                
                f.write("\nUnique URLs:\n")
                urls = set(call['url'] for call in self.api_calls)
                for url in sorted(urls):
                    f.write(f"  {url}\n")
                
                f.write("\nImportant Headers Found:\n")
                all_headers = set()
                for call in self.api_calls:
                    all_headers.update(call['headers'].keys())
                
                important_headers = ['Authorization', 'X-API-Key', 'Content-Type', 'User-Agent', 'Cookie']
                for header in important_headers:
                    if header in all_headers:
                        f.write(f"  ✓ {header}\n")
            
            print(f"📊 Summary saved to {summary_filename}")
            
        except Exception as e:
            print(f"⚠️ Error creating summary: {e}")
    
    def stop(self):
        """Dừng proxy server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("\n⏹️  Proxy server stopped")

def main():
    print("🎮 TopHeroes API Catcher Tool")
    print("=" * 40)
    
    # Get port from user
    try:
        port = int(input("Enter proxy port (default 8080): ") or "8080")
    except ValueError:
        port = 8080
    
    catcher = TopHeroesAPICatcher(port)
    
    try:
        # Start proxy server
        catcher.start_proxy_server()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping...")
        catcher.stop()
        
        # Save results
        if catcher.api_calls:
            catcher.save_results()
        else:
            print("ℹ️  No API calls captured")
        
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
