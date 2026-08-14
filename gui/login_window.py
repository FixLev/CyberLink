import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from gui.styles import LOGIN_STYLE, CYBERLINK_ASCII, COLORS

class LoginWindow(QDialog):
    """Окно входа в CyberLink"""
    
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.username = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("CyberLink - Вход в систему")
        self.setFixedSize(550, 500)
        self.setStyleSheet(LOGIN_STYLE)
        
        # Устанавливаем модальность
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        
        # Центральный виджет
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(50, 40, 50, 40)
        
        # ASCII логотип (в GUI используем стилизованный текст)
        logo_label = QLabel("CYBERLINK")
        logo_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {COLORS['neon_pink']};
            font-family: 'Consolas', monospace;
            letter-spacing: 5px;
        """)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        subtitle = QLabel("⚡ Децентрализованный P2P Мессенджер ⚡")
        subtitle.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['neon_blue']};
            font-family: 'Consolas', monospace;
            letter-spacing: 2px;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {COLORS['neon_blue']}; max-height: 2px;")
        layout.addWidget(line)
        
        layout.addSpacing(20)
        
        # Информация
        info_box = QFrame()
        info_box.setStyleSheet(f"""
            background-color: {COLORS['dark_card']};
            border: 1px solid {COLORS['neon_blue']};
            border-radius: 10px;
            padding: 15px;
        """)
        info_layout = QVBoxLayout(info_box)
        
        info_text = QLabel("🔐 Безопасный вход в CyberLink")
        info_text.setStyleSheet(f"color: {COLORS['neon_green']}; font-weight: bold; font-size: 13px;")
        info_layout.addWidget(info_text)
        
        info_text2 = QLabel("• Ваши данные хранятся только на вашем устройстве")
        info_text2.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        info_layout.addWidget(info_text2)
        
        info_text3 = QLabel("• Все сообщения передаются напрямую (P2P)")
        info_text3.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        info_layout.addWidget(info_text3)
        
        info_text4 = QLabel("• Никаких серверов и централизованных хранилищ")
        info_text4.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        info_layout.addWidget(info_text4)
        
        layout.addWidget(info_box)
        
        layout.addSpacing(10)
        
        # Поле для логина
        login_label = QLabel("👤 Логин (@никнейм):")
        login_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: bold; font-size: 13px;")
        layout.addWidget(login_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите логин (3-24 символа)")
        self.username_input.textChanged.connect(self.on_username_changed)
        self.username_input.returnPressed.connect(self.try_login)
        layout.addWidget(self.username_input)
        
        # Индикатор валидности
        self.valid_label = QLabel("")
        self.valid_label.setStyleSheet(f"color: {COLORS['neon_pink']}; font-size: 12px; font-family: 'Consolas', monospace;")
        layout.addWidget(self.valid_label)
        
        layout.addSpacing(20)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.login_btn = QPushButton("🔑 Войти")
        self.login_btn.setEnabled(False)
        self.login_btn.clicked.connect(self.login)
        btn_layout.addWidget(self.login_btn)
        
        self.register_btn = QPushButton("📝 Регистрация")
        self.register_btn.setEnabled(False)
        self.register_btn.clicked.connect(self.register)
        btn_layout.addWidget(self.register_btn)
        
        layout.addLayout(btn_layout)
        
        # Информация о формате
        info = QLabel("💡 Имя может содержать латиницу, цифры и _ (3-24 символа)")
        info.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        # Версия
        version = QLabel("CyberLink v1.0.0 | P2P Network")
        version.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10px; margin-top: 10px;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
    
    def on_username_changed(self, text):
        """Проверка ввода логина"""
        username = text.strip()
        if not username:
            self.valid_label.setText("")
            self.login_btn.setEnabled(False)
            self.register_btn.setEnabled(False)
            return
        
        # Проверяем валидность
        valid, message = self.user_manager.validate_username(username)
        if valid:
            self.valid_label.setText("✅ Логин валидный")
            self.valid_label.setStyleSheet(f"color: {COLORS['neon_green']}; font-size: 12px; font-family: 'Consolas', monospace;")
            
            # Проверяем, существует ли пользователь
            exists = self.user_manager.user_exists(username)
            if exists:
                self.valid_label.setText("✅ Пользователь найден! Входите.")
                self.login_btn.setEnabled(True)
                self.register_btn.setEnabled(False)
            else:
                self.valid_label.setText("✅ Новый пользователь! Зарегистрируйтесь.")
                self.login_btn.setEnabled(False)
                self.register_btn.setEnabled(True)
        else:
            self.valid_label.setText(f"❌ {message}")
            self.valid_label.setStyleSheet(f"color: {COLORS['neon_pink']}; font-size: 12px; font-family: 'Consolas', monospace;")
            self.login_btn.setEnabled(False)
            self.register_btn.setEnabled(False)
    
    def try_login(self):
        """Попытка входа по Enter"""
        if self.login_btn.isEnabled():
            self.login()
        elif self.register_btn.isEnabled():
            self.register()
    
    def login(self):
        """Вход в систему"""
        username = self.username_input.text().strip()
        success, message = self.user_manager.login_user(username)
        
        if success:
            self.username = username
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", message)
    
    def register(self):
        """Регистрация нового пользователя"""
        username = self.username_input.text().strip()
        success, message = self.user_manager.register_user(username)
        
        if success:
            QMessageBox.information(
                self, 
                "Успех", 
                f"✅ Пользователь @{username} успешно зарегистрирован!\n\nТеперь вы можете войти в CyberLink."
            )
            self.username = username
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", message)
    
    def get_username(self):
        """Получение имени пользователя"""
        return self.username