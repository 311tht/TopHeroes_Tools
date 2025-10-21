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
                for action in self.actions:
                    if not self.running:
                        break
                    if action.action_type == "coordinate":
                        self.parent.execute_coordinate_action(action)

                if _ < self.total_loops - 1 and self.loop_delay > 0:
                    self.msleep(int(self.loop_delay * 1000))
        finally:
            self.finished.emit()
            if not self.running:
                self.stopped.emit()
