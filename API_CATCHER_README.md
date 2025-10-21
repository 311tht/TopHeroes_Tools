# TopHeroes API Catcher Tool

Tool để bắt và phân tích API calls từ game TopHeroes, giúp hiểu cấu trúc API và tạo automation tools.

## 🎯 Mục đích

- **Bắt API calls**: Capture tất cả HTTP/HTTPS requests từ game TopHeroes
- **Phân tích cấu trúc**: Hiểu cách game giao tiếp với server
- **Tạo automation**: Sử dụng API để tự động hóa các tác vụ game
- **Reverse engineering**: Phân tích logic game và tạo tools tương ứng

## 🚀 Cài đặt nhanh

### Bước 1: Chạy setup script
```bash
chmod +x setup_api_catcher.sh
./setup_api_catcher.sh
```

### Bước 2: Cấu hình proxy
```bash
./setup_proxy.sh
```

### Bước 3: Chạy API catcher
```bash
./run_catcher.sh
```

## 📱 Cấu hình Proxy

### Trên máy tính (macOS):
1. **System Preferences** → **Network**
2. Chọn **WiFi** → **Advanced** → **Proxies**
3. Tick **Web Proxy (HTTP)** và **Secure Web Proxy (HTTPS)**
4. Server: `127.0.0.1`, Port: `8080`
5. Nhấn **OK** và **Apply**

### Trên điện thoại/emulator:
1. Vào **Settings** → **WiFi**
2. Chọn mạng WiFi → **Configure Proxy**
3. Manual: Server `127.0.0.1`, Port `8080`

## 🎮 Cách sử dụng

### 1. Khởi động API Catcher
```bash
./run_catcher.sh
```

### 2. Chạy game TopHeroes
- Mở game trên máy tính hoặc điện thoại
- Thực hiện các hành động: đăng nhập, chơi game, mua item, etc.

### 3. Xem kết quả
- API calls sẽ được hiển thị real-time trong terminal
- Dữ liệu được lưu tự động vào file JSON

### 4. Phân tích dữ liệu
```bash
# Xem file JSON
cat topheroes_api_calls_*.json

# Xem summary
cat topheroes_api_calls_*_summary.txt
```

## 📊 Dữ liệu được capture

### Request Data:
- **Method**: GET, POST, PUT, DELETE
- **URL**: Endpoint API
- **Headers**: Authorization, Content-Type, User-Agent, etc.
- **Body**: JSON data gửi lên server
- **Timestamp**: Thời gian request

### Response Data:
- **Status Code**: 200, 404, 500, etc.
- **Headers**: Response headers
- **Body**: JSON data từ server
- **Timestamp**: Thời gian response

## 🔍 Ví dụ API calls thường gặp

### Login API:
```json
{
  "method": "POST",
  "url": "https://api.topheroes.com/login",
  "body": {
    "username": "player123",
    "password": "encrypted_password",
    "device_id": "unique_device_id"
  }
}
```

### Get Player Info:
```json
{
  "method": "GET", 
  "url": "https://api.topheroes.com/player/info",
  "headers": {
    "Authorization": "Bearer token_here"
  }
}
```

### Battle API:
```json
{
  "method": "POST",
  "url": "https://api.topheroes.com/battle/start",
  "body": {
    "enemy_id": 12345,
    "formation": [1, 2, 3, 4, 5]
  }
}
```

## 🛠️ Tạo Automation Tool

Sau khi có API calls, bạn có thể tạo automation:

### 1. Tạo Python script
```python
import requests
import json

class TopHeroesAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def login(self, username, password):
        response = requests.post(
            f"{self.base_url}/login",
            json={"username": username, "password": password}
        )
        return response.json()
    
    def get_player_info(self):
        response = requests.get(
            f"{self.base_url}/player/info",
            headers=self.headers
        )
        return response.json()
    
    def start_battle(self, enemy_id, formation):
        response = requests.post(
            f"{self.base_url}/battle/start",
            json={"enemy_id": enemy_id, "formation": formation},
            headers=self.headers
        )
        return response.json()
```

### 2. Sử dụng API
```python
api = TopHeroesAPI("https://api.topheroes.com", "your_token")

# Lấy thông tin player
player_info = api.get_player_info()
print(f"Player level: {player_info['level']}")

# Bắt đầu battle
battle_result = api.start_battle(12345, [1, 2, 3, 4, 5])
print(f"Battle result: {battle_result['result']}")
```

## 📁 Cấu trúc file

```
api_catcher/
├── api_catcher.py              # Tool chính (standalone)
├── mitmproxy_catcher.py        # Tool sử dụng mitmproxy
├── setup_api_catcher.sh        # Script cài đặt
├── setup_proxy.sh              # Script cấu hình proxy
├── run_catcher.sh              # Script chạy tool
├── config.json                 # File cấu hình
└── logs/                       # Thư mục lưu logs
    ├── topheroes_api_calls_*.json
    └── topheroes_api_calls_*_summary.txt
```

## ⚠️ Lưu ý quan trọng

### Bảo mật:
- **Không chia sẻ** file chứa API calls với người khác
- **Xóa** file logs sau khi phân tích xong
- **Không commit** file chứa token/password vào Git

### Sử dụng có trách nhiệm:
- Chỉ sử dụng cho mục đích học tập và nghiên cứu
- Tuân thủ Terms of Service của game
- Không sử dụng để gian lận hoặc làm hại người khác

### Troubleshooting:
1. **Không bắt được API**: Kiểm tra proxy settings
2. **Lỗi SSL**: Cài đặt mitmproxy certificate
3. **Game không hoạt động**: Tắt proxy sau khi capture xong

## 🔧 Troubleshooting

### Lỗi thường gặp:

1. **"Permission denied"**:
   ```bash
   chmod +x *.sh
   ```

2. **"mitmproxy not found"**:
   ```bash
   pip3 install mitmproxy
   ```

3. **"Cannot connect to proxy"**:
   - Kiểm tra port 8080 có bị chiếm không
   - Thử port khác: `mitmdump -p 8081`

4. **"SSL Certificate error"**:
   ```bash
   # Cài đặt certificate
   mitmproxy --set confdir=~/.mitmproxy
   ```

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra Python version >= 3.6
2. Đảm bảo đã cài đặt đầy đủ dependencies
3. Kiểm tra proxy settings
4. Xem logs trong terminal để debug

---

**TopHeroes API Catcher** - Công cụ mạnh mẽ để phân tích và tự động hóa game TopHeroes! 🎮
