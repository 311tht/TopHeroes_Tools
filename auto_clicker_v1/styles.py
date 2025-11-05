def get_stylesheet():
    return """
QMainWindow {
    background-color: #f5f5f5;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QGroupBox {
    border: 1px solid #ddd;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 15px;
    background: #fff;
}
QTableWidget {
    border: 1px solid #ddd;
    alternate-background-color: #f9f9f9;
    background: #fff;
}
QHeaderView::section {
    background-color: #1976D2;
    color: white;
    padding: 6px;
    border-radius: 0px;
    font-weight: bold;
}
QPushButton {
    padding: 7px 16px;
    border-radius: 5px;
    background-color: #2196F3;
    color: white;
    font-weight: 500;
    border: none;
    font-size: 15px;
}
QPushButton:hover {
    background-color: #1976D2;
}
QPushButton:disabled {
    background-color: #bdbdbd;
    color: #eee;
}
QTabWidget::pane {
    border: 1px solid #ddd;
    border-radius: 8px;
}
QTabBar::tab {
    padding: 7px 18px;
    background: #e3e3e3;
    border: 1px solid #ddd;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-size: 15px;
}
QTabBar::tab:selected {
    background: #fff;
    color: #1976D2;
}
QSpinBox, QDoubleSpinBox, QLineEdit {
    border: 1px solid #bbb;
    border-radius: 4px;
    padding: 4px 8px;
    background: #fafafa;
    font-size: 15px;
}
QProgressBar {
    border: 1px solid #bbb;
    border-radius: 6px;
    text-align: center;
    height: 18px;
    background: #eee;
}
QProgressBar::chunk {
    background-color: #1976D2;
    border-radius: 6px;
}
"""