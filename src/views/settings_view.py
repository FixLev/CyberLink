# src/views/settings_view.py
# Страница настроек

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.theme.colors import COLORS
from src.core.profile_manager import ProfileManager
from src.utils.dialogs import CyberDialog, get_dialog_style, show_cyber_message


class SettingsView(QWidget):
    def __init__(self, username=None, main_window=None, friends_manager=None, network=None, password=None):
        super().__init__()
        self.username = username
        self.main_window = main_window
        self.friends_manager = friends_manager
        self.network = network
        self.password = password
        
        # Создаём ProfileManager с паролем
        if username and password:
            self.profile_manager = ProfileManager(username, password)
        else:
            self.profile_manager = ProfileManager(username) if username else None
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Заголовок
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("border-bottom: 1px solid rgba(79, 195, 247, 0.06);")
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("⚙️ Настройки")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #f5f5f5;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addWidget(header)
        
        # Контент
        self.content = QScrollArea()
        self.content.setWidgetResizable(True)
        self.content.setStyleSheet("""
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
        """)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(30, 20, 30, 20)
        self.content_layout.setSpacing(15)
        
        # Приватность профиля
        self.add_setting_category("🔒 Приватность профиля")
        self.add_setting_item("📱 Телефон", "Кто видит ваш номер", "phone")
        self.add_setting_item("📧 Email", "Кто видит ваш email", "email")
        self.add_setting_item("⚧️ Пол", "Кто видит ваш пол", "gender")
        self.add_setting_item("🎂 Дата рождения", "Кто видит вашу дату рождения", "birth_date")
        self.add_setting_item("🏙️ Город", "Кто видит ваш город", "city")
        self.add_setting_item("🌍 Страна", "Кто видит вашу страну", "country")
        self.add_setting_item("💼 Должность", "Кто видит вашу должность", "occupation")
        self.add_setting_item("🏢 Компания", "Кто видит вашу компанию", "company")
        self.add_setting_item("📝 Статус", "Кто видит ваш статус", "bio")
        
        # Общие настройки
        self.add_setting_category("🔒 Общие настройки")
        self.add_setting_item("Кто видит мой статус онлайн", "Настройка видимости статуса", "last_seen")
        self.add_setting_item("Кто может писать мне", "Настройка сообщений", "who_can_message_me")
        
        # Статус
        self.add_setting_category("🟢 Статус активности")
        self.add_setting_item("Изменить статус активности", "Онлайн, Не беспокоить, Отошёл, Невидимка", "status")
        
        # В разработке
        self.add_setting_category("🚧 В разработке")
        self.add_setting_item("Уведомления", "Скоро будет доступно", None)
        self.add_setting_item("Внешний вид", "Скоро будет доступно", None)
        self.add_setting_item("Язык", "Скоро будет доступно", None)
        
        self.content_layout.addStretch()
        self.content.setWidget(self.content_widget)
        layout.addWidget(self.content)
    
    def add_setting_category(self, title):
        label = QLabel(title)
        label.setStyleSheet("""
            color: #4fc3f7;
            font-size: 16px;
            font-weight: bold;
            font-family: 'TT Mussels', 'Arial', sans-serif;
            margin-top: 10px;
        """)
        self.content_layout.addWidget(label)
    
    def add_setting_item(self, title, description, key):
        item = QPushButton()
        item.setCursor(Qt.PointingHandCursor)
        item.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.02);
                border: none;
                border-radius: 12px;
                padding: 16px 20px;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.05);
            }
        """)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(0, 0, 0, 0)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #f5f5f5; font-size: 14px; font-weight: bold; font-family: 'TT Mussels', 'Arial', sans-serif;")
        info_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #8888aa; font-size: 12px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        info_layout.addWidget(desc_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        arrow = QLabel("›")
        arrow.setStyleSheet("color: #666688; font-size: 20px;")
        layout.addWidget(arrow)
        
        if key:
            item.clicked.connect(lambda: self.open_setting(key))
        else:
            item.setEnabled(False)
            item.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.02);
                    border: none;
                    border-radius: 12px;
                    padding: 16px 20px;
                    text-align: left;
                    opacity: 0.5;
                }
            """)
        
        self.content_layout.addWidget(item)
    
    def open_setting(self, key):
        if key == "who_can_message_me":
            self.show_message_privacy()
        elif key == "last_seen":
            self.show_last_seen()
        elif key == "status":
            self.show_status_settings()
        else:
            self.open_privacy_dialog(key)
    
    def open_privacy_dialog(self, key):
        if not self.profile_manager:
            show_cyber_message(self, "Ошибка", "❌ Профиль не загружен", QMessageBox.Critical)
            return
        
        titles = {
            "phone": "Телефон",
            "email": "Email",
            "gender": "Пол",
            "birth_date": "Дату рождения",
            "city": "Город",
            "country": "Страну",
            "occupation": "Должность",
            "company": "Компанию",
            "bio": "Статус",
        }
        title = titles.get(key, key)
        
        privacy = self.profile_manager.get_privacy()
        current_data = privacy.get(key, {"level": "contacts", "selected": []})
        current_level = current_data.get("level", "contacts")
        current_selected = current_data.get("selected", [])
        
        dialog = CyberDialog(self, f"Приватность: {title}", width=450, height=380)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        
        label = QLabel(f"Кто видит {title.lower()}:")
        label.setStyleSheet("color: #f5f5f5; font-size: 14px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        layout.addWidget(label)
        
        combo = QComboBox()
        combo.addItems(["Все", "Контакты", "Выбранные", "Никто"])
        levels = {"everyone": 0, "contacts": 1, "selected": 2, "nobody": 3}
        combo.setCurrentIndex(levels.get(current_level, 1))
        layout.addWidget(combo)
        
        selected_label = QLabel("Выбранные пользователи (через пробел):")
        selected_label.setStyleSheet("color: #8888aa; font-size: 13px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        selected_label.hide()
        layout.addWidget(selected_label)
        
        selected_input = QLineEdit()
        selected_input.setPlaceholderText("user1 user2 user3")
        selected_input.setText(" ".join(current_selected))
        selected_input.setStyleSheet("""
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
        selected_input.hide()
        layout.addWidget(selected_input)
        
        def on_level_change(index):
            if index == 2:
                selected_label.show()
                selected_input.show()
            else:
                selected_label.hide()
                selected_input.hide()
        
        combo.currentIndexChanged.connect(on_level_change)
        if combo.currentIndex() == 2:
            selected_label.show()
            selected_input.show()
        
        dialog.set_content(content)
        
        if dialog.exec_() == QDialog.Accepted:
            level_map = {0: "everyone", 1: "contacts", 2: "selected", 3: "nobody"}
            new_level = level_map.get(combo.currentIndex(), "contacts")
            
            selected_text = selected_input.text().strip()
            selected_users = []
            if selected_text:
                users = [u.strip() for u in selected_text.split() if u.strip()]
                selected_users = users
            
            self.profile_manager.update_privacy({
                key: {"level": new_level, "selected": selected_users}
            })
            show_cyber_message(self, "Успех", "✅ Настройки сохранены!", QMessageBox.Information)
    
    def show_last_seen(self):
        if not self.profile_manager:
            show_cyber_message(self, "Ошибка", "❌ Профиль не загружен", QMessageBox.Critical)
            return
        
        privacy = self.profile_manager.get_privacy()
        current = privacy.get("last_seen", {}).get("level", "contacts")
        current_selected = privacy.get("last_seen", {}).get("selected", [])
        
        dialog = CyberDialog(self, "Кто видит мой статус онлайн", width=450, height=380)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        
        label = QLabel("Кто видит мой статус онлайн:")
        label.setStyleSheet("color: #f5f5f5; font-size: 14px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        layout.addWidget(label)
        
        combo = QComboBox()
        combo.addItems(["Все", "Контакты", "Выбранные", "Никто"])
        levels = {"everyone": 0, "contacts": 1, "selected": 2, "nobody": 3}
        combo.setCurrentIndex(levels.get(current, 1))
        layout.addWidget(combo)
        
        selected_label = QLabel("Выбранные пользователи (через пробел):")
        selected_label.setStyleSheet("color: #8888aa; font-size: 13px;")
        selected_label.hide()
        layout.addWidget(selected_label)
        
        selected_input = QLineEdit()
        selected_input.setPlaceholderText("user1 user2 user3")
        selected_input.setText(" ".join(current_selected))
        selected_input.setStyleSheet("""
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
        selected_input.hide()
        layout.addWidget(selected_input)
        
        def on_level_change(index):
            if index == 2:
                selected_label.show()
                selected_input.show()
            else:
                selected_label.hide()
                selected_input.hide()
        
        combo.currentIndexChanged.connect(on_level_change)
        if combo.currentIndex() == 2:
            selected_label.show()
            selected_input.show()
        
        dialog.set_content(content)
        
        if dialog.exec_() == QDialog.Accepted:
            level_map = {0: "everyone", 1: "contacts", 2: "selected", 3: "nobody"}
            new_level = level_map.get(combo.currentIndex(), "contacts")
            
            selected_text = selected_input.text().strip()
            selected_users = []
            if selected_text:
                users = [u.strip() for u in selected_text.split() if u.strip()]
                selected_users = users
            
            self.profile_manager.update_privacy({
                "last_seen": {"level": new_level, "selected": selected_users}
            })
            show_cyber_message(self, "Успех", "✅ Настройки сохранены!", QMessageBox.Information)
    
    def show_message_privacy(self):
        if not self.profile_manager:
            show_cyber_message(self, "Ошибка", "❌ Профиль не загружен", QMessageBox.Critical)
            return
        
        privacy = self.profile_manager.get_privacy()
        current = privacy.get("who_can_message_me", "everyone")
        
        dialog = CyberDialog(self, "Кто может писать мне", width=450, height=250)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        
        label = QLabel("Кто может писать мне:")
        label.setStyleSheet("color: #f5f5f5; font-size: 14px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        layout.addWidget(label)
        
        combo = QComboBox()
        combo.addItems(["Все", "Контакты"])
        combo.setCurrentIndex({"everyone": 0, "contacts": 1}.get(current, 0))
        layout.addWidget(combo)
        
        dialog.set_content(content)
        
        if dialog.exec_() == QDialog.Accepted:
            level_map = {0: "everyone", 1: "contacts"}
            self.profile_manager.update_privacy({"who_can_message_me": level_map.get(combo.currentIndex(), "everyone")})
            show_cyber_message(self, "Успех", "✅ Настройки сохранены!", QMessageBox.Information)
    
    def show_status_settings(self):
        if not self.profile_manager:
            show_cyber_message(self, "Ошибка", "❌ Профиль не загружен", QMessageBox.Critical)
            return
        
        privacy = self.profile_manager.get_privacy()
        current_status = privacy.get("status", "online")
        
        dialog = CyberDialog(self, "Статус активности", width=450, height=250)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        
        label = QLabel("Выберите статус:")
        label.setStyleSheet("color: #f5f5f5; font-size: 14px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        layout.addWidget(label)
        
        combo = QComboBox()
        combo.addItems(["🟢 Онлайн", "🟡 Не беспокоить", "🟠 Отошёл", "⚪ Невидимка"])
        status_values = ["online", "dnd", "idle", "invisible"]
        combo.setCurrentIndex(status_values.index(current_status) if current_status in status_values else 0)
        layout.addWidget(combo)
        
        dialog.set_content(content)
        
        if dialog.exec_() == QDialog.Accepted:
            status_map = {0: "online", 1: "dnd", 2: "idle", 3: "invisible"}
            new_status = status_map.get(combo.currentIndex(), "online")
            self.profile_manager.set_status(new_status)
            self.update_status_in_main(new_status)
            show_cyber_message(self, "Успех", "✅ Статус обновлён!", QMessageBox.Information)
    
    def update_status_in_main(self, status):
        status_icons = {"online": "🟢", "dnd": "🟡", "idle": "🟠", "invisible": "⚪"}
        status_texts = {"online": "Онлайн", "dnd": "Не беспокоить", "idle": "Отошёл", "invisible": "Невидимка"}
        
        main_window = self.window()
        if hasattr(main_window, 'status_label'):
            main_window.status_label.setText(
                f"{status_icons.get(status, '🟢')} {status_texts.get(status, 'Онлайн')}"
            )