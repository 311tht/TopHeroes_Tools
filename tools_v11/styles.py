def get_stylesheet():
    return """
    QMainWindow {
        background-color: #f5f5f5;
        font-family: Arial;
    }
    QGroupBox {
        border: 1px solid #ddd;
        border-radius: 5px;
        margin-top: 10px;
        padding-top: 15px;
    }
    QTableWidget {
        border: 1px solid #ddd;
        alternate-background-color: #f9f9f9;
    }
    QHeaderView::section {
        background-color: #607D8B;  
        color: white;
        padding: 5px;
    }
    QPushButton {
        padding: 5px 10px;
        border-radius: 3px;
        background-color: #e0e0e0;
    }
    QPushButton:hover {
        background-color: #d0d0d0;
    }
    QTabWidget::pane {
        border: 1px solid #ddd;
    }
    QTabBar::tab {
        padding: 5px 10px;
        background: #e0e0e0;
        border: 1px solid #ddd;
        border-bottom: none;
        border-top-left-radius: 3px;
        border-top-right-radius: 3px;
    }
    QTabBar::tab:selected {
        background: white;
    }

        /* Style cho SpinBox trong bảng */
    QSpinBox {
        padding: 2px;
        border: 1px solid #ddd;
        border-radius: 3px;
    }
       QSpinBox {
        min-width: 60px;
        padding: 3px;
    }
    """