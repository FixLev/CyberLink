# src/views/login_view.py
# Окно входа с кастомным курсором

import random
import math
import time
import re

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.theme.colors import COLORS
from src.core.user_manager import UserManager
from src.widgets.custom_cursor_widget import CustomCursorWidget


class LoginSpaceWidget(QWidget):
    """Космический фон для окна входа"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        
        self.stars = []
        for _ in range(100):
            self.stars.append({
                'x': random.randint(0, 10000),
                'y': random.randint(0, 10000),
                'size': random.randint(1, 2),
                'speed': random.uniform(0.2, 0.6),
                'phase': random.uniform(0, 6.28),
                'opacity': random.uniform(0.3, 1.0),
                'brightness': random.uniform(180, 255),
            })
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        w = self.width()
        h = self.height()
        
        gradient = QLinearGradient(0, 0, w, h)
        gradient.setColorAt(0, QColor(5, 5, 15))
        gradient.setColorAt(0.5, QColor(8, 8, 30))
        gradient.setColorAt(1, QColor(5, 5, 15))
        painter.fillRect(0, 0, w, h, gradient)
        
        for star in self.stars:
            x = int(star['x'] * w / 10000)
            y = int(star['y'] * h / 10000)
            size = max(1, int(star['size'] * w / 2000))
            opacity = int(star['opacity'] * star['brightness'])
            
            color = QColor(255, 255, 255, opacity)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x - size//2, y - size//2, size, size)
    
    def animate(self):
        for star in self.stars:
            star['opacity'] = 0.3 + 0.7 * abs(
                math.sin(time.time() * star['speed'] + star['phase'])
            )
        self.update()


class LoginView(QDialog):
    def __init__(self):
        super().__init__()
        self.user_manager = UserManager()
        self.username = None
        self.drag_pos = None
        self.password_visible = False
        self.cursor = None
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("CyberLink - Вход")
        self.setFixedSize(480, 460)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.space_widget = LoginSpaceWidget(self)
        self.space_widget.setGeometry(0, 0, 480, 460)
        
        glass = QFrame(self.space_widget)
        glass.setGeometry(15, 15, 450, 430)
        glass.setStyleSheet("""
            QFrame {
                background-color: rgba(10, 10, 25, 0.15);
                border: 1px solid rgba(79, 195, 247, 0.06);
                border-radius: 16px;
            }
        """)
        
        glass.mousePressEvent = self.mousePressEvent
        glass.mouseMoveEvent = self.mouseMoveEvent
        glass.mouseReleaseEvent = self.mouseReleaseEvent
        
        # === СОЗДАЁМ КУРСОР ДЛЯ ОКНА ЛОГИНА ===
        try:
            self.cursor = CustomCursorWidget(self)
            self.cursor.raise_()
        except:
            pass
        
        close_btn = QPushButton("✕", glass)
        close_btn.setFixedSize(28, 28)
        close_btn.move(410, 10)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #8888aa;
                border: none;
                border-radius: 6px;
                font-size: 15px;
            }
            QPushButton:hover {
                background: #ff2d55;
                color: white;
            }
        """)
        close_btn.clicked.connect(self.reject)
        
        layout = QVBoxLayout(glass)
        layout.setSpacing(10)
        layout.setContentsMargins(35, 20, 35, 20)
        
        logo = QLabel("✦ CYBERLINK")
        logo.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #f5f5f5;
            font-family: 'Karvx', 'Arial', sans-serif;
            background: transparent;
            border: none;
        """)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        
        layout.addSpacing(25)
        
        # Поле логина - без @
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите логин")
        self.username_input.setMaxLength(24)
        self.username_input.setStyleSheet("""
            QLineEdit {
                background: rgba(30, 30, 48, 0.6);
                color: #f5f5f5;
                border: 1px solid rgba(79, 195, 247, 0.15);
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
                font-smooth: always;
                -webkit-font-smoothing: antialiased;
            }
            QLineEdit:focus {
                border-color: rgba(79, 195, 247, 0.4);
                background: rgba(30, 30, 48, 0.8);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.3);
                font-style: italic;
            }
        """)
        layout.addWidget(self.username_input)
        
        # Поле пароля - без замка
        password_container = QWidget()
        password_container.setStyleSheet("background: transparent;")
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(0)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMaxLength(24)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background: rgba(30, 30, 48, 0.6);
                color: #f5f5f5;
                border: 1px solid rgba(79, 195, 247, 0.15);
                border-radius: 12px 0px 0px 12px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
                border-right: none;
                font-smooth: always;
                -webkit-font-smoothing: antialiased;
            }
            QLineEdit:focus {
                border-color: rgba(79, 195, 247, 0.4);
                background: rgba(30, 30, 48, 0.8);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.3);
                font-style: italic;
            }
        """)
        password_layout.addWidget(self.password_input, stretch=1)
        
        self.eye_btn = QPushButton("👁")
        self.eye_btn.setFixedSize(46, 46)
        self.eye_btn.setCursor(Qt.PointingHandCursor)
        self.eye_btn.setStyleSheet("""
            QPushButton {
                background: rgba(30, 30, 48, 0.6);
                color: #8888aa;
                border: 1px solid rgba(79, 195, 247, 0.15);
                border-radius: 0px 12px 12px 0px;
                font-size: 18px;
                padding: 0px;
                border-left: none;
                font-smooth: always;
                -webkit-font-smoothing: antialiased;
            }
            QPushButton:hover {
                background: rgba(30, 30, 48, 0.8);
                color: #f5f5f5;
            }
        """)
        self.eye_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.eye_btn)
        
        layout.addWidget(password_container)
        
        layout.addSpacing(15)
        
        self.action_btn = QPushButton("🚀 Войти / Создать")
        self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4fc3f7,
                    stop:1 #7b2ffc);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'TT Mussels', 'Arial', sans-serif;
                font-smooth: always;
                -webkit-font-smoothing: antialiased;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #81d4fa,
                    stop:1 #8b4ffc);
            }
        """)
        self.action_btn.clicked.connect(self.handle_auth)
        layout.addWidget(self.action_btn)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            color: #ff6b6b;
            font-size: 12px;
            font-family: 'TT Mussels', 'Arial', sans-serif;
            background: transparent;
            border: none;
            font-smooth: always;
            -webkit-font-smoothing: antialiased;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.glass = glass
    
    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        
        if self.password_visible:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.eye_btn.setText("🙈")
            self.eye_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(30, 30, 48, 0.8);
                    color: #4fc3f7;
                    border: 1px solid rgba(79, 195, 247, 0.4);
                    border-radius: 0px 12px 12px 0px;
                    font-size: 18px;
                    padding: 0px;
                    border-left: none;
                    font-smooth: always;
                    -webkit-font-smoothing: antialiased;
                }
            """)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.eye_btn.setText("👁")
            self.eye_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(30, 30, 48, 0.6);
                    color: #8888aa;
                    border: 1px solid rgba(79, 195, 247, 0.15);
                    border-radius: 0px 12px 12px 0px;
                    font-size: 18px;
                    padding: 0px;
                    border-left: none;
                    font-smooth: always;
                    -webkit-font-smoothing: antialiased;
                }
                QPushButton:hover {
                    background: rgba(30, 30, 48, 0.8);
                    color: #f5f5f5;
                }
            """)
        
        self.password_input.setFocus()
    
    def validate_input(self, text):
        clean = text
        if clean.startswith('@'):
            clean = clean[1:]
        return bool(re.match(r'^[a-zA-Z0-9_]*$', clean))
    
    def handle_auth(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.status_label.setText("❌ Заполните все поля")
            return
        
        # Проверяем, не начинается ли с @
        if username.startswith('@'):
            self.status_label.setText("❌ Не используйте @ в логине")
            return
        
        clean_username = username
        
        if not clean_username:
            self.status_label.setText("❌ Введите логин")
            return
        
        if not self.validate_input(clean_username):
            self.status_label.setText("❌ Только латиница, цифры и _")
            return
        
        if not self.validate_input(password):
            self.status_label.setText("❌ Только латиница, цифры и _")
            return
        
        if len(clean_username) < 3:
            self.status_label.setText("❌ Логин минимум 3 символа")
            return
        
        if len(password) < 6:
            self.status_label.setText("❌ Пароль минимум 6 символов")
            return
        
        exists = self.user_manager.user_exists(clean_username)
        
        if exists:
            success, message = self.user_manager.login_user(clean_username, password)
            if success:
                self.username = clean_username
                self.accept()
            else:
                self.status_label.setText(f"❌ {message}")
        else:
            success, message = self.user_manager.register_user(clean_username, password)
            if success:
                self.username = clean_username
                self.accept()
            else:
                self.status_label.setText(f"❌ {message}")
    
    def get_username(self):
        return self.username
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() <= 80:
            self.drag_pos = event.globalPos()
        else:
            self.drag_pos = None
    
    def mouseMoveEvent(self, event):
        if self.drag_pos is not None:
            delta = event.globalPos() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = event.globalPos()
    
    def mouseReleaseEvent(self, event):
        self.drag_pos = None
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.handle_auth()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.stop()
        event.accept()