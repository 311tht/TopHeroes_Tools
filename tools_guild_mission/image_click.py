import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab

class ImageClicker:
    def __init__(self, confidence=0.7):
        self.confidence = confidence
    
    def find_image(self, template_path, region=None):
        """Tìm ảnh mẫu trên màn hình với xử lý lỗi đầy đủ"""
        try:
            # Chụp màn hình và chuyển đổi định dạng
            if region:
                screen = np.array(ImageGrab.grab(bbox=region))
            else:
                screen = np.array(ImageGrab.grab())
            
            # Chuyển đổi sang định dạng BGR (OpenCV mặc định)
            screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
            
            # Đọc ảnh mẫu và kiểm tra
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                raise ValueError(f"Không thể đọc file ảnh mẫu: {template_path}")
            
            # Kiểm tra kích thước ảnh
            if screen.shape[0] < template.shape[0] or screen.shape[1] < template.shape[1]:
                raise ValueError("Ảnh mẫu lớn hơn ảnh màn hình")
            
            # So khớp template
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= self.confidence:
                h, w = template.shape[:-1]
                if region:
                    center_x = region[0] + max_loc[0] + w // 2
                    center_y = region[1] + max_loc[1] + h // 2
                else:
                    center_x = max_loc[0] + w // 2
                    center_y = max_loc[1] + h // 2
                return (center_x, center_y)
            
            return None
            
        except Exception as e:
            print(f"Lỗi tìm ảnh: {str(e)}")
            return None