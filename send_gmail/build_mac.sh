#!/bin/bash

APP_NAME="TopHeroesEmailVerifier"
PY_FILE="email_verifier.py"
DIST_DIR="dist"

echo "🔄 Xóa build cũ..."
rm -rf build dist __pycache__ *.spec

echo "⚙️ Đang build app với PyInstaller..."
pyinstaller --onefile --windowed --name="$APP_NAME" --clean --strip "$PY_FILE"

echo "📦 Đóng gói thành file .app..."
# Đảm bảo thư mục dist tồn tại
mkdir -p "$DIST_DIR"

echo "🔒 Xóa quarantine attribute để app chạy không bị chặn..."
xattr -cr "dist/${APP_NAME}.app" 2>/dev/null || true

echo "📝 Tạo hướng dẫn cài đặt..."
cat > "dist/INSTALL_INSTRUCTIONS.txt" << EOF
HƯỚNG DẪN CÀI ĐẶT TOPHEROES EMAIL VERIFIER

1. Kéo file ${APP_NAME}.app vào thư mục Applications

2. Nếu macOS chặn ứng dụng:
   - Vào System Preferences → Security & Privacy
   - Nhấp "Open Anyway" bên cạnh ${APP_NAME}
   - Hoặc chạy lệnh terminal:
     sudo xattr -rd com.apple.quarantine /Applications/${APP_NAME}.app

3. Dữ liệu tài khoản được lưu tại:
   ~/Library/Application Support/TopHeroesEmailVerifier/accounts.json

4. Để import tài khoản cũ:
   - Copy file accounts.json vào thư mục trên
   - Hoặc thêm tài khoản thủ công trong app

Ứng dụng đã sẵn sàng sử dụng!
EOF

echo "✅ Build hoàn tất!"
echo "📁 App được tạo tại: dist/${APP_NAME}.app"
echo "📋 Hướng dẫn cài đặt: dist/INSTALL_INSTRUCTIONS.txt"
echo ""
echo "🚀 Để chạy app:"
echo "   open 'dist/${APP_NAME}.app'"