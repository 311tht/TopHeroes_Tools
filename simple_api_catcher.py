#!/usr/bin/env python3
"""
TopHeroes Simple API Catcher
Bắt API calls đơn giản không cần SSL certificate
"""

import socket
import threading
import json
import time
from datetime import datetime
import re

class SimpleAPICatcher:
    def __init__(self, port=8080):
        self.port = port
        self.api_calls = []
        self.running = False
        
    def start_server(self):
        """Khởi động HTTP proxy server"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('127.0.0.1', self.port))
            server_socket.listen(5)
            self.running = True
            
            print(f"🚀 Simple API Catcher started on port {self.port}")
            print(f"📱 Configure proxy: 127.0.0.1:{self.port}")
            print("🎮 Play TopHeroes now!")
            print("⏹️  Press Ctrl+C to stop")
            
            while self.running:
                try:
                    client_socket, address = server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.error:
                    break
                    
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            server_socket.close()
    
    def handle_client(self, client_socket, address):
        """Xử lý client connection"""
        try:
            request_data = client_socket.recv(4096).decode('utf-8', errors='ignore')
            if request_data:
                self.parse_and_log_request(request_data, address)
                
                # Trả về response đơn giản
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nOK"
                client_socket.send(response.encode())
                
        except Exception as e:
            print(f"⚠️ Error handling client: {e}")
        finally:
            client_socket.close()
    
    def parse_and_log_request(self, request_data, address):
        """Phân tích và log request"""
        try:
            lines = request_data.split('\n')
            if not lines:
                return
                
            # Parse request line
            request_line = lines[0]
            parts = request_line.split(' ')
            if len(parts) < 3:
                return
                
            method = parts[0]
            url = parts[1]
            protocol = parts[2]
            
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
            
            # Kiểm tra xem có phải TopHeroes không
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
    
    def is_topheroes_request(self, url, headers):
        """Kiểm tra xem có phải TopHeroes request không"""
        topheroes_keywords = [
            'topheroes', 'topwar', 'topwarapp', 'tophero-cdn',
            'game', 'api', 'login', 'user', 'player', 'battle',
            'mission', 'quest', 'reward', 'item', 'shop', 'guild'
        ]
        
        url_lower = url.lower()
        user_agent = headers.get('User-Agent', '').lower()
        host = headers.get('Host', '').lower()
        
        # Kiểm tra URL
        for keyword in topheroes_keywords:
            if keyword in url_lower:
                return True
        
        # Kiểm tra Host header
        for keyword in topheroes_keywords:
            if keyword in host:
                return True
                
        # Kiểm tra User-Agent
        for keyword in topheroes_keywords:
            if keyword in user_agent:
                return True
                
        return False
    
    def print_api_call(self, api_call):
        """In thông tin API call"""
        print(f"\n🔍 [{api_call['timestamp']}] {api_call['method']} {api_call['url']}")
        
        # In headers quan trọng
        important_headers = ['Host', 'User-Agent', 'Authorization', 'Content-Type', 'Cookie']
        for header in important_headers:
            if header in api_call['headers']:
                value = api_call['headers'][header]
                if len(value) > 100:
                    value = value[:100] + "..."
                print(f"   📋 {header}: {value}")
        
        # In body nếu có
        if api_call['body']:
            print(f"   📦 Body: {api_call['body'][:200]}...")
    
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
            print(f"❌ Error saving: {e}")
    
    def create_summary(self, filename):
        """Tạo file tóm tắt"""
        summary_filename = filename.replace('.json', '_summary.txt')
        
        try:
            with open(summary_filename, 'w', encoding='utf-8') as f:
                f.write("TopHeroes API Calls Summary\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Total API calls captured: {len(self.api_calls)}\n")
                f.write(f"Capture time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Thống kê methods
                methods = {}
                for call in self.api_calls:
                    method = call['method']
                    methods[method] = methods.get(method, 0) + 1
                
                f.write("HTTP Methods:\n")
                for method, count in methods.items():
                    f.write(f"  {method}: {count} calls\n")
                
                # Thống kê URLs
                f.write("\nUnique URLs:\n")
                urls = set(call['url'] for call in self.api_calls)
                for url in sorted(urls):
                    f.write(f"  {url}\n")
                
                # Thống kê Hosts
                f.write("\nHosts found:\n")
                hosts = set()
                for call in self.api_calls:
                    host = call['headers'].get('Host', '')
                    if host:
                        hosts.add(host)
                
                for host in sorted(hosts):
                    f.write(f"  {host}\n")
            
            print(f"📊 Summary saved to {summary_filename}")
            
        except Exception as e:
            print(f"⚠️ Error creating summary: {e}")
    
    def stop(self):
        """Dừng server"""
        self.running = False

def main():
    print("🎮 TopHeroes Simple API Catcher")
    print("=" * 40)
    
    catcher = SimpleAPICatcher()
    
    try:
        catcher.start_server()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping...")
        catcher.stop()
        catcher.save_results()
        print("👋 Done!")

if __name__ == "__main__":
    main()

