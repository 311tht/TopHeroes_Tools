import pyautogui
import random
import time

class CoordinateClicker:
    def __init__(self):
        self.delay = 1.0  # Mặc định 1 giây
    
    def set_delay(self, delay):
        self.delay = delay
    
    def click(self, x, y, click_type="Click Trái", repeat=1, move_back=False):
        original_pos = pyautogui.position()
        
        for _ in range(repeat):
            # Thêm ngẫu nhiên nhỏ để tránh bị phát hiện
            target_x = x + random.randint(-2, 2)
            target_y = y + random.randint(-2, 2)
            
            pyautogui.moveTo(target_x, target_y, duration=0.1)
            
            if click_type == "Click Trái":
                pyautogui.click()
            elif click_type == "Click Phải":
                pyautogui.rightClick()
            elif click_type == "Double Click":
                pyautogui.doubleClick()
            
            time.sleep(self.delay)  # Sử dụng delay trực tiếp
        
        if move_back:
            pyautogui.moveTo(original_pos, duration=0.1)