#!/usr/bin/env python3
"""
TopHeroes Simple API Catcher
Simple API catcher without SSL certificate requirements
"""

import socket
import threading
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
from contextlib import contextmanager

# Common modules
from common.filters import is_topheroes_api
from common.config import (
    DEFAULT_PROXY_PORT, DEFAULT_PROXY_HOST, BUFFER_SIZE,
    OUTPUT_DIR, OUTPUT_FILE_PREFIX, OUTPUT_FILE_SUFFIX, SUMMARY_FILE_SUFFIX
)
from common.utils import safe_json_parse, truncate_string
from common.logger import setup_logger

logger = setup_logger(__name__)


class SimpleAPICatcher:
    def __init__(self, port: int = DEFAULT_PROXY_PORT, host: str = DEFAULT_PROXY_HOST):
        self.port = port
        self.host = host
        self.api_calls: List[Dict[str, Any]] = []
        self.running = False
        logger.info(f"SimpleAPICatcher initialized on {host}:{port}")
        
    def start_server(self) -> None:
        """Start HTTP proxy server"""
        server_socket = None
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            self.running = True
            
            logger.info(f"Simple API Catcher started on {self.host}:{self.port}")
            print(f"🚀 Simple API Catcher started on port {self.port}")
            print(f"📱 Configure proxy: {self.host}:{self.port}")
            print("🎮 Play TopHeroes now!")
            print("⏹️  Press Ctrl+C to stop")
            
            while self.running:
                try:
                    client_socket, address = server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                except (socket.error, OSError) as e:
                    logger.warning(f"Socket error: {e}")
                    break
                    
        except (socket.error, OSError) as e:
            logger.error(f"Error starting server: {e}", exc_info=True)
            print(f"❌ Error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error starting server: {e}", exc_info=True)
            raise
        finally:
            if server_socket:
                try:
                    server_socket.close()
                except socket.error:
                    pass
    
    def handle_client(self, client_socket: socket.socket, address: Tuple[str, int]) -> None:
        """Handle client connection"""
        try:
            with self.client_connection(client_socket):
                request_data = client_socket.recv(BUFFER_SIZE).decode('utf-8', errors='ignore')
                if request_data:
                    self.parse_and_log_request(request_data, address)
                    
                    # Return simple response
                    response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nOK"
                    client_socket.send(response.encode())
                    
        except (socket.error, ConnectionError) as e:
            logger.warning(f"Error handling client {address}: {e}")
            print(f"⚠️ Error handling client: {e}")
        except Exception as e:
            logger.error(f"Unexpected error handling client {address}: {e}", exc_info=True)
    
    @contextmanager
    def client_connection(self, client_socket: socket.socket):
        """Context manager for client socket connection"""
        try:
            yield client_socket
        finally:
            try:
                client_socket.close()
            except socket.error:
                pass
    
    def parse_and_log_request(self, request_data: str, address: Tuple[str, int]) -> None:
        """Parse and log request"""
        try:
            lines = request_data.split('\n')
            if not lines:
                return
                
            # Parse request line
            request_line = lines[0]
            parts = request_line.split(' ', 2)
            if len(parts) < 3:
                return
                
            method, url, protocol = parts
            
            # Parse headers
            headers = self.parse_headers(request_data)
            
            # Parse body
            body = self.parse_body(request_data)
            
            # Check if it's TopHeroes request
            if is_topheroes_api(url, headers):
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
                logger.debug(f"Captured request: {method} {url}")
                
        except (ValueError, IndexError) as e:
            logger.warning(f"Error parsing request: {e}")
            print(f"⚠️ Error parsing request: {e}")
        except Exception as e:
            logger.error(f"Unexpected error parsing request: {e}", exc_info=True)
    
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
    
    def print_api_call(self, api_call: Dict[str, Any]) -> None:
        """Print API call information"""
        print(f"\n🔍 [{api_call['timestamp']}] {api_call['method']} {api_call['url']}")
        
        # Print important headers
        important_headers = ['Host', 'User-Agent', 'Authorization', 'Content-Type', 'Cookie']
        for header in important_headers:
            if header in api_call['headers']:
                value = api_call['headers'][header]
                if header == 'Authorization':
                    value = truncate_string(value, 50)
                else:
                    value = truncate_string(value, 100)
                print(f"   📋 {header}: {value}")
        
        # Print body if exists
        if api_call.get('body'):
            body_json = safe_json_parse(api_call['body'])
            if body_json:
                print(f"   📦 Body: {truncate_string(json.dumps(body_json, indent=2), 200)}")
            else:
                print(f"   📦 Body: {truncate_string(api_call['body'], 200)}")
    
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
            logger.error(f"Error saving: {e}", exc_info=True)
            print(f"❌ Error saving: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving: {e}", exc_info=True)
            raise
    
    def create_summary(self, filename: Path) -> None:
        """Create summary file"""
        summary_filename = filename.with_suffix(SUMMARY_FILE_SUFFIX.replace('_', ''))
        
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
            
            logger.info(f"Summary saved to {summary_filename}")
            print(f"📊 Summary saved to {summary_filename}")
            
        except (IOError, OSError) as e:
            logger.error(f"Error creating summary: {e}", exc_info=True)
            print(f"⚠️ Error creating summary: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating summary: {e}", exc_info=True)
            raise
    
    def stop(self) -> None:
        """Stop server"""
        self.running = False
        logger.info("Server stopped")

def main() -> None:
    """Main entry point"""
    print("🎮 TopHeroes Simple API Catcher")
    print("=" * 40)
    
    catcher = SimpleAPICatcher()
    
    try:
        catcher.start_server()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        print("\n\n🛑 Stopping...")
        catcher.stop()
        catcher.save_results()
        print("👋 Done!")

if __name__ == "__main__":
    main()

