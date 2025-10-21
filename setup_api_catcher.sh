#!/bin/bash
# TopHeroes API Catcher Setup Script

echo "🎮 TopHeroes API Catcher Setup"
echo "=============================="

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.6+"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Cài đặt mitmproxy
echo "📦 Installing mitmproxy..."
pip3 install mitmproxy

# Cài đặt requests
echo "📦 Installing requests..."
pip3 install requests

# Tạo thư mục logs
mkdir -p logs
echo "📁 Created logs directory"

# Tạo file cấu hình
cat > config.json << EOF
{
    "proxy_port": 8080,
    "topheroes_keywords": [
        "topheroes", "topwar", "topwarapp", "game", "api",
        "login", "user", "player", "battle", "mission",
        "quest", "reward", "item", "shop", "guild"
    ],
    "save_format": "json",
    "auto_save": true,
    "save_interval": 300
}
EOF

echo "⚙️  Created config.json"

# Tạo script chạy
cat > run_catcher.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting TopHeroes API Catcher..."
echo "📱 Configure your device to use proxy: 127.0.0.1:8080"
echo "🎮 Start TopHeroes game and perform actions"
echo "⏹️  Press Ctrl+C to stop"

mitmdump -s mitmproxy_catcher.py -p 8080
EOF

chmod +x run_catcher.sh
echo "✅ Created run_catcher.sh"

# Tạo script cấu hình proxy
cat > setup_proxy.sh << 'EOF'
#!/bin/bash
echo "🔧 Setting up system proxy..."

# macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detected macOS"
    echo "Please manually configure proxy in System Preferences:"
    echo "1. System Preferences → Network"
    echo "2. Select WiFi → Advanced → Proxies"
    echo "3. Check 'Web Proxy (HTTP)' and 'Secure Web Proxy (HTTPS)'"
    echo "4. Server: 127.0.0.1, Port: 8080"
    echo "5. Click OK and Apply"
fi

# Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detected Linux"
    echo "Please configure proxy in your network settings"
fi

# Windows
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    echo "🪟 Detected Windows"
    echo "Please configure proxy in Windows Settings"
fi
EOF

chmod +x setup_proxy.sh
echo "✅ Created setup_proxy.sh"

echo ""
echo "🎉 Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Run: ./setup_proxy.sh (to configure system proxy)"
echo "2. Run: ./run_catcher.sh (to start API catcher)"
echo "3. Start TopHeroes game and perform actions"
echo "4. Check logs/ directory for captured API calls"
echo ""
echo "📚 For mobile devices:"
echo "   Configure WiFi proxy to: 127.0.0.1:8080"
echo ""
echo "🔍 Captured data will be saved as:"
echo "   - topheroes_api_calls_YYYYMMDD_HHMMSS.json"
echo "   - topheroes_api_calls_YYYYMMDD_HHMMSS_summary.txt"
