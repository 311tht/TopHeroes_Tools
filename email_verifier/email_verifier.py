import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import imaplib
import email
import re
import time
from datetime import datetime, timedelta
import sys

class GmailChecker:
    def __init__(self, email_addr, app_password):
        # LÀM SẠCH dữ liệu ngay từ đầu
        self.email_addr = self.clean_string(email_addr)
        self.app_password = self.clean_string(app_password)
        self.mail = None
    
    def clean_string(self, text):
        """Loại bỏ hoàn toàn ký tự không phải ASCII"""
        if isinstance(text, str):
            # Giữ chỉ các ký tự ASCII in được (32-126)
            return ''.join(char for char in text if 32 <= ord(char) <= 126)
        return str(text)
        
    def connect(self):
        """Kết nối đến Gmail IMAP"""
        try:
            self.mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
            print(f"🔐 Đang kết nối với: {self.email_addr}")
            self.mail.login(self.email_addr, self.app_password)
            print("✅ Kết nối thành công")
            return True
        except Exception as e:
            print(f"❌ Lỗi kết nối: {str(e)}")
            raise Exception(f"Lỗi kết nối Gmail: {str(e)}")
    
    def disconnect(self):
        """Đóng kết nối"""
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
            except:
                pass
            self.mail = None
    
    def search_unread_topheroes_emails(self, minutes_back=1):
        """Tìm email CHƯA ĐỌC của TopHeroes trong 1 phút gần nhất - SIÊU NHANH"""
        if not self.mail:
            raise Exception("Chưa kết nối đến Gmail")
        
        try:
            self.mail.select('INBOX')
            
            # Tính thời gian 1 phút trước
            since_time = (datetime.now() - timedelta(minutes=minutes_back))
            since_date = since_time.strftime('%d-%b-%Y')
            
            # Tìm email CHƯA ĐỌC từ TopHeroes trong 1 phút gần nhất
            search_query = f'(UNSEEN FROM "service@topheroesmail.topwarapp.com" SINCE "{since_date}")'
            print(f"🔍 Tìm kiếm: {search_query}")
            
            status, messages = self.mail.search(None, search_query)
            
            if status == 'OK' and messages[0]:
                email_ids = messages[0].split()
                print(f"✅ Tìm thấy {len(email_ids)} email chưa đọc")
                return email_ids
            else:
                print("ℹ️ Không tìm thấy email chưa đọc trong 1 phút qua")
                return []
            
        except Exception as e:
            raise Exception(f"Lỗi tìm kiếm email: {str(e)}")
    
    def get_email_content_fast(self, email_id):
        """Lấy nội dung email NHANH"""
        if not self.mail:
            raise Exception("Chưa kết nối đến Gmail")
        
        try:
            status, msg_data = self.mail.fetch(email_id, '(BODY.PEEK[TEXT])')
            if status != 'OK':
                return None
                
            if msg_data and msg_data[0]:
                raw_content = msg_data[0][1]
                if raw_content:
                    try:
                        body = raw_content.decode('utf-8', errors='ignore')
                        # Làm sạch body
                        body = self.clean_string(body)
                        return {'body': body}
                    except:
                        body = str(raw_content)
                        body = self.clean_string(body)
                        return {'body': body}
            
            return None
            
        except Exception as e:
            print(f"⚠️ Lỗi đọc email {email_id}: {e}")
            return None
    
    def extract_verification_code_fast(self, body):
        """Trích xuất mã xác minh NHANH"""
        if not body:
            return None
        
        patterns = [
            r'\b(\d{6})\b',
            r'code[\s:]*(\d{6})',
            r'mã[\s:]*(\d{6})',
            r'verification code[\s:]*(\d{6})',
            r'xác minh[\s:]*(\d{6})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def get_latest_verification_code_super_fast(self):
        """Lấy mã xác minh mới nhất - SIÊU TỐC (chỉ 1 phút, chưa đọc)"""
        try:
            self.connect()
            
            # CHỈ tìm email CHƯA ĐỌC trong 1 PHÚT gần nhất
            email_ids = self.search_unread_topheroes_emails(1)
            
            if not email_ids:
                return None, "Không tìm thấy email chưa đọc trong 1 phút qua"
            
            # Sắp xếp theo thời gian (mới nhất trước)
            email_ids.sort(key=int, reverse=True)
            
            print(f"📧 Kiểm tra {len(email_ids)} email chưa đọc...")
            
            # CHỈ kiểm tra email đầu tiên (mới nhất)
            for email_id in email_ids[:1]:
                email_content = self.get_email_content_fast(email_id)
                if email_content and 'body' in email_content:
                    code = self.extract_verification_code_fast(email_content['body'])
                    if code:
                        # ĐÁNH DẤU ĐÃ ĐỌC email này
                        self.mark_as_read(email_id)
                        return {'code': code}, "Thành công"
            
            return None, "Không tìm thấy mã xác minh trong email chưa đọc"
            
        except Exception as e:
            return None, f"Lỗi: {str(e)}"
        finally:
            self.disconnect()
    
    def mark_as_read(self, email_id):
        """Đánh dấu email đã đọc"""
        try:
            self.mail.store(email_id, '+FLAGS', '\\Seen')
            print(f"📭 Đã đánh dấu email {email_id} là đã đọc")
        except Exception as e:
            print(f"⚠️ Không thể đánh dấu đã đọc: {e}")

class GmailVerifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TopHeroes Email Verifier - Multi Account")

        # Đường dẫn lưu dữ liệu
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        app_support_dir = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "TopHeroesEmailVerifier")
        os.makedirs(app_support_dir, exist_ok=True)
        
        self.accounts_file = os.path.join(app_support_dir, "accounts.json")
        
        # Copy file cũ nếu có
        old_accounts_file = os.path.join(base_path, "accounts.json")
        if os.path.exists(old_accounts_file) and not os.path.exists(self.accounts_file):
            try:
                import shutil
                shutil.copy2(old_accounts_file, self.accounts_file)
                print(f"✅ Đã copy file accounts.json")
            except Exception as e:
                print(f"❌ Không thể copy file cũ: {e}")

        self.accounts = self.load_accounts()
        self.current_account = None

        self.create_widgets()
        print(f"📁 File accounts: {self.accounts_file}")

    def clean_string(self, text):
        """Loại bỏ hoàn toàn ký tự không phải ASCII"""
        if isinstance(text, str):
            return ''.join(char for char in text if 32 <= ord(char) <= 126)
        return str(text)

    def load_accounts(self):
        """Tải dữ liệu tài khoản - LÀM SẠCH DỮ LIỆU"""
        try:
            if os.path.exists(self.accounts_file):
                with open(self.accounts_file, "r", encoding='utf-8') as f:
                    accounts_data = json.load(f)
                    
                # LÀM SẠCH toàn bộ dữ liệu
                cleaned_accounts = {}
                for email, info in accounts_data.items():
                    if isinstance(info, dict) and 'password' in info:
                        cleaned_email = self.clean_string(email)
                        cleaned_password = self.clean_string(info['password'])
                        
                        if cleaned_email and cleaned_password:
                            cleaned_accounts[cleaned_email] = {"password": cleaned_password}
                            print(f"✅ Đã làm sạch: {cleaned_email}")
                        else:
                            print(f"⚠️ Bỏ qua: {email} (dữ liệu không hợp lệ sau khi làm sạch)")
                
                print(f"📊 Tổng số tài khoản hợp lệ: {len(cleaned_accounts)}")
                return cleaned_accounts
            return {}
        except Exception as e:
            print(f"❌ Lỗi tải accounts: {e}")
            return {}

    def save_accounts(self):
        """Lưu dữ liệu tài khoản - CHỈ LƯU DỮ LIỆU ĐÃ LÀM SẠCH"""
        try:
            # Đảm bảo chỉ lưu dữ liệu đã làm sạch
            cleaned_accounts = {}
            for email, info in self.accounts.items():
                cleaned_email = self.clean_string(email)
                cleaned_password = self.clean_string(info.get('password', ''))
                
                if cleaned_email and cleaned_password and len(cleaned_password) >= 16:
                    cleaned_accounts[cleaned_email] = {"password": cleaned_password}
            
            with open(self.accounts_file, "w", encoding='utf-8') as f:
                json.dump(cleaned_accounts, f, indent=4, ensure_ascii=False)
            
            print(f"💾 Đã lưu {len(cleaned_accounts)} tài khoản đã làm sạch")
        except Exception as e:
            print(f"❌ Lỗi lưu accounts: {e}")

    def delete_account(self):
        acc = self.account_var.get()
        if acc in self.accounts:
            confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xoá tài khoản {acc}?")
            if confirm:
                del self.accounts[acc]
                self.save_accounts()
                self.update_account_combo()
                messagebox.showinfo("Xong", f"Đã xoá tài khoản {acc}")

    # ================== UI - GIỮ NGUYÊN GIAO DIỆN GỐC ==================
    def create_widgets(self):
        # --- Quản lý tài khoản ---
        account_frame = tk.LabelFrame(self.root, text="Quản lý tài khoản", bg="#f9f9f9", fg="black", padx=5, pady=5)
        account_frame.pack(fill=tk.X, padx=5, pady=2)

        # Dòng 1: Chọn tài khoản
        select_frame = tk.Frame(account_frame, bg="#f9f9f9")
        select_frame.pack(fill=tk.X, pady=2)

        tk.Label(select_frame, text="Tài khoản:", bg="#f9f9f9", fg="black").pack(side=tk.LEFT, padx=2)

        self.account_var = tk.StringVar()
        self.account_combo = ttk.Combobox(select_frame, textvariable=self.account_var, state="readonly", width=25)
        self.account_combo.pack(side=tk.LEFT, padx=2)

        # Dòng 2: Các nút chức năng - CĂN GIỮA
        btn_frame = tk.Frame(account_frame, bg="#f9f9f9")
        btn_frame.pack(fill=tk.X, pady=5)

        # Frame con để căn giữa các nút
        center_btn_frame = tk.Frame(btn_frame, bg="#f9f9f9")
        center_btn_frame.pack(expand=True)  # Căn giữa

        add_account_btn = tk.Button(center_btn_frame, text="Thêm tài khoản", command=self.show_login_frame, width=15)
        add_account_btn.pack(side=tk.LEFT, padx=5)

        delete_account_btn = tk.Button(center_btn_frame, text="Xoá tài khoản", command=self.delete_account, fg="red", width=15)
        delete_account_btn.pack(side=tk.LEFT, padx=5)

        # --- Form đăng nhập ---
        self.login_container = tk.LabelFrame(self.root, text="Thêm tài khoản mới", bg="#f9f9f9", fg="black", padx=15, pady=15)

        # Form nhập liệu
        form_frame = tk.Frame(self.login_container, bg="#f9f9f9")
        form_frame.pack(fill=tk.X, pady=5)

        # Email
        tk.Label(form_frame, text="Email:", bg="#f9f9f9", fg="black", width=10, anchor="w").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.email_entry = tk.Entry(form_frame, width=35, fg="black", bg="white", insertbackground="black")
        self.email_entry.grid(row=0, column=1, pady=5, padx=5, sticky="we")

        # Password
        tk.Label(form_frame, text="Mật khẩu APP:", bg="#f9f9f9", fg="black", width=10, anchor="w").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.password_entry = tk.Entry(form_frame, show="*", width=35, fg="black", bg="white", insertbackground="black")
        self.password_entry.grid(row=1, column=1, pady=5, padx=5, sticky="we")

        # Checkbox hiện mật khẩu
        self.show_pw_var = tk.IntVar()
        self.show_pw_check = tk.Checkbutton(form_frame, text="Hiện mật khẩu", variable=self.show_pw_var, 
                                           command=self.toggle_password, bg="#f9f9f9", fg="black")
        self.show_pw_check.grid(row=2, column=1, sticky="w", pady=5, padx=5)

        # Nút đăng nhập + hủy - CĂN GIỮA
        button_frame = tk.Frame(self.login_container, bg="#f9f9f9")
        button_frame.pack(fill=tk.X, pady=10)

        # Frame con để căn giữa các nút
        center_button_frame = tk.Frame(button_frame, bg="#f9f9f9")
        center_button_frame.pack(expand=True)  # Căn giữa

        self.login_btn = tk.Button(center_button_frame, text="Đăng nhập", command=self.login_gmail, 
                                  width=12, font=("Arial", 10, "bold"), relief="raised", bd=2)
        self.login_btn.pack(side=tk.LEFT, padx=8)

        self.cancel_btn = tk.Button(center_button_frame, text="Hủy", command=self.hide_login_frame, 
                                   width=12, font=("Arial", 10, "bold"), relief="raised", bd=2)
        self.cancel_btn.pack(side=tk.LEFT, padx=8)

        # Cấu hình grid weights
        form_frame.columnconfigure(1, weight=1)

        # --- Kiểm tra mã ---
        verify_frame = tk.LabelFrame(self.root, text="Kiểm tra mã xác minh", bg="#f9f9f9", fg="black", padx=5, pady=5)
        verify_frame.pack(fill=tk.X, padx=5, pady=5)

        self.status_label = tk.Label(verify_frame, text="Chưa chọn tài khoản", fg="blue", bg="#f9f9f9", font=("Arial", 9))
        self.status_label.pack(pady=3)

        btns_frame = tk.Frame(verify_frame, bg="#f9f9f9")
        btns_frame.pack(pady=5)

        # Căn giữa các nút kiểm tra
        center_verify_frame = tk.Frame(btns_frame, bg="#f9f9f9")
        center_verify_frame.pack(expand=True)

        # NÚT GỐC - KHÔNG THAY ĐỔI MÀU SẮC HAY FONT
        tk.Button(center_verify_frame, text="Kiểm tra tài khoản đã chọn", 
                 command=self.check_selected_account_fast, width=25).pack()

        # --- Kết quả ---
        result_frame = tk.LabelFrame(self.root, text="Kết quả", bg="#f9f9f9", fg="black", padx=5, pady=5)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame chứa text và scrollbar
        text_frame = tk.Frame(result_frame, bg="#f9f9f9")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.result_text = tk.Text(text_frame, height=12, bg="white", fg="black", 
                                  insertbackground="black", font=("Arial", 12))
        
        scrollbar = tk.Scrollbar(text_frame, command=self.result_text.yview)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Các nút hành động - CĂN GIỮA
        action_frame = tk.Frame(result_frame, bg="#f9f9f9")
        action_frame.pack(fill=tk.X, pady=8)

        center_action_frame = tk.Frame(action_frame, bg="#f9f9f9")
        center_action_frame.pack(expand=True)

        self.copy_btn = tk.Button(center_action_frame, text="Copy mã mới nhất", command=self.copy_latest_code, 
                                 state=tk.DISABLED, width=15)
        self.copy_btn.pack(side=tk.LEFT, padx=6)

        tk.Button(center_action_frame, text="Xoá kết quả", command=self.clear_results, width=12).pack(side=tk.LEFT, padx=6)
        tk.Button(center_action_frame, text="Thoát", command=self.root.quit, width=10).pack(side=tk.LEFT, padx=6)

        # Cập nhật dropdown sau khi tất cả widgets được tạo
        self.update_account_combo()

    # ================== Login form helpers ==================
    def show_login_frame(self):
        """Chỉ hiện form khi nhấn nút Thêm tài khoản"""
        self.clear_login_form()
        self.login_container.pack(fill=tk.X, padx=5, pady=5, ipady=10)
        self.email_entry.focus_set()
        
        self.root.update_idletasks()
        self.root.geometry("800x700")

    def hide_login_frame(self):
        """Ẩn form đăng nhập"""
        self.login_container.pack_forget()
        self.clear_login_form()

    def toggle_password(self):
        if self.show_pw_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def clear_login_form(self):
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.show_pw_var.set(0)
        self.password_entry.config(show="*")

    def update_account_combo(self):
        self.account_combo["values"] = list(self.accounts.keys())
        if self.accounts:
            first = list(self.accounts.keys())[0]
            self.account_var.set(first)
            self.current_account = first
            self.status_label.config(text=f"Đã chọn: {first}", fg="green")
        else:
            self.account_var.set("")
            self.current_account = None
            self.status_label.config(text="Chưa có tài khoản nào", fg="red")

    # ================== Gmail login & check ==================
    def login_gmail(self):
        email_addr = self.email_entry.get().strip()
        app_pw = self.password_entry.get().strip()
        
        if not email_addr or not app_pw:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ Gmail và App Password")
            return

        # LÀM SẠCH dữ liệu trước khi sử dụng
        cleaned_email = self.clean_string(email_addr)
        cleaned_password = self.clean_string(app_pw)

        try:
            checker = GmailChecker(cleaned_email, cleaned_password)
            checker.connect()
            checker.disconnect()
            
            # Lưu dữ liệu đã làm sạch
            self.accounts[cleaned_email] = {"password": cleaned_password}
            self.save_accounts()
            self.update_account_combo()
            self.hide_login_frame()
            messagebox.showinfo("Thành công", f"Đã lưu tài khoản {cleaned_email}")
            
        except Exception as e:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối đến Gmail: {str(e)}")

    def check_selected_account_fast(self):
        """Kiểm tra SIÊU TỐC - chỉ mail chưa đọc trong 1 phút"""
        acc = self.account_var.get()
        if not acc:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một tài khoản")
            return
        
        if acc not in self.accounts:
            messagebox.showerror("Lỗi", f"Không tìm thấy thông tin tài khoản {acc}")
            return
            
        account_info = self.accounts[acc]
        app_password = account_info.get('password', '')
        
        if not app_password:
            messagebox.showwarning("Thiếu mật khẩu", f"Tài khoản {acc} chưa có mật khẩu App Password.")
            return
            
        self.status_label.config(text=f"Đang kiểm tra: {acc}", fg="orange")
        self.root.update()
        
        try:
            # Sử dụng phiên bản SIÊU TỐC
            checker = GmailChecker(acc, app_password)
            result, message = checker.get_latest_verification_code_super_fast()
            
            if result:
                self.append_result(f"✅ {acc} - Thành công!")
                self.append_result(f"🔐 Mã xác minh: {result['code']}")
            else:
                self.append_result(f"❌ {acc}: {message}")
                
        except Exception as e:
            self.append_result(f"❌ {acc}: {str(e)}")
        
        self.status_label.config(text=f"Hoàn thành: {acc}", fg="green")

    # ================== Results ==================
    def append_result(self, text):
        self.result_text.insert(tk.END, text + "\n")
        self.result_text.see(tk.END)
        self.copy_btn.config(state=tk.NORMAL)

    def copy_latest_code(self):
        content = self.result_text.get(1.0, tk.END).strip()
        if content:
            lines = content.split('\n')
            
            for line in reversed(lines):
                if "Mã xác minh:" in line:
                    match = re.search(r'(\d{4,8})', line)
                    if match:
                        code = match.group(1)
                        self.root.clipboard_clear()
                        self.root.clipboard_append(code)
                        messagebox.showinfo("Copy thành công", f"✅ Đã copy mã: {code}")
                        return

    def clear_results(self):
        self.result_text.delete(1.0, tk.END)
        self.copy_btn.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    root.geometry("800x700")
    root.minsize(750, 650)
    root.resizable(True, True)
    
    print("🚀 Khởi động TopHeroes Email Verifier...")
    
    app = GmailVerifierApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()