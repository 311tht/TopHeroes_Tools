# TopHeroes Email Verifier - Hướng dẫn sử dụng

## 🎯 Mục đích
Ứng dụng giúp tự động kiểm tra và lấy mã xác minh từ email Gmail cho game TopHeroes.

## 🚀 Cách sử dụng

### 1. Chuẩn bị tài khoản Gmail
- **Bật 2-Factor Authentication** cho tài khoản Gmail
- **Tạo App Password**:
  - Vào Google Account Settings
  - Security → 2-Step Verification → App passwords
  - Tạo password mới cho "Mail"
  - Lưu lại password này (16 ký tự)

### 2. Chạy ứng dụng
```bash
python email_verifier.py
```

### 3. Thêm tài khoản
1. Nhấn **"Thêm tài khoản"**
2. Nhập **Email Gmail** (ví dụ: yourname@gmail.com)
3. Nhập **App Password** (16 ký tự từ bước 1)
4. Nhấn **"Đăng nhập"**

### 4. Kiểm tra mã xác minh
- **Kiểm tra tài khoản đã chọn**: Chọn tài khoản từ dropdown, nhấn "Kiểm tra tài khoản đã chọn"
- **Kiểm tra tất cả tài khoản**: Nhấn "Kiểm tra tất cả tài khoản"

### 5. Copy mã
- Nhấn **"Copy mã mới nhất"** để copy mã xác minh vào clipboard
- Mã sẽ được tự động tìm và copy

## ✨ Tính năng

### 🔍 Tìm kiếm thông minh
- Tìm email từ các nguồn phổ biến: `noreply@topheroes.com`, `support@topheroes.com`
- Tìm theo từ khóa: "verification", "xác minh", "code", "mã"
- Kiểm tra email trong 24h gần nhất

### 📧 Trích xuất mã
- Tự động tìm mã 4-8 chữ số
- Hỗ trợ nhiều format: "verification code: 123456", "mã xác minh: 123456"
- Ưu tiên email mới nhất

### 🎨 Giao diện thân thiện
- Quản lý nhiều tài khoản
- Hiển thị kết quả chi tiết với emoji
- Copy mã nhanh chóng
- Thông báo lỗi rõ ràng

## ⚠️ Lưu ý quan trọng

### Bảo mật
- **App Password** được lưu trong file `accounts.json` ở thư mục Documents/TopHeroes
- Không chia sẻ file này với người khác
- Xóa tài khoản nếu không sử dụng

### Lỗi thường gặp
1. **"Lỗi kết nối Gmail"**: Kiểm tra App Password
2. **"Không tìm thấy email xác minh"**: 
   - Kiểm tra email có trong INBOX không
   - Thử kiểm tra trong 24h gần nhất
3. **"Không tìm thấy mã xác minh"**: Email có thể không chứa mã số

### Tối ưu hóa
- Chỉ kiểm tra 5 email mới nhất để tăng tốc
- Tự động đóng kết nối sau mỗi lần kiểm tra
- Hiển thị tiến trình rõ ràng

## 🛠️ Cấu trúc file
```
send_gmail/
├── email_verifier.py          # File chính
├── requirements.txt           # Danh sách thư viện
├── HUONG_DAN_SU_DUNG.md      # Hướng dẫn này
├── accounts.json             # Lưu tài khoản (tự tạo)
└── build/                    # File build (nếu có)
```

## 📞 Hỗ trợ
Nếu gặp vấn đề, kiểm tra:
1. Python version >= 3.6
2. Gmail đã bật 2FA
3. App Password đúng
4. Kết nối internet ổn định

---
**TopHeroes Email Verifier v1.0** - Tự động hóa việc lấy mã xác minh!

