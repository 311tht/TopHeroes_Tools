from PyQt5.QtCore import QThread, pyqtSignal

class Worker(QThread):
    finished = pyqtSignal()
    stopped = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.actions = []
        self.total_loops = 1
        self.loop_delay = 0
        self.running = True
        self.parent = parent

    def run(self):
        try:
            for _ in range(self.total_loops):
                if not self.running:
                    break
                # Gom tất cả action image lại
                image_actions = [a for a in self.actions if a.action_type == "image" and getattr(a, 'enabled', True)]
                coord_actions = [a for a in self.actions if a.action_type == "coordinate"]
                # Thực hiện các hành động toạ độ như cũ
                for action in coord_actions:
                    if not self.running:
                        break
                    self.parent.execute_coordinate_action(action)
                # Nếu có nhiều ảnh, tìm tất cả cùng lúc
                if image_actions:
                    found = False
                    for action in image_actions:
                        if not self.running:
                            break
                        result = self.parent.image_clicker.find_image(action.x)
                        if result:
                            self.parent.execute_image_action(action)
                            found = True
                            break
                    if found:
                        break
                if _ < self.total_loops - 1 and self.loop_delay > 0:
                    self.msleep(int(self.loop_delay * 1000))
        finally:
            self.finished.emit()
            if not self.running:
                self.stopped.emit()
