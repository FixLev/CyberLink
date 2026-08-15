# src/utils/dialogs.py
# Единый стиль для всех диалоговых окон

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


def get_dialog_style():
    """Стиль для всех диалоговых окон"""
    return """
        QDialog {
            background: rgba(10, 10, 25, 0.98);
            color: #f5f5f5;
            border: 1px solid rgba(79, 195, 247, 0.1);
            border-radius: 12px;
        }
        QLabel {
            color: #f5f5f5;
            font-size: 14px;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        }
        QPushButton {
            background: rgba(79, 195, 247, 0.12);
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
        QPushButton:disabled {
            background: rgba(255, 255, 255, 0.03);
            color: #666688;
        }
        QLineEdit {
            background: rgba(30, 30, 48, 0.6);
            color: #f5f5f5;
            border: 1px solid rgba(79, 195, 247, 0.15);
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        }
        QLineEdit:focus {
            border-color: rgba(79, 195, 247, 0.4);
        }
        QLineEdit::placeholder {
            color: rgba(255, 255, 255, 0.3);
        }
        QTextEdit {
            background: rgba(30, 30, 48, 0.6);
            color: #f5f5f5;
            border: 1px solid rgba(79, 195, 247, 0.15);
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        }
        QTextEdit:focus {
            border-color: rgba(79, 195, 247, 0.4);
        }
        QComboBox {
            background: rgba(30, 30, 48, 0.6);
            color: #f5f5f5;
            border: 1px solid rgba(79, 195, 247, 0.15);
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 14px;
            font-family: 'TT Mussels', 'Arial', sans-serif;
            min-width: 150px;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #8888aa;
            margin-right: 5px;
        }
        QComboBox QAbstractItemView {
            background: rgba(30, 30, 48, 0.9);
            color: #f5f5f5;
            border: 1px solid rgba(79, 195, 247, 0.15);
            border-radius: 8px;
            selection-background-color: rgba(79, 195, 247, 0.2);
        }
        QCheckBox {
            color: #f5f5f5;
            font-size: 14px;
            font-family: 'TT Mussels', 'Arial', sans-serif;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 5px;
            border: 2px solid rgba(79, 195, 247, 0.3);
            background: rgba(30, 30, 48, 0.6);
        }
        QCheckBox::indicator:checked {
            background: rgba(79, 195, 247, 0.4);
            border-color: #4fc3f7;
        }
        QScrollArea {
            background: transparent;
            border: none;
        }
        QScrollBar:vertical {
            background: rgba(255, 255, 255, 0.03);
            width: 6px;
            border-radius: 3px;
        }
        QScrollBar::handle:vertical {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background: rgba(255, 255, 255, 0.15);
        }
    """


class CyberDialog(QDialog):
    """Стандартный диалог CyberLink с тёмной темой"""
    
    def __init__(self, parent=None, title="", content=None, width=450, height=300):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(width, height)
        self.setStyleSheet(get_dialog_style())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        
        if content:
            layout.addWidget(content)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.05);
                color: #8888aa;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Сохранить")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def set_content(self, widget):
        """Установка содержимого диалога"""
        layout = self.layout()
        layout.insertWidget(0, widget)


def show_cyber_message(parent, title, message, icon=QMessageBox.Information):
    """Показ сообщения в стиле CyberLink"""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(icon)
    msg.setStyleSheet(get_dialog_style())
    
    # Настраиваем кнопку
    ok_btn = msg.addButton("OK", QMessageBox.AcceptRole)
    ok_btn.setStyleSheet("""
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
    
    return msg.exec_()


def show_cyber_input_dialog(parent, title, label, text=""):
    """Показ диалога ввода в стиле CyberLink"""
    dialog = CyberDialog(parent, title, width=450, height=250)
    
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setSpacing(15)
    
    label_widget = QLabel(label)
    label_widget.setStyleSheet("color: #f5f5f5; font-size: 14px; font-family: 'TT Mussels', 'Arial', sans-serif;")
    layout.addWidget(label_widget)
    
    input_field = QLineEdit()
    input_field.setText(text)
    input_field.setStyleSheet("""
        QLineEdit {
            background: rgba(30, 30, 48, 0.6);
            color: #f5f5f5;
            border: 1px solid rgba(79, 195, 247, 0.15);
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        }
        QLineEdit:focus {
            border-color: rgba(79, 195, 247, 0.4);
        }
    """)
    layout.addWidget(input_field)
    
    dialog.set_content(content)
    
    if dialog.exec_() == QDialog.Accepted:
        return True, input_field.text()
    return False, ""