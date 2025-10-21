# Game Automation Tools Collection

Bộ sưu tập các công cụ tự động hóa game được phát triển bằng Python, bao gồm Auto Clicker và Email Verifier cho game TopHeroes.

## 📁 Cấu trúc dự án

```
Game_code/
├── auto_clieck_v1/          # Auto Clicker phiên bản đầu tiên
├── tools_login/             # Auto Clicker với tính năng đăng nhập tự động
├── tools_nv_hoi/            # Auto Clicker cho nhiệm vụ hội
├── tools_v11/               # Auto Clicker phiên bản 11
├── tools_v12/               # Auto Clicker phiên bản 12 (mới nhất)
└── send_gmail/              # Email Verifier cho TopHeroes
```

## 🎮 Auto Clicker Tools

### Tính năng chính
- **Click theo tọa độ**: Tự động click tại các vị trí cụ thể trên màn hình
- **Click theo hình ảnh**: Tìm và click vào các hình ảnh mẫu
- **Tự động nhập text**: Nhập văn bản tự động
- **Lặp lại hành động**: Thực hiện chuỗi hành động nhiều lần
- **Lưu/tải kịch bản**: Lưu trữ và tải lại các kịch bản đã tạo
- **Overlay hiển thị**: Hiển thị các điểm click trên màn hình

### Phiên bản hiện tại
- **tools_v12**: Phiên bản mới nhất với đầy đủ tính năng
- **tools_nv_hoi**: Chuyên dụng cho nhiệm vụ hội
- **tools_login**: Có tính năng đăng nhập tự động

### Cách sử dụng
1. Chạy file `main.py` trong thư mục tương ứng
2. Thiết lập các hành động click theo tọa độ hoặc hình ảnh
3. Cấu hình số lần lặp và delay
4. Nhấn "Bắt đầu" để thực thi

## 📧 Email Verifier (TopHeroes)

### Mục đích
Tự động kiểm tra và lấy mã xác minh từ email Gmail cho game TopHeroes.

### Tính năng
- **Quản lý nhiều tài khoản**: Lưu trữ và quản lý nhiều tài khoản Gmail
- **Tìm kiếm thông minh**: Tự động tìm email xác minh từ TopHeroes
- **Trích xuất mã**: Tự động tìm và trích xuất mã xác minh
- **Copy nhanh**: Copy mã vào clipboard chỉ với một click
- **Giao diện thân thiện**: Dễ sử dụng với giao diện trực quan

### Cách sử dụng
1. **Chuẩn bị tài khoản Gmail**:
   - Bật 2-Factor Authentication
   - Tạo App Password (16 ký tự)
   
2. **Chạy ứng dụng**:
   ```bash
   cd send_gmail
   python email_verifier.py
   ```

3. **Thêm tài khoản**:
   - Nhấn "Thêm tài khoản"
   - Nhập email và App Password
   - Nhấn "Đăng nhập"

4. **Kiểm tra mã**:
   - Chọn tài khoản từ dropdown
   - Nhấn "Kiểm tra tài khoản đã chọn"
   - Nhấn "Copy mã mới nhất" để copy mã

## 🛠️ Yêu cầu hệ thống

### Auto Clicker
- Python 3.6+
- PyQt5
- pyautogui
- opencv-python (cho tính năng click theo hình ảnh)

### Email Verifier
- Python 3.6+
- Chỉ sử dụng thư viện chuẩn của Python (không cần cài đặt thêm)

## 📦 Cài đặt

### Auto Clicker
```bash
pip install PyQt5 pyautogui opencv-python
```

### Email Verifier
Không cần cài đặt thêm thư viện nào, chỉ cần Python chuẩn.

## ⚠️ Lưu ý quan trọng

### Bảo mật
- **App Password** được lưu trong file `accounts.json`
- Không chia sẻ file này với người khác
- Xóa tài khoản nếu không sử dụng

### Sử dụng có trách nhiệm
- Chỉ sử dụng cho mục đích cá nhân
- Tuân thủ Terms of Service của game
- Không sử dụng để gian lận hoặc làm hại người khác

## 🐛 Xử lý lỗi thường gặp

### Auto Clicker
1. **Lỗi import PyQt5**: Cài đặt lại PyQt5
2. **Không click được**: Kiểm tra quyền truy cập accessibility
3. **Không tìm thấy hình ảnh**: Kiểm tra đường dẫn file hình ảnh

### Email Verifier
1. **"Lỗi kết nối Gmail"**: Kiểm tra App Password
2. **"Không tìm thấy email"**: Kiểm tra email có trong INBOX không
3. **"Không tìm thấy mã"**: Email có thể không chứa mã số

## 📞 Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. Python version >= 3.6
2. Đã cài đặt đầy đủ thư viện
3. Quyền truy cập hệ thống (cho Auto Clicker)
4. Cấu hình Gmail đúng (cho Email Verifier)

## 📝 License

Dự án này được phát triển cho mục đích học tập và sử dụng cá nhân. Vui lòng sử dụng có trách nhiệm.

---

**Game Automation Tools Collection** - Tự động hóa các tác vụ game một cách thông minh và hiệu quả!
