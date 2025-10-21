
"""
main.py - Main GUI for Auto Clicker Pro
Author: [tantranhuyen]
Description: PyQt5-based auto clicker with coordinate and image click features.
"""

# Standard library imports
import sys
import random
import time

# Third-party imports
import pyautogui
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QSpinBox,
    QCheckBox, QHBoxLayout, QVBoxLayout, QWidget, QFileDialog,
    QGroupBox, QHeaderView, QMessageBox, QTabWidget, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QTimer, QPoint, QThread, pyqtSignal
from PyQt5.QtGui import QIcon

# Local imports
from overlay_window import OverlayWindow
from worker import Worker
from coordinate_click import CoordinateClicker
from image_click import ImageClicker
from actions_manager import ActionsManager, GameAction
from config import CLICK_TYPES, SEARCH_REGIONS, ASSETS_DIR
from styles import get_stylesheet


# =====================
# Worker Thread
# =====================

# (Worker class is now in worker.py, imported above)

# =====================
# Main GUI Class
# =====================

class AutoClickerGUI(QMainWindow):



    def check_coordinate_highlight(self):
        """Bật/tắt overlay kiểm tra toạ độ, đổi nhãn nút tương ứng"""
        # Nếu overlay đang mở, tắt overlay và đổi lại nhãn nút
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.close()
            self.overlay = None
            self.check_coord_btn.setText("Kiểm tra toạ độ")
            return
        # Nếu chưa mở overlay, hiển thị overlay và đổi nhãn nút
        points = []
        for idx, action in enumerate(self.actions_manager.actions):
            if action.action_type == "coordinate":
                try:
                    x = int(action.x)
                    y = int(action.y)
                    points.append((x, y, idx))
                except Exception:
                    pass
        if not points:
            QMessageBox.information(self, "Thông báo", "Không có hành động toạ độ nào để kiểm tra!")
            return
        self.overlay = OverlayWindow(points, parent=self)
        self.overlay.show()
        self.overlay.activateWindow()
        self.overlay.raise_()
        self.overlay.setFocus()
        self.check_coord_btn.setText("Tắt kiểm tra")


    def close_overlay(self):
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.close()
            self.overlay = None
        self.check_coord_btn.setText("Kiểm tra toạ độ")

    def _highlight_next_coordinate_row(self):
        if self._coord_highlight_step > 0:
            # Reset hàng trước đó
            prev_row = self._coord_highlight_indexes[self._coord_highlight_step-1]
            self.reset_row_highlight(prev_row)
        if self._coord_highlight_step < len(self._coord_highlight_indexes):
            row = self._coord_highlight_indexes[self._coord_highlight_step]
            self.action_table.selectRow(row)
            for col in range(self.action_table.columnCount()):
                item = self.action_table.item(row, col)
                if item:
                    item.setBackground(Qt.yellow)
            self._coord_highlight_step += 1
        else:
            self.action_table.clearSelection()
            self._coord_highlight_timer.stop()

    def reset_row_highlight(self, row):
        for col in range(self.action_table.columnCount()):
            item = self.action_table.item(row, col)
            if item:
                item.setBackground(Qt.white)
    def __init__(self):
        super().__init__()
        # Core logic
        self.coord_clicker = CoordinateClicker()
        self.image_clicker = ImageClicker()
        self.actions_manager = ActionsManager()
        self.worker = Worker(self)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.stopped.connect(self.on_worker_stopped)
        # UI state
        self.is_tracking = False
        self.is_running = False
        # Setup
        self.init_control_buttons()
        self.setup_ui()
        self.setup_events()
    
    def init_control_buttons(self):
        """Khởi tạo tất cả nút điều khiển"""
        self.start_btn = QPushButton("Bắt đầu")
        self.stop_btn = QPushButton("Dừng lại")
        self.clear_btn = QPushButton("Xóa tất cả")
        self.save_btn = QPushButton("Lưu kịch bản")
        self.load_btn = QPushButton("Tải kịch bản")
        self.check_coord_btn = QPushButton("Kiểm tra toạ độ")
        self.check_coord_btn.setStyleSheet("background-color: #FFC107; color: black;")
        # Thiết lập style
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.stop_btn.setStyleSheet("background-color: #F44336; color: white;")
        self.stop_btn.setEnabled(False)

    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        self.setWindowTitle("Auto Clicker Pro")
        self.setWindowIcon(QIcon(str(ASSETS_DIR / "icon.png")))
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet(get_stylesheet())
        
        # Layout chính
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Tab tọa độ
        coord_tab = QWidget()
        self.setup_coord_tab(coord_tab)
        self.tab_widget.addTab(coord_tab, "Click theo tọa độ")
        
        # Tab ảnh
        image_tab = QWidget()
        self.setup_image_tab(image_tab)
        self.tab_widget.addTab(image_tab, "Click theo ảnh")
        
        main_layout.addWidget(self.tab_widget)




        # Bảng hành động
        self.setup_actions_table()
        main_layout.addWidget(self.action_table)
        
        # Nút điều khiển
        self.setup_control_buttons()
        main_layout.addLayout(self.control_layout)
    
    def setup_coord_tab(self, tab):
        """Thiết lập tab click theo tọa độ"""
        layout = QVBoxLayout(tab)
        
        # Nhóm nhập liệu
        input_group = QGroupBox("Thiết lập Click theo tọa độ")
        input_layout = QVBoxLayout()
        
        # Nhập tọa độ
        coord_layout = QHBoxLayout()
        coord_layout.addWidget(QLabel("Tọa độ X:"))
        self.x_input = QLineEdit()
        coord_layout.addWidget(self.x_input)
        
        coord_layout.addWidget(QLabel("Tọa độ Y:"))
        self.y_input = QLineEdit()
        coord_layout.addWidget(self.y_input)
        
        self.track_btn = QPushButton("Lấy vị trí")
        self.track_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        coord_layout.addWidget(self.track_btn)
        
        input_layout.addLayout(coord_layout)
        
        # Các tùy chọn
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("Loại Click:"))
        self.click_type = QComboBox()
        self.click_type.addItems(CLICK_TYPES)
        options_layout.addWidget(self.click_type)
        
        options_layout.addWidget(QLabel("Lặp lại:"))
        self.repeat_spin = QSpinBox()
        self.repeat_spin.setRange(1, 100)
        options_layout.addWidget(self.repeat_spin)
        
        self.move_back_check = QCheckBox("Di chuột về vị trí cũ")
        options_layout.addWidget(self.move_back_check)
        
        input_layout.addLayout(options_layout)
        
        # Delay (đổi thành QDoubleSpinBox)
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Delay (giây):"))
        self.delay_input = QDoubleSpinBox()
        self.delay_input.setRange(0.1, 10.0)  # Từ 0.1 đến 10 giây
        self.delay_input.setSingleStep(0.1)   # Bước nhảy 0.1 giây
        self.delay_input.setValue(1.0)        # Giá trị mặc định 1 giây
        delay_layout.addWidget(self.delay_input)
        
        input_layout.addLayout(delay_layout)
        
        # Nút thêm hành động
        self.add_coord_btn = QPushButton("Thêm hành động")
        self.add_coord_btn.setMinimumHeight(40)
        self.add_coord_btn.setMinimumWidth(180)
        self.add_coord_btn.setStyleSheet("background-color: #2196F3; color: white; font-size: 18px; font-weight: bold;")
        input_layout.addWidget(self.add_coord_btn)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
    
    def setup_image_tab(self, tab):
        """Thiết lập tab click theo ảnh"""
        layout = QVBoxLayout(tab)
        
        # Nhóm nhập liệu
        input_group = QGroupBox("Thiết lập Click theo ảnh")
        input_layout = QVBoxLayout()
        
        # Chọn ảnh
        image_layout = QHBoxLayout()
        image_layout.addWidget(QLabel("Ảnh mẫu:"))
        self.image_path = QLineEdit()
        image_layout.addWidget(self.image_path)
        
        self.browse_btn = QPushButton("Chọn ảnh")
        image_layout.addWidget(self.browse_btn)
        
        input_layout.addLayout(image_layout)
        
        # Khu vực tìm kiếm
        region_layout = QHBoxLayout()
        region_layout.addWidget(QLabel("Khu vực tìm kiếm:"))
        self.region_combo = QComboBox()
        custom_regions = list(SEARCH_REGIONS) + ["1/4 trái", "1/4 phải"]
        self.region_combo.addItems(custom_regions)
        region_layout.addWidget(self.region_combo)
        
        self.custom_region = QLineEdit()
        self.custom_region.setPlaceholderText("x1,y1,x2,y2")
        region_layout.addWidget(self.custom_region)
        
        input_layout.addLayout(region_layout)
        
        # Các tùy chọn
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("Loại Click:"))
        self.image_click_type = QComboBox()
        self.image_click_type.addItems(CLICK_TYPES)
        options_layout.addWidget(self.image_click_type)
        
        options_layout.addWidget(QLabel("Lặp lại:"))
        self.image_repeat = QSpinBox()
        self.image_repeat.setRange(1, 100)
        options_layout.addWidget(self.image_repeat)
        
        input_layout.addLayout(options_layout)
        
        # Delay
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Delay (giây):"))
        self.image_delay_input = QDoubleSpinBox()
        self.image_delay_input.setRange(0.1, 10.0)
        self.image_delay_input.setSingleStep(0.1)
        self.image_delay_input.setValue(1.0)
        delay_layout.addWidget(self.image_delay_input)
        
        input_layout.addLayout(delay_layout)
        
        # Nút kiểm tra và thêm
        btn_layout = QHBoxLayout()
        self.test_btn = QPushButton("Kiểm tra ảnh")
        btn_layout.addWidget(self.test_btn)
        
        self.add_image_btn = QPushButton("Thêm hành động")
        self.add_image_btn.setMinimumHeight(40)
        self.add_image_btn.setMinimumWidth(180)
        self.add_image_btn.setStyleSheet("background-color: #2196F3; color: white; font-size: 18px; font-weight: bold;")
        btn_layout.addWidget(self.add_image_btn)
        
        input_layout.addLayout(btn_layout)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
    
    def setup_actions_table(self):
        """Thiết lập bảng hành động với spinbox điều chỉnh số lần lặp"""
        self.action_table = QTableWidget()
        self.action_table.setColumnCount(9)  # Giảm 1 cột so với trước
        self.action_table.setHorizontalHeaderLabels(
            ["#", "Loại", "X/Ảnh", "Y/Khu vực", "Click", "Lặp", "Delay", "Di chuyển", "Xóa"]
        )
        self.action_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.action_table.verticalHeader().setVisible(False)
        
        # Đặt chiều rộng cố định cho các cột
        self.action_table.setColumnWidth(5, 80)   # Cột số lần lặp
        self.action_table.setColumnWidth(7, 100)  # Cột di chuyển
        self.action_table.setColumnWidth(8, 50)   # Cột xóa
    
    def add_control_buttons_to_row(self, row):
        """Thêm nút điều khiển vào hàng (đã điều chỉnh vị trí cột)"""
        # Nút di chuyển lên
        btn_up = QPushButton("↑")
        btn_up.setStyleSheet("padding: 2px; font-weight: bold;")
        btn_up.clicked.connect(lambda: self.move_row_up(row))
        
        # Nút di chuyển xuống
        btn_down = QPushButton("↓")
        btn_down.setStyleSheet("padding: 2px; font-weight: bold;")
        btn_down.clicked.connect(lambda: self.move_row_down(row))
        
        # Layout chứa 2 nút lên/xuống
        move_layout = QHBoxLayout()
        move_layout.addWidget(btn_up)
        move_layout.addWidget(btn_down)
        move_layout.setContentsMargins(0, 0, 0, 0)
        move_layout.setSpacing(2)
        
        move_widget = QWidget()
        move_widget.setLayout(move_layout)
        
        # Nút xóa
        btn_delete = QPushButton("X")
        btn_delete.setStyleSheet("padding: 2px; font-weight: bold; color: red;")
        btn_delete.clicked.connect(lambda: self.delete_row(row))
        
        # Thêm vào bảng (cột 7 và 8 thay vì 8 và 9 như trước)
        self.action_table.setCellWidget(row, 7, move_widget)
        self.action_table.setCellWidget(row, 8, btn_delete)

    def move_row_up(self, row):
        """Di chuyển hàng lên trên"""
        if row > 0:
            # Hoán đổi hàng trong danh sách actions
            self.actions_manager.actions[row], self.actions_manager.actions[row-1] = \
                self.actions_manager.actions[row-1], self.actions_manager.actions[row]
            self.update_actions_table()

    def move_row_down(self, row):
        """Di chuyển hàng xuống dưới"""
        if row < len(self.actions_manager.actions) - 1:
            # Hoán đổi hàng trong danh sách actions
            self.actions_manager.actions[row], self.actions_manager.actions[row+1] = \
                self.actions_manager.actions[row+1], self.actions_manager.actions[row]
            self.update_actions_table()

    def delete_row(self, row):
        """Xóa hàng khỏi bảng"""
        if 0 <= row < len(self.actions_manager.actions):
            self.actions_manager.remove_action(row)
            self.update_actions_table()

    def setup_control_buttons(self):
        """Thiết lập layout các nút điều khiển"""
        self.control_layout = QHBoxLayout()
        
        # Thêm phần lặp toàn bộ
        self.loop_layout = QHBoxLayout()
        self.loop_layout.addWidget(QLabel("Lặp toàn bộ:"))
        self.total_loop_spin = QSpinBox()
        self.total_loop_spin.setRange(1, 999)
        self.total_loop_spin.setValue(1)
        self.loop_layout.addWidget(self.total_loop_spin)
        self.loop_layout.addWidget(QLabel("lần"))

        self.loop_layout.addWidget(QLabel("Delay giữa các lần:"))
        self.loop_delay_input = QDoubleSpinBox()
        self.loop_delay_input.setRange(0, 60)
        self.loop_delay_input.setValue(0)
        self.loop_layout.addWidget(self.loop_delay_input)
        self.loop_layout.addWidget(QLabel("giây"))
        
        # Thêm các nút vào layout chính
        self.control_layout.addLayout(self.loop_layout)
        self.control_layout.addWidget(self.start_btn)
        self.control_layout.addWidget(self.stop_btn)
        self.control_layout.addWidget(self.check_coord_btn)
        self.control_layout.addWidget(self.clear_btn)
        self.control_layout.addWidget(self.save_btn)
        self.control_layout.addWidget(self.load_btn)
        # Căn chỉnh khoảng cách
        self.control_layout.setSpacing(10)
    
    def setup_events(self):
        """Kết nối các sự kiện"""
        # Tab tọa độ
        self.track_btn.clicked.connect(self.start_position_picker)
        self.add_coord_btn.clicked.connect(self.add_coordinate_action)
        
        # Tab ảnh
        self.browse_btn.clicked.connect(self.browse_image)
        self.test_btn.clicked.connect(self.test_image)
        self.add_image_btn.clicked.connect(self.add_image_action)

        # Điều khiển chung
        self.start_btn.clicked.connect(self.start_clicking)
        self.stop_btn.clicked.connect(self.stop_clicking)
        self.clear_btn.clicked.connect(self.clear_actions)
        self.save_btn.clicked.connect(self.save_script)
        self.load_btn.clicked.connect(self.load_script)
        self.check_coord_btn.clicked.connect(self.check_coordinate_highlight)
    
    def start_position_picker(self):
        """Bắt đầu chế độ chọn vị trí bằng cách di chuột và nhấn ESC"""
        self.is_tracking = True
        self.track_btn.setText("Đang chọn vị trí (ESC để hủy)")
        self.track_btn.setStyleSheet("background-color: #FF5722; color: white;")
        
        # Tạo label hiển thị vị trí chuột
        self.pos_label = QLabel("Di chuột đến vị trí cần lấy\nNhấn ESC để xác nhận", self)
        self.pos_label.setAlignment(Qt.AlignCenter)
        self.pos_label.setStyleSheet("""
            background-color: rgba(0,0,0,0.7); 
            color: white; 
            font-size: 16px;
            border-radius: 5px;
            padding: 10px;
        """)
        self.pos_label.resize(250, 80)
        self.pos_label.move(10, 10)
        self.pos_label.show()
        
        # Bắt đầu timer để cập nhật vị trí
        self.pos_timer = QTimer(self)
        self.pos_timer.timeout.connect(self.update_mouse_position)
        self.pos_timer.start(50)  # Cập nhật mỗi 50ms

    def update_mouse_position(self):
        """Cập nhật vị trí chuột liên tục"""
        if self.is_tracking:
            pos = pyautogui.position()
            self.pos_label.setText(f"X: {pos.x}, Y: {pos.y}\nNhấn ESC để xác nhận")
            self.pos_label.move(pos.x + 20, pos.y + 20)  # Di chuyển label theo chuột

    def keyPressEvent(self, event):
        """Bắt sự kiện phím ESC để lấy vị trí"""
        if self.is_tracking and event.key() == Qt.Key_Escape:
            pos = pyautogui.position()
            self.x_input.setText(str(pos.x))
            self.y_input.setText(str(pos.y))
            self.finish_position_picking()

    def finish_position_picking(self):
        """Kết thúc chế độ chọn vị trí"""
        self.is_tracking = False
        if hasattr(self, 'pos_timer'):
            self.pos_timer.stop()
        if hasattr(self, 'pos_label'):
            self.pos_label.hide()
        
        # Khôi phục trạng thái nút
        self.track_btn.setText("Lấy vị trí")
        self.track_btn.setStyleSheet("background-color: #4CAF50; color: white;")
    
    
    def browse_image(self):
        """Mở hộp thoại chọn ảnh"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh mẫu", "", "Image Files (*.png *.jpg *.bmp)")
        if filename:
            self.image_path.setText(filename)
    
    def test_image(self):
        """Kiểm tra tìm ảnh trên màn hình"""
        if not self.image_path.text():
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ảnh mẫu trước")
            return
        
        region = self.get_search_region()
        pos = self.image_clicker.find_image(self.image_path.text(), region)
        
        if pos:
            x, y = pos
            QMessageBox.information(
                self, "Thành công", 
                f"Tìm thấy ảnh tại vị trí ({x}, {y})"
            )
        else:
            QMessageBox.warning(self, "Không tìm thấy", "Không tìm thấy ảnh mẫu trên màn hình")
    
    def get_search_region(self):
        """Lấy khu vực tìm kiếm từ combobox"""
        region_text = self.region_combo.currentText()
        
        if region_text == "Toàn màn hình":
            return None
        elif region_text == "Nửa trái":
            width, height = pyautogui.size()
            return (0, 0, width // 2, height)
        elif region_text == "Nửa phải":
            width, height = pyautogui.size()
            return (width // 2, 0, width, height)
        elif region_text == "1/4 trái":
            width, height = pyautogui.size()
            return (0, 0, width // 4, height)
        elif region_text == "1/4 phải":
            width, height = pyautogui.size()
            return (width * 3 // 4, 0, width, height)
        elif region_text == "Tùy chỉnh":
            try:
                coords = list(map(int, self.custom_region.text().split(',')))
                if len(coords) == 4:
                    return tuple(coords)
            except:
                pass
        return None
    
    def add_coordinate_action(self):
        """Thêm hành động click theo tọa độ"""
        try:
            x = self.x_input.text()
            y = self.y_input.text()
            
            if not x or not y:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tọa độ")
                return
                
            action = GameAction(
                action_type="coordinate",
                x=x,
                y=y,
                click_type=self.click_type.currentText(),
                repeat=self.repeat_spin.value(),
                delay=self.delay_input.value(),  # Sử dụng delay_input.value()
                move_back=self.move_back_check.isChecked()
            )
            
            self.actions_manager.add_action(action)
            self.update_actions_table()
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra: {str(e)}")
    
    def add_image_action(self):
        """Thêm hành động click theo ảnh"""
        try:
            image_path = self.image_path.text()
            if not image_path:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ảnh mẫu")
                return
                
            region = self.get_search_region()
            region_text = self.region_combo.currentText()
            
            action = GameAction(
                action_type="image",
                x=image_path,
                y=region_text if region_text != "Tùy chỉnh" else self.custom_region.text(),
                click_type=self.image_click_type.currentText(),
                repeat=self.image_repeat.value(),
                delay=self.image_delay_input.value(),  # Sử dụng image_delay_input.value()
                move_back=False
            )
            
            self.actions_manager.add_action(action)
            self.update_actions_table()
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra: {str(e)}")
    
    def update_actions_table(self):
        """Cập nhật bảng hành động"""
        self.action_table.setRowCount(len(self.actions_manager.actions))
        
        for i, action in enumerate(self.actions_manager.actions):
            # Các cột thông tin
            self.action_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.action_table.setItem(i, 1, QTableWidgetItem(
                "Tọa độ" if action.action_type == "coordinate" else "Ảnh"
            ))
            self.action_table.setItem(i, 2, QTableWidgetItem(action.x))
            self.action_table.setItem(i, 3, QTableWidgetItem(action.y))
            self.action_table.setItem(i, 4, QTableWidgetItem(action.click_type))
            
            # Cột số lần lặp
            spin_box = QSpinBox()
            spin_box.setRange(1, 999)
            spin_box.setValue(action.repeat)
            spin_box.valueChanged.connect(lambda value, idx=i: self.update_repeat_count(idx, value))
            self.action_table.setCellWidget(i, 5, spin_box)
            
            # Cột delay (sử dụng QDoubleSpinBox)
            delay_spin = QDoubleSpinBox()
            delay_spin.setRange(0.1, 10.0)
            delay_spin.setSingleStep(0.1)
            delay_spin.setValue(action.delay)
            delay_spin.valueChanged.connect(lambda value, idx=i: self.update_delay(idx, value))
            self.action_table.setCellWidget(i, 6, delay_spin)
            
            # Thêm nút điều khiển
            self.add_control_buttons_to_row(i)
    
    def update_delay(self, row, value):
        """Cập nhật delay khi người dùng thay đổi giá trị"""
        if 0 <= row < len(self.actions_manager.actions):
            self.actions_manager.actions[row].delay = value

    def update_action_delay(self, row, value):
        if 0 <= row < len(self.actions_manager.actions):
            self.actions_manager.actions[row].delay = value

    def start_clicking(self):
        if not self.actions_manager.actions:
            QMessageBox.warning(self, "Lỗi", "Không có hành động nào để thực thi")
            return

        self.is_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Cập nhật worker
        self.worker.actions = self.actions_manager.actions
        self.worker.total_loops = self.total_loop_spin.value()
        self.worker.loop_delay = self.loop_delay_input.value()
        self.worker.running = True
        
        self.worker.start()

    def update_repeat_count(self, row, value):
        """Cập nhật số lần lặp khi người dùng thay đổi giá trị"""
        if 0 <= row < len(self.actions_manager.actions):
            self.actions_manager.actions[row].repeat = value
    
    def execute_coordinate_action(self, action):
        """Thực hiện hành động click theo tọa độ (tối ưu)"""
        if not self.is_running:
            return
        # Chỉ set delay 1 lần
        self.coord_clicker.set_delay(action.delay)
        # Gom click thành 1 lần nếu có thể
        self.coord_clicker.click(
            x=int(action.x),
            y=int(action.y),
            click_type=action.click_type,
            repeat=action.repeat,
            move_back=action.move_back
        )
    
    def execute_image_action(self, action):
        """Thực hiện hành động click theo ảnh (tối ưu)"""
        if not self.is_running:
            return
        self.coord_clicker.set_delay(action.delay)
        region = None
        if action.y == "Toàn màn hình":
            region = None
        elif action.y == "Nửa trái":
            width, height = pyautogui.size()
            region = (0, 0, width // 2, height)
        elif action.y == "Nửa phải":
            width, height = pyautogui.size()
            region = (width // 2, 0, width, height)
        else:
            try:
                region = tuple(map(int, action.y.split(',')))
            except:
                region = None
        pos = self.image_clicker.find_image(action.x, region)
        if pos:
            x, y = pos
            self.coord_clicker.click(
                x=x,
                y=y,
                click_type=action.click_type,
                repeat=action.repeat,
                move_back=False
            )
        else:
            QMessageBox.warning(self, "Cảnh báo", f"Không tìm thấy ảnh: {action.x}")
    
    def stop_clicking(self):
        """Dừng thực hiện các hành động (kể cả khi đang lặp)"""
        self.worker.running = False
    
    def on_worker_finished(self):
        self.is_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def on_worker_stopped(self):
        self.is_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.information(self, "Thông báo", "Đã dừng thực thi")

    def clear_actions(self):
        """Xóa tất cả hành động"""
        if self.actions_manager.actions:
            reply = QMessageBox.question(
                self, "Xác nhận",
                "Bạn có chắc muốn xóa tất cả hành động?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.actions_manager.clear_actions()
                self.update_actions_table()
    
    def save_script(self):
        """Lưu kịch bản ra file"""
        if not self.actions_manager.actions:
            QMessageBox.warning(self, "Lỗi", "Không có hành động nào để lưu")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Lưu kịch bản", "", "JSON Files (*.json)")
        
        if filename:
            self.actions_manager.save_to_file(filename)
            QMessageBox.information(self, "Thành công", "Đã lưu kịch bản thành công")
    
    def load_script(self):
        """Tải kịch bản từ file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Tải kịch bản", "", "JSON Files (*.json)")
        
        if filename:
            self.actions_manager.load_from_file(filename)
            self.update_actions_table()
            QMessageBox.information(self, "Thành công", "Đã tải kịch bản thành công")
    
    def closeEvent(self, event):
        """Xử lý khi đóng ứng dụng"""
        if self.is_tracking and self.overlay:
            self.overlay.close()
        super().closeEvent(event)


# =====================
# Main entry point
# =====================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoClickerGUI()
    window.show()
    sys.exit(app.exec_())