# [file name]: actions_manager.py
# [file content begin]
import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple, Union

@dataclass
class GameAction:
    action_type: str  # "coordinate" or "image"
    # For coordinate actions
    x: Optional[int] = None
    y: Optional[int] = None
    # For image actions
    image_path: Optional[str] = None
    region: Optional[Tuple[int, int, int, int]] = None
    # Common properties
    click_type: str = "left"
    repeat: int = 1
    delay: float = 1.0
    move_back: bool = False

class ActionsManager:
    def __init__(self):
        self.actions: List[GameAction] = []
    
    def add_action(self, action: GameAction):
        self.actions.append(action)
    
    def remove_action(self, index: int):
        if 0 <= index < len(self.actions):
            self.actions.pop(index)
    
    def clear_actions(self):
        self.actions.clear()
    
    def save_to_file(self, file_path: str):
        data = {
            "actions": [asdict(action) for action in self.actions]
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.actions.clear()
            
            # Xử lý cả hai định dạng: object có key "actions" hoặc mảng trực tiếp
            if isinstance(data, dict) and "actions" in data:
                # Định dạng mới: {"actions": [...]}
                actions_data = data["actions"]
            elif isinstance(data, list):
                # Định dạng cũ: [...]
                actions_data = data
            else:
                raise ValueError("Định dạng file không hợp lệ")
            
            for action_data in actions_data:
                # Xử lý region nếu là tuple string
                region = action_data.get("region")
                if region and isinstance(region, str):
                    try:
                        region = tuple(map(int, region.strip("()").split(",")))
                        action_data["region"] = region
                    except:
                        action_data["region"] = None
                
                # Đảm bảo tương thích với định dạng cũ
                if "x" in action_data and "y" in action_data:
                    # Định dạng tọa độ
                    action = GameAction(
                        action_type="coordinate",
                        x=action_data["x"],
                        y=action_data["y"],
                        click_type=action_data.get("click_type", "left"),
                        repeat=action_data.get("repeat", 1),
                        delay=action_data.get("delay", 1.0),
                        move_back=action_data.get("move_back", False)
                    )
                elif "image_path" in action_data:
                    # Định dạng ảnh
                    action = GameAction(
                        action_type="image",
                        image_path=action_data["image_path"],
                        region=action_data.get("region"),
                        click_type=action_data.get("click_type", "left"),
                        repeat=action_data.get("repeat", 1),
                        delay=action_data.get("delay", 1.0),
                        move_back=action_data.get("move_back", False)
                    )
                else:
                    # Định dạng mới với action_type
                    action = GameAction(**action_data)
                
                self.actions.append(action)
                
        except Exception as e:
            print(f"Lỗi khi tải file: {str(e)}")
            raise
# [file content end]