# src/widgets/rotation_speed_dialog.py
# Диалог настройки курсора

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.utils.dialogs import CyberDialog


class RotationSpeedDialog:
    """Диалог настройки курсора"""
    
    @staticmethod
    def show(parent, cursor_widget):
        if not cursor_widget:
            return
        
        dialog = CyberDialog(parent, "Настройка курсора", width=400, height=250)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        
        label = QLabel("Курсор статичный. Вращение отключено.")
        label.setStyleSheet("color: #f5f5f5; font-size: 14px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        info = QLabel("""
        4 угла образуют квадрат.
        Каждый угол имеет свой цвет и начальный поворот.
        При наведении на кнопки углы становятся ярче.
        """)
        info.setStyleSheet("color: #8888aa; font-size: 12px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Кнопка закрытия
        close_btn = QPushButton("OK")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(79, 195, 247, 0.15);
                color: #4fc3f7;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(79, 195, 247, 0.25);
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        
        dialog.set_content(content)
        dialog.exec_()
        return True