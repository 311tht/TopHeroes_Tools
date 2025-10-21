# [file name]: main.py
# [file content begin]
import sys
import random
import pyautogui
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
                            QPushButton, QLabel, QLineEdit, QComboBox, QSpinBox,
                            QCheckBox, QHBoxLayout, QVBoxLayout, QWidget, QFileDialog,
                            QGroupBox, QHeaderView, QMessageBox, QTabWidget, QDoubleSpinBox) 
from PyQt5.QtCore import Qt, QTimer, QPoint,QThread, pyqtSignal
from PyQt5.QtGui import QIcon

from PyQt5.QtGui import QIcon, QPainter, QPen, QBrush, QColor, QFont
from PyQt5.QtCore import Qt, QTimer, QPoint, QThread, pyqtSignal, QRect

from coordinate_click import CoordinateClicker
from image_click import ImageClicker
from actions_manager import ActionsManager, GameAction
from config import CLICK_TYPES, SEARCH_REGIONS, ASSETS_DIR
from styles import get_stylesheet

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
                    elif action.action_type == "image":
                        self.parent.execute_image_action(action)
                
                # Thêm delay giữa các lần lặp toàn bộ
                if _ < self.total_loops - 1:  # Không delay sau lần cuối
                    time.sleep(self.loop_delay)
        
        finally:
            self.finished.emit()
            if not self.running:
                self.stopped.emit()



class AutoClickerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.coord_clicker = CoordinateClicker()
        self.image_clicker = ImageClicker()
        self.actions_manager = ActionsManager()
        
        # Khởi tạo các nút điều khiển trước

        self.worker = Worker(self)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.stopped.connect(self.on_worker_stopped)

        # Thêm biến để theo dõi trạng thái kiểm tra
        self.is_testing = False
        self.test_overlay = None

        self.init_control_buttons()
        
        self.setup_ui()
        self.setup_events()
        
        self.is_tracking = False
        self.is_running = False
    
    def init_control_buttons(self):
        """Khởi tạo tất cả nút điều khiển"""
        self.start_btn = QPushButton("Bắt đầu")
        self.stop_btn = QPushButton("Dừng lại")
        self.clear_btn = QPushButton("Xóa tất cả")
        self.save_btn = QPushButton("Lưu kịch bản")
        self.load_btn = QPushButton("Tải kịch bản")

        self.test_all_btn = QPushButton("Kiểm tra")
        
        # Thiết lập style
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.stop_btn.setStyleSheet("background-color: #F44336; color: white;")
        self.test_all_btn.setStyleSheet("background-color: #FF9800; color: white;")
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
        self.add_coord_btn.setStyleSheet("background-color: #2196F3; color: white;")
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
        self.region_combo.addItems(SEARCH_REGIONS)
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
        self.add_image_btn.setStyleSheet("background-color: #2196F3; color: white;")
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
        self.control_layout.addWidget(self.test_all_btn)
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
        self.test_all_btn.clicked.connect(self.toggle_test_all_actions)
        self.clear_btn.clicked.connect(self.clear_actions)
        self.save_btn.clicked.connect(self.save_script)
        self.load_btn.clicked.connect(self.load_script)
    
    def start_position_picker(self):
        """Bắt đầu chế độ chọn vị trí bằng cách di chuột và nhấn ESC"""
        self.is_tracking = True
        self.track_btn.setText("Đang chọn vị trí (ESC để hủy)")
        self.track_btn.setStyleSheet("background-color: #FF5722; color: white;")
        
        # Tạo label hiển thị vị trí chuột
        self.pos_label = QLabel("", self)
        self.pos_label.setStyleSheet("background-color: yellow; color: black; padding: 5px;")
        self.pos_label.move(10, 10)
        self.pos_label.show()
        
        # Bắt đầu timer để cập nhật vị trí
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_mouse_position)
        self.timer.start(100)  # Cập nhật mỗi 100ms
    
    def update_mouse_position(self):
        """Cập nhật vị trí chuột hiện tại"""
        if self.is_tracking:
            x, y = pyautogui.position()
            self.pos_label.setText(f"X: {x}, Y: {y}")
            
            # Kiểm tra nếu nhấn ESC
            try:
                import keyboard
                if keyboard.is_pressed('esc'):
                    self.stop_position_picker()
            except:
                pass
    
    def stop_position_picker(self):
        """Dừng chế độ chọn vị trí"""
        self.is_tracking = False
        self.timer.stop()
        self.pos_label.hide()
        self.track_btn.setText("Lấy vị trí")
        self.track_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        
        # Lấy vị trí cuối cùng
        x, y = pyautogui.position()
        self.x_input.setText(str(x))
        self.y_input.setText(str(y))
    
    def add_coordinate_action(self):
        """Thêm hành động click tọa độ vào danh sách"""
        try:
            x = int(self.x_input.text())
            y = int(self.y_input.text())
            click_type = self.click_type.currentText()
            repeat = self.repeat_spin.value()
            delay = self.delay_input.value()
            move_back = self.move_back_check.isChecked()
            
            action = GameAction(
                action_type="coordinate",
                x=x,
                y=y,
                click_type=click_type,
                repeat=repeat,
                delay=delay,
                move_back=move_back
            )
            
            self.actions_manager.add_action(action)
            self.update_actions_table()
            
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tọa độ hợp lệ")
    
    def browse_image(self):
        """Mở hộp thoại chọn ảnh"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh mẫu", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.image_path.setText(file_path)
    
    def test_image(self):
        """Kiểm tra tìm ảnh trên màn hình"""
        image_path = self.image_path.text()
        if not image_path:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ảnh mẫu")
            return
        
        region = self.get_search_region()
        
        try:
            result = self.image_clicker.find_image_on_screen(image_path, region)
            if result:
                x, y = result
                QMessageBox.information(
                    self, "Kết quả", 
                    f"Tìm thấy ảnh tại vị trí ({x}, {y})"
                )
                # Di chuột đến vị trí tìm thấy
                pyautogui.moveTo(x, y)
            else:
                QMessageBox.warning(self, "Kết quả", "Không tìm thấy ảnh")
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi tìm ảnh: {str(e)}")
    
    def get_search_region(self):
        """Lấy khu vực tìm kiếm từ combobox hoặc nhập tùy chỉnh"""
        region_text = self.region_combo.currentText()
        if region_text == "Toàn màn hình":
            return None
        elif region_text == "Tùy chỉnh":
            custom = self.custom_region.text()
            if custom:
                try:
                    x1, y1, x2, y2 = map(int, custom.split(','))
                    return (x1, y1, x2, y2)
                except:
                    QMessageBox.warning(self, "Lỗi", "Định dạng khu vực tùy chỉnh không hợp lệ")
                    return None
        else:
            # Các khu vực định nghĩa sẵn
            regions = {
                "Nửa trên": (0, 0, pyautogui.size().width, pyautogui.size().height // 2),
                "Nửa dưới": (0, pyautogui.size().height // 2, pyautogui.size().width, pyautogui.size().height),
                "Góc trái trên": (0, 0, pyautogui.size().width // 2, pyautogui.size().height // 2)
            }
            return regions.get(region_text, None)
    
    def add_image_action(self):
        """Thêm hành động click ảnh vào danh sách"""
        image_path = self.image_path.text()
        if not image_path:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ảnh mẫu")
            return
        
        region = self.get_search_region()
        click_type = self.image_click_type.currentText()
        repeat = self.image_repeat.value()
        delay = self.image_delay_input.value()
        
        action = GameAction(
            action_type="image",
            image_path=image_path,
            region=region,
            click_type=click_type,
            repeat=repeat,
            delay=delay
        )
        
        self.actions_manager.add_action(action)
        self.update_actions_table()
    
    def update_actions_table(self):
        """Cập nhật bảng hiển thị danh sách hành động"""
        self.action_table.setRowCount(len(self.actions_manager.actions))
        
        for row, action in enumerate(self.actions_manager.actions):
            # Cột số thứ tự
            self.action_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            
            # Cột loại hành động
            self.action_table.setItem(row, 1, QTableWidgetItem(
                "Tọa độ" if action.action_type == "coordinate" else "Ảnh"
            ))
            
            # Cột thông tin tọa độ/ảnh
            if action.action_type == "coordinate":
                self.action_table.setItem(row, 2, QTableWidgetItem(str(action.x)))
                self.action_table.setItem(row, 3, QTableWidgetItem(str(action.y)))
            else:
                self.action_table.setItem(row, 2, QTableWidgetItem(action.image_path))
                region_text = "Toàn màn hình" if not action.region else str(action.region)
                self.action_table.setItem(row, 3, QTableWidgetItem(region_text))
            
            # Cột loại click
            self.action_table.setItem(row, 4, QTableWidgetItem(action.click_type))
            
            # Cột số lần lặp (sử dụng QSpinBox)
            spin_box = QSpinBox()
            spin_box.setRange(1, 100)
            spin_box.setValue(action.repeat)
            spin_box.valueChanged.connect(lambda value, r=row: self.update_repeat_count(r, value))
            self.action_table.setCellWidget(row, 5, spin_box)
            
            # Cột delay (sử dụng QDoubleSpinBox)
            delay_spin = QDoubleSpinBox()
            delay_spin.setRange(0.1, 10.0)
            delay_spin.setSingleStep(0.1)
            delay_spin.setValue(action.delay)
            delay_spin.valueChanged.connect(lambda value, r=row: self.update_delay(r, value))
            self.action_table.setCellWidget(row, 6, delay_spin)
            
            # Thêm nút điều khiển
            self.add_control_buttons_to_row(row)
    
    def update_repeat_count(self, row, value):
        """Cập nhật số lần lặp của hành động"""
        if 0 <= row < len(self.actions_manager.actions):
            self.actions_manager.actions[row].repeat = value
    
    def update_delay(self, row, value):
        """Cập nhật delay của hành động"""
        if 0 <= row < len(self.actions_manager.actions):
            self.actions_manager.actions[row].delay = value
    
    def start_clicking(self):
        """Bắt đầu thực hiện các hành động"""
        if not self.actions_manager.actions:
            QMessageBox.warning(self, "Lỗi", "Không có hành động nào để thực hiện")
            return
        
        self.is_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.test_all_btn.setEnabled(False)
        
        # Thiết lập worker
        self.worker.actions = self.actions_manager.actions.copy()
        self.worker.total_loops = self.total_loop_spin.value()
        self.worker.loop_delay = self.loop_delay_input.value()
        self.worker.running = True
        
        self.worker.start()
    
    def stop_clicking(self):
        """Dừng thực hiện các hành động"""
        self.worker.running = False
        self.is_running = False
    
    def on_worker_finished(self):
        """Khi worker hoàn thành"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.test_all_btn.setEnabled(True)
    
    def on_worker_stopped(self):
        """Khi worker bị dừng"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.test_all_btn.setEnabled(True)
    
    def toggle_test_all_actions(self):
        """Chuyển đổi giữa chế độ kiểm tra và hủy kiểm tra"""
        if not self.is_testing:
            self.start_test_all_actions()
        else:
            self.cancel_test_all_actions()
    
    def start_test_all_actions(self):
        """Bắt đầu kiểm tra tất cả hành động"""
        if not self.actions_manager.actions:
            QMessageBox.warning(self, "Lỗi", "Không có hành động nào để kiểm tra")
            return
        
        self.is_testing = True
        self.test_all_btn.setText("Hủy kiểm tra")
        self.test_all_btn.setStyleSheet("background-color: #F44336; color: white;")
        
        # Tạo overlay để hiển thị các điểm click
        self.create_test_overlay()
        
        # Thực hiện kiểm tra (bỏ qua các hành động tìm ảnh)
        self.test_actions()
    
    def cancel_test_all_actions(self):
        """Hủy kiểm tra tất cả hành động"""
        self.is_testing = False
        self.test_all_btn.setText("Kiểm tra")
        self.test_all_btn.setStyleSheet("background-color: #FF9800; color: white;")
        
        # Xóa overlay
        if self.test_overlay:
            self.test_overlay.close()
            self.test_overlay = None
    
    def create_test_overlay(self):
        """Tạo overlay để hiển thị các điểm click"""
        self.test_overlay = QMainWindow()
        self.test_overlay.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.test_overlay.setAttribute(Qt.WA_TranslucentBackground)
        self.test_overlay.setGeometry(0, 0, pyautogui.size().width, pyautogui.size().height)
        
        overlay_widget = QWidget()
        overlay_widget.setStyleSheet("background-color: transparent;")
        self.test_overlay.setCentralWidget(overlay_widget)
        
        self.test_overlay.show()
    
    def test_actions(self):
        """Kiểm tra các hành động (bỏ qua tìm ảnh, chỉ hiển thị điểm click)"""
        if not self.is_testing:
            return
        
        # Vẽ các điểm click lên overlay
        self.draw_click_points()
        
        # Thực hiện các hành động (bỏ qua tìm ảnh)
        for action in self.actions_manager.actions:
            if not self.is_testing:  # Kiểm tra lại trạng thái
                break
                
            if action.action_type == "coordinate":
                # Chỉ di chuột đến vị trí mà không click
                pyautogui.moveTo(action.x, action.y)
                time.sleep(0.5)  # Delay để người dùng nhìn thấy
            elif action.action_type == "image":
                # Bỏ qua hành động tìm ảnh trong chế độ kiểm tra
                continue
    
    def draw_click_points(self):
        """Vẽ các điểm click lên overlay"""
        if not self.test_overlay:
            return
        
        # Lấy widget chính của overlay
        overlay_widget = self.test_overlay.centralWidget()
        
        # Vẽ các điểm cho hành động tọa độ
        for action in self.actions_manager.actions:
            if action.action_type == "coordinate":
                # Tạo label hoặc vẽ điểm tại vị trí
                label = QLabel("●", overlay_widget)
                label.setStyleSheet("color: red; font-size: 20px; background-color: transparent;")
                label.move(action.x - 10, action.y - 10)  # Điều chỉnh vị trí
                label.show()
    
    def execute_coordinate_action(self, action):
        """Thực hiện hành động click tọa độ"""
        for _ in range(action.repeat):
            if not self.worker.running:
                break
                
            current_pos = pyautogui.position()
            
            # Thực hiện click
            self.coord_clicker.click_at(action.x, action.y, action.click_type)
            
            # Di chuyển về vị trí cũ nếu được chọn
            if action.move_back:
                pyautogui.moveTo(current_pos)
            
            # Thêm delay giữa các lần lặp
            if _ < action.repeat - 1:
                time.sleep(action.delay)
    
    def execute_image_action(self, action):
        """Thực hiện hành động click ảnh"""
        for _ in range(action.repeat):
            if not self.worker.running:
                break
                
            # Tìm và click vào ảnh
            result = self.image_clicker.find_and_click(
                action.image_path, 
                action.region, 
                action.click_type
            )
            
            # Thêm delay giữa các lần lặp
            if _ < action.repeat - 1:
                time.sleep(action.delay)
    
    def clear_actions(self):
        """Xóa tất cả hành động"""
        self.actions_manager.clear_actions()
        self.update_actions_table()
    
    def save_script(self):
        """Lưu kịch bản vào file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu kịch bản", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                self.actions_manager.save_to_file(file_path)
                QMessageBox.information(self, "Thành công", "Đã lưu kịch bản")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi khi lưu file: {str(e)}")
    
    def load_script(self):
        """Tải kịch bản từ file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Tải kịch bản", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                self.actions_manager.load_from_file(file_path)
                self.update_actions_table()
                QMessageBox.information(self, "Thành công", "Đã tải kịch bản")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi khi tải file: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = AutoClickerGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
# [file content end]