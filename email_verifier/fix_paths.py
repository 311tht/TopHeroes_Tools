#!/usr/bin/env python3
"""
Script để fix đường dẫn cho app MacOS
"""

import os
import json
import shutil
from pathlib import Path

def migrate_old_accounts():
    """Di chuyển dữ liệu tài khoản từ các vị trí cũ"""
    
    # Các vị trí có thể chứa file accounts.json cũ
    possible_locations = [
        Path(".").absolute(),  # Thư mục hiện tại
        Path(__file__).parent.absolute(),  # Thư mục script
        Path.home() / "Documents" / "TopHeroes",  # Vị trí cũ
    ]
    
    # Vị trí mới
    new_location = Path.home() / "Library" / "Application Support" / "TopHeroesEmailVerifier"
    new_location.mkdir(parents=True, exist_ok=True)
    
    new_accounts_file = new_location / "accounts.json"
    
    # Tìm và di chuyển file cũ
    for old_location in possible_locations:
        old_accounts_file = old_location / "accounts.json"
        if old_accounts_file.exists() and not new_accounts_file.exists():
            try:
                shutil.copy2(old_accounts_file, new_accounts_file)
                print(f"✅ Đã di chuyển accounts.json từ: {old_accounts_file}")
                print(f"   đến: {new_accounts_file}")
                return True
            except Exception as e:
                print(f"❌ Lỗi khi di chuyển: {e}")
    
    return False

if __name__ == "__main__":
    print("🔄 Đang tìm và di chuyển dữ liệu tài khoản cũ...")
    if migrate_old_accounts():
        print("✅ Hoàn thành!")
    else:
        print("ℹ️ Không tìm thấy dữ liệu cũ để di chuyển")