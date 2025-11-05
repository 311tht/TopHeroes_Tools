from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt

class OverlayWindow(QWidget):
    def closeEvent(self, event):
        parent = self.parent()
        if parent and hasattr(parent, 'check_coord_btn'):
            parent.check_coord_btn.setText("Kiểm tra toạ độ")
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def __init__(self, points, parent=None):
        super().__init__(parent)
        self.points = points  # List of (x, y, index)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        screen = self.screen().geometry() if hasattr(self, 'screen') else self.primaryScreen().geometry()
        self.setGeometry(screen)
        self.close_btn = QPushButton('Đóng kiểm tra', self)
        self.close_btn.setStyleSheet('background-color: #F44336; color: white; font-size: 16px; padding: 8px; border-radius: 8px;')
        self.close_btn.move(30, 30)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setFocusPolicy(Qt.StrongFocus)
        self.close_btn.raise_()
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        painter.setFont(font)
        for x, y, idx in self.points:
            painter.setBrush(QColor(255, 215, 0, 180))
            painter.setPen(QColor(255, 140, 0))
            painter.drawEllipse(x-20, y-20, 40, 40)
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(x-10, y+10, str(idx+1))
        painter.end()
