import json
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path

@dataclass
class GameAction:
    action_type: str  # "coordinate" hoặc "image"
    x: str            # Tọa độ X hoặc đường dẫn ảnh
    y: str            # Tọa độ Y hoặc khu vực tìm kiếm
    click_type: str
    repeat: int
    delay: float
    move_back: bool
    comment: str = ""

class ActionsManager:
    def exit(self):
        """
        Thoát chương trình.
        """
        import sys
        print("Đã thoát chương trình.")
        sys.exit(0)
    def __init__(self):
        self.actions: List[GameAction] = []
    
    def add_action(self, action: GameAction):
        self.actions.append(action)
    
    def remove_action(self, index: int):
        if 0 <= index < len(self.actions):
            self.actions.pop(index)
    
    def clear_actions(self):
        self.actions = []
    
    def save_to_file(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump([a.__dict__ for a in self.actions], f, indent=2)
    
    def load_from_file(self, filepath: str):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.actions = [GameAction(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.actions = []
    
    def remove_action(self, index: int):
        """Xóa hàng tại vị trí index"""
        if 0 <= index < len(self.actions):
            self.actions.pop(index)
    
    def import_images(self, image_paths: List[str]):
        """
        Thêm nhiều đường dẫn ảnh vào danh sách actions dưới dạng action_type 'image'.
        """
        for image_path in image_paths:
            action = GameAction(
                action_type='image',
                x=image_path,
                y='',
                click_type='',
                repeat=1,
                delay=0.0,
                move_back=False,
                comment='Import ảnh cần tìm kiếm.'
            )
            self.add_action(action)