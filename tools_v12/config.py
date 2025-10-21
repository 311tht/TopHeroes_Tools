from pathlib import Path

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"

# Các giá trị mặc định
DEFAULT_DELAY = 1.0  # Đổi thành giây
DEFAULT_REPEAT = 1
CLICK_TYPES = ["Click Trái", "Click Phải", "Double Click"]
SEARCH_REGIONS = ["Toàn màn hình", "Nửa trái", "Nửa phải", "Tùy chỉnh"]