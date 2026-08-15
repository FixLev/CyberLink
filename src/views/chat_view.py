# src/views/chat_view.py
# Страница чатов с увеличенными шрифтами

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.theme.colors import COLORS


class ChatView(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Заголовок чата
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("border-bottom: 1px solid rgba(79, 195, 247, 0.06);")
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        title = QLabel("💬 Чаты")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #f5f5f5;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Кнопки действий
        actions = [
            ("📎", lambda: print("Прикрепить")),
            ("📞", lambda: print("Звонок")),
            ("⋮", lambda: print("Меню")),
        ]
        
        for text, callback in actions:
            btn = QPushButton(text)
            btn.setFixedSize(38, 38)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #8888aa;
                    border: none;
                    border-radius: 6px;
                    font-size: 20px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.05);
                    color: #f5f5f5;
                }
            """)
            btn.clicked.connect(callback)
            header_layout.addWidget(btn)
        
        layout.addWidget(header)
        
        # Область сообщений
        messages = QTextEdit()
        messages.setReadOnly(True)
        messages.setStyleSheet("""
            QTextEdit {
                background: transparent;
                color: #f5f5f5;
                border: none;
                padding: 15px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
                font-size: 16px;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.03);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.15);
            }
        """)
        messages.setPlaceholderText("Выберите чат, чтобы начать общение")
        layout.addWidget(messages)
        
        # Поле ввода
        input_container = QFrame()
        input_container.setFixedHeight(64)
        input_container.setStyleSheet("border-top: 1px solid rgba(79, 195, 247, 0.06);")
        
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(15, 10, 15, 10)
        input_layout.setSpacing(12)
        
        attach_btn = QPushButton("📎")
        attach_btn.setFixedSize(42, 42)
        attach_btn.setCursor(Qt.PointingHandCursor)
        attach_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #8888aa;
                border: none;
                border-radius: 6px;
                font-size: 22px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.05);
                color: #f5f5f5;
            }
        """)
        input_layout.addWidget(attach_btn)
        
        input_field = QLineEdit()
        input_field.setPlaceholderText("Введите сообщение...")
        input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(30, 30, 48, 0.4);
                color: #f5f5f5;
                border: 1px solid rgba(79, 195, 247, 0.08);
                border-radius: 22px;
                padding: 12px 18px;
                font-size: 16px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
            }
            QLineEdit:focus {
                border-color: rgba(79, 195, 247, 0.25);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.25);
            }
        """)
        input_layout.addWidget(input_field)
        
        mic_btn = QPushButton("🎙️")
        mic_btn.setFixedSize(42, 42)
        mic_btn.setCursor(Qt.PointingHandCursor)
        mic_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #8888aa;
                border: none;
                border-radius: 6px;
                font-size: 22px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.05);
                color: #f5f5f5;
            }
        """)
        input_layout.addWidget(mic_btn)
        
        send_btn = QPushButton("📤")
        send_btn.setFixedSize(42, 42)
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.setStyleSheet("""
            QPushButton {
                background: rgba(79, 195, 247, 0.15);
                color: #4fc3f7;
                border: none;
                border-radius: 21px;
                font-size: 22px;
            }
            QPushButton:hover {
                background: rgba(79, 195, 247, 0.25);
            }
        """)
        input_layout.addWidget(send_btn)
        
        layout.addWidget(input_container)