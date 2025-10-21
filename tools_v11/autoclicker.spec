# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# Kiểm tra xem icon có tồn tại không
icon_path = 'assets/icon.png'
if not os.path.exists(icon_path):
    icon_path = None
    print("Warning: Icon not found, building without icon")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('actions_manager.py', '.'),
        ('image_click.py', '.'),
        ('coordinate_click.py', '.'),
        ('styles.py', '.')
    ],
    hiddenimports=['PyQt5', 'pyautogui', 'cv2', 'numpy', 'PIL'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AutoClickerPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,  # Sử dụng icon_path đã kiểm tra
)

app = BUNDLE(
    exe,
    name='AutoClickerPro.app',
    icon=icon_path,  # Sử dụng icon_path đã kiểm tra
    bundle_identifier='com.autoclicker.pro',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'NSAppleScriptEnabled': 'False',
        'LSUIElement': 'False',
    },
)