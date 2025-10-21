#!/usr/bin/env python3
"""
TopHeroes API Tester
Test các API calls đã capture được
"""

import requests
import json
import time
from datetime import datetime

class TopHeroesAPITester:
    def __init__(self, base_url="https://api.topheroes.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.player_id = None
        
    def load_api_calls(self, filename):
        """Load API calls từ file JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading API calls: {e}")
            return []
    
    def extract_credentials(self, api_calls):
        """Trích xuất thông tin đăng nhập từ API calls"""
        login_calls = []
        
        for call in api_calls:
            if 'login' in call['url'].lower() and call['method'] == 'POST':
                login_calls.append(call)
        
        return login_calls
    
    def extract_tokens(self, api_calls):
        """Trích xuất tokens từ API calls"""
        tokens = set()
        
        for call in api_calls:
            headers = call.get('headers', {})
            
            # Tìm Authorization header
            if 'Authorization' in headers:
                auth = headers['Authorization']
                if 'Bearer' in auth:
                    token = auth.replace('Bearer ', '').strip()
                    tokens.add(token)
            
            # Tìm trong response
            if 'response' in call:
                response_body = call['response'].get('body', '')
                try:
                    response_json = json.loads(response_body)
                    if 'token' in response_json:
                        tokens.add(response_json['token'])
                    if 'access_token' in response_json:
                        tokens.add(response_json['access_token'])
                except:
                    pass
        
        return list(tokens)
    
    def test_login(self, username, password):
        """Test đăng nhập"""
        print(f"🔐 Testing login for: {username}")
        
        login_data = {
            "username": username,
            "password": password,
            "device_id": "test_device_123"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/login",
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.player_id = data.get('player_id')
                print(f"✅ Login successful! Token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_get_player_info(self):
        """Test lấy thông tin player"""
        if not self.token:
            print("❌ No token available")
            return None
        
        print("👤 Getting player info...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/player/info",
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Player info: {json.dumps(data, indent=2)}")
                return data
            else:
                print(f"❌ Failed to get player info: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting player info: {e}")
            return None
    
    def test_battle_apis(self):
        """Test các API battle"""
        if not self.token:
            print("❌ No token available")
            return
        
        print("⚔️ Testing battle APIs...")
        
        # Test get battle list
        try:
            response = self.session.get(
                f"{self.base_url}/battle/list",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if response.status_code == 200:
                battles = response.json()
                print(f"✅ Found {len(battles)} battles")
                
                # Test start battle với battle đầu tiên
                if battles:
                    battle_id = battles[0].get('id')
                    self.test_start_battle(battle_id)
            else:
                print(f"❌ Failed to get battle list: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing battle APIs: {e}")
    
    def test_start_battle(self, battle_id):
        """Test bắt đầu battle"""
        print(f"⚔️ Testing start battle: {battle_id}")
        
        battle_data = {
            "battle_id": battle_id,
            "formation": [1, 2, 3, 4, 5]  # Default formation
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/battle/start",
                json=battle_data,
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Battle started: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"❌ Failed to start battle: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error starting battle: {e}")
            return None
    
    def test_shop_apis(self):
        """Test các API shop"""
        if not self.token:
            print("❌ No token available")
            return
        
        print("🛒 Testing shop APIs...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/shop/items",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if response.status_code == 200:
                items = response.json()
                print(f"✅ Found {len(items)} shop items")
                return items
            else:
                print(f"❌ Failed to get shop items: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error testing shop APIs: {e}")
            return None
    
    def run_comprehensive_test(self, api_calls_file):
        """Chạy test toàn diện"""
        print("🧪 TopHeroes API Comprehensive Test")
        print("=" * 50)
        
        # Load API calls
        api_calls = self.load_api_calls(api_calls_file)
        if not api_calls:
            print("❌ No API calls found")
            return
        
        print(f"📊 Loaded {len(api_calls)} API calls")
        
        # Extract credentials
        login_calls = self.extract_credentials(api_calls)
        tokens = self.extract_tokens(api_calls)
        
        print(f"🔐 Found {len(login_calls)} login calls")
        print(f"🎫 Found {len(tokens)} tokens")
        
        # Test với token nếu có
        if tokens:
            self.token = tokens[0]
            print(f"🎫 Using token: {self.token[:20]}...")
            
            # Test các API
            self.test_get_player_info()
            self.test_battle_apis()
            self.test_shop_apis()
        else:
            print("ℹ️  No tokens found, skipping API tests")
        
        print("\n✅ Comprehensive test completed!")

def main():
    print("🎮 TopHeroes API Tester")
    print("=" * 30)
    
    # Tìm file API calls mới nhất
    import glob
    api_files = glob.glob("topheroes_api_calls_*.json")
    
    if not api_files:
        print("❌ No API calls file found")
        print("💡 Run the API catcher first to capture some calls")
        return
    
    # Sử dụng file mới nhất
    latest_file = max(api_files, key=os.path.getctime)
    print(f"📁 Using API calls file: {latest_file}")
    
    # Tạo tester
    tester = TopHeroesAPITester()
    
    # Chạy test
    tester.run_comprehensive_test(latest_file)

if __name__ == "__main__":
    import os
    main()
