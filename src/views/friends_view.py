# src/views/friends_view.py
# Страница друзей и приглашений

import json
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.theme.colors import COLORS
from src.core.profile_manager import ProfileManager
from src.utils.dialogs import CyberDialog, show_cyber_message


class FriendsView(QWidget):
    def __init__(self, username, friends_manager=None, network=None):
        super().__init__()
        self.username = username
        self.friends_manager = friends_manager
        self.network = network
        
        # Для обратной совместимости
        if friends_manager is None:
            self.profile_manager = ProfileManager(username)
        else:
            self.profile_manager = None
        
        self.init_ui()
        self.load_friends()
        
        # Подключаем сигналы если есть friends_manager
        if self.friends_manager:
            self.friends_manager.friend_added.connect(self.load_friends)
            self.friends_manager.friend_removed.connect(self.load_friends)
            self.friends_manager.friend_request_received.connect(self.load_friends)
            self.friends_manager.friend_request_responded.connect(self.load_friends)
        
        # Если есть сеть - подключаем её сигналы
        if self.network:
            self.network.friend_online.connect(self.load_friends)
            self.network.friend_offline.connect(self.load_friends)
    
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
        
        title = QLabel("🤝 Друзья")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #f5f5f5;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Кнопка добавить друга
        add_btn = QPushButton("➕ Добавить друга")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background: rgba(79, 195, 247, 0.12);
                color: #4fc3f7;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 14px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(79, 195, 247, 0.2);
            }
        """)
        add_btn.clicked.connect(self.add_friend)
        header_layout.addWidget(add_btn)
        
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
        
        # Секция: Входящие заявки
        self.add_section("📨 Входящие заявки")
        self.pending_container = QVBoxLayout()
        self.pending_container.setSpacing(8)
        self.content_layout.addLayout(self.pending_container)
        
        # Секция: Мои друзья
        self.add_section("👥 Мои друзья")
        self.friends_container = QVBoxLayout()
        self.friends_container.setSpacing(8)
        self.content_layout.addLayout(self.friends_container)
        
        # Секция: Приветственное сообщение
        self.add_section("💬 Приветственное сообщение")
        self.add_welcome_message()
        
        self.content_layout.addStretch()
        
        self.content.setWidget(self.content_widget)
        layout.addWidget(self.content)
    
    def add_section(self, title):
        label = QLabel(title)
        label.setStyleSheet("""
            color: #4fc3f7;
            font-size: 16px;
            font-weight: bold;
            font-family: 'TT Mussels', 'Arial', sans-serif;
            margin-top: 10px;
        """)
        self.content_layout.addWidget(label)
    
    def add_welcome_message(self):
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.02);
                border-radius: 12px;
                padding: 16px;
            }
        """)
        layout = QVBoxLayout(container)
        
        desc = QLabel("Сообщение, которое увидят пользователи при отправке заявки в друзья (до 100 символов):")
        desc.setStyleSheet("color: #8888aa; font-size: 13px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        layout.addWidget(desc)
        
        self.welcome_input = QLineEdit()
        self.welcome_input.setMaxLength(100)
        self.welcome_input.setPlaceholderText("Введите приветственное сообщение...")
        self.welcome_input.setStyleSheet("""
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
        self.welcome_input.textChanged.connect(self.save_welcome_message)
        layout.addWidget(self.welcome_input)
        
        char_count = QLabel("0 / 100")
        char_count.setStyleSheet("color: #666688; font-size: 11px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        char_count.setAlignment(Qt.AlignRight)
        
        def update_count(text):
            char_count.setText(f"{len(text)} / 100")
        
        self.welcome_input.textChanged.connect(update_count)
        layout.addWidget(char_count)
        
        self.content_layout.addWidget(container)
    
    def load_friends(self):
        # Очищаем контейнеры
        self._clear_layout(self.pending_container)
        self._clear_layout(self.friends_container)
        
        # Если есть friends_manager - используем его
        if self.friends_manager:
            self._load_friends_from_manager()
        else:
            self._load_friends_from_profile()
    
    def _clear_layout(self, layout):
        """Очистка layout от всех виджетов"""
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _load_friends_from_manager(self):
        """Загрузка из FriendsManager"""
        pending = self.friends_manager.get_pending_requests()
        friends = self.friends_manager.get_friends_list()
        
        if pending:
            for req in pending:
                from_id = req.get('from')
                if from_id:
                    self.pending_container.addWidget(self.create_pending_item(from_id, req))
        else:
            empty = QLabel("Нет входящих заявок")
            empty.setStyleSheet("color: #666688; font-size: 13px; font-family: 'TT Mussels', 'Arial', sans-serif; padding: 10px;")
            self.pending_container.addWidget(empty)
        
        if friends:
            for friend in friends:
                friend_id = friend.get('id')
                display_name = friend.get('display_name', friend_id)
                self.friends_container.addWidget(self.create_friend_item(friend_id, display_name))
        else:
            empty = QLabel("У вас пока нет друзей\n\n💫 Нажмите «Добавить друга» чтобы найти друзей")
            empty.setStyleSheet("color: #666688; font-size: 13px; font-family: 'TT Mussels', 'Arial', sans-serif; padding: 10px;")
            empty.setAlignment(Qt.AlignCenter)
            self.friends_container.addWidget(empty)
        
        # Приветственное сообщение
        if self.profile_manager:
            profile = self.profile_manager.get_profile()
            welcome = profile.get("welcome_message", "")
            self.welcome_input.setText(welcome)
    
    def _load_friends_from_profile(self):
        """Загрузка из ProfileManager (старый способ)"""
        contacts = self.profile_manager.get_contacts()
        
        pending = contacts.get("pending", [])
        if pending:
            for username in pending:
                self.pending_container.addWidget(self.create_pending_item(username, {'from': username}))
        else:
            empty = QLabel("Нет входящих заявок")
            empty.setStyleSheet("color: #666688; font-size: 13px; font-family: 'TT Mussels', 'Arial', sans-serif; padding: 10px;")
            self.pending_container.addWidget(empty)
        
        friends = contacts.get("contacts", [])
        if friends:
            for username in friends:
                self.friends_container.addWidget(self.create_friend_item(username, username))
        else:
            empty = QLabel("У вас пока нет друзей\n\n💫 Нажмите «Добавить друга» чтобы найти друзей")
            empty.setStyleSheet("color: #666688; font-size: 13px; font-family: 'TT Mussels', 'Arial', sans-serif; padding: 10px;")
            empty.setAlignment(Qt.AlignCenter)
            self.friends_container.addWidget(empty)
        
        profile = self.profile_manager.get_profile()
        welcome = profile.get("welcome_message", "")
        self.welcome_input.setText(welcome)
    
    def create_pending_item(self, username, request=None):
        item = QFrame()
        item.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 10px;
                padding: 12px;
            }
            QFrame:hover {
                background: rgba(255, 255, 255, 0.05);
            }
        """)
        
        layout = QVBoxLayout(item)
        layout.setSpacing(5)
        
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        
        avatar = QLabel("👤")
        avatar.setStyleSheet("font-size: 24px;")
        top_row.addWidget(avatar)
        
        name = QLabel(f"{username}")
        name.setStyleSheet("color: #f5f5f5; font-size: 14px; font-weight: bold; font-family: 'TT Mussels', 'Arial', sans-serif;")
        top_row.addWidget(name)
        
        top_row.addStretch()
        
        accept_btn = QPushButton("✅ Принять")
        accept_btn.setCursor(Qt.PointingHandCursor)
        accept_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 136, 0.15);
                color: #00ff88;
                border: none;
                border-radius: 6px;
                padding: 5px 14px;
                font-size: 12px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(0, 255, 136, 0.25);
            }
        """)
        accept_btn.clicked.connect(lambda: self.accept_friend(username))
        top_row.addWidget(accept_btn)
        
        reject_btn = QPushButton("❌ Отклонить")
        reject_btn.setCursor(Qt.PointingHandCursor)
        reject_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 45, 85, 0.15);
                color: #ff2d55;
                border: none;
                border-radius: 6px;
                padding: 5px 14px;
                font-size: 12px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 45, 85, 0.25);
            }
        """)
        reject_btn.clicked.connect(lambda: self.reject_friend(username))
        top_row.addWidget(reject_btn)
        
        layout.addLayout(top_row)
        
        # Приветственное сообщение
        msg = request.get('message', '') if request else ''
        if msg:
            msg_label = QLabel(f"💬 {msg}")
            msg_label.setStyleSheet("color: #8888aa; font-size: 12px; font-family: 'TT Mussels', 'Arial', sans-serif; padding-left: 40px;")
            layout.addWidget(msg_label)
        elif self.profile_manager:
            profile = self.profile_manager.get_profile()
            welcome = profile.get("welcome_message", "")
            if welcome:
                msg_label = QLabel(f"💬 {welcome}")
                msg_label.setStyleSheet("color: #8888aa; font-size: 12px; font-family: 'TT Mussels', 'Arial', sans-serif; padding-left: 40px;")
                layout.addWidget(msg_label)
        
        return item
    
    def create_friend_item(self, username, display_name=None):
        item = QFrame()
        item.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 10px;
                padding: 12px;
            }
            QFrame:hover {
                background: rgba(255, 255, 255, 0.05);
            }
        """)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Статус
        is_online = False
        if self.friends_manager:
            is_online = self.friends_manager.is_online(username)
        elif self.network:
            # Проверяем через сеть
            pass
        
        status_icon = "🟢" if is_online else "⚪"
        
        avatar = QLabel("👤")
        avatar.setStyleSheet("font-size: 24px;")
        layout.addWidget(avatar)
        
        name_text = display_name if display_name else username
        name = QLabel(f"{status_icon} {name_text}")
        name.setStyleSheet(f"""
            color: {'#00ff88' if is_online else '#f5f5f5'};
            font-size: 14px;
            font-weight: bold;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        """)
        layout.addWidget(name)
        
        layout.addStretch()
        
        chat_btn = QPushButton("💬 Чат")
        chat_btn.setCursor(Qt.PointingHandCursor)
        chat_btn.setStyleSheet("""
            QPushButton {
                background: rgba(79, 195, 247, 0.12);
                color: #4fc3f7;
                border: none;
                border-radius: 6px;
                padding: 5px 14px;
                font-size: 12px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(79, 195, 247, 0.2);
            }
        """)
        chat_btn.clicked.connect(lambda: self.open_chat(username))
        layout.addWidget(chat_btn)
        
        remove_btn = QPushButton("🗑️")
        remove_btn.setFixedSize(28, 28)
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #8888aa;
                border: none;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(255, 45, 85, 0.15);
                color: #ff2d55;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_friend(username))
        layout.addWidget(remove_btn)
        
        return item
    
    def add_friend(self):
        dialog = CyberDialog(self, "Добавить друга")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel("Введите имя пользователя:")
        label.setStyleSheet("color: #f5f5f5; font-size: 14px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        layout.addWidget(label)
        
        input_field = QLineEdit()
        input_field.setPlaceholderText("username")
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
        
        msg_label = QLabel("Приветственное сообщение (необязательно):")
        msg_label.setStyleSheet("color: #8888aa; font-size: 13px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        layout.addWidget(msg_label)
        
        msg_input = QLineEdit()
        msg_input.setMaxLength(100)
        msg_input.setPlaceholderText("Напишите что-то приятное...")
        msg_input.setStyleSheet("""
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
        layout.addWidget(msg_input)
        
        layout.addStretch()
        
        dialog.set_content(content)
        
        if dialog.exec_() == QDialog.Accepted:
            target_username = input_field.text().strip()
            
            # Убираем @ если пользователь его ввёл
            if target_username.startswith('@'):
                target_username = target_username[1:]
            
            if not target_username:
                return
            
            if target_username == self.username:
                self.show_error("Нельзя добавить самого себя!")
                return
            
            # Проверяем через friends_manager
            if self.friends_manager:
                if self.friends_manager.is_friend(target_username):
                    self.show_error(f"{target_username} уже в друзьях!")
                    return
                
                # Проверяем, не отправлена ли уже заявка
                pending = self.friends_manager.get_pending_requests()
                for req in pending:
                    if req.get('from') == target_username:
                        self.show_error(f"Заявка от {target_username} уже ожидает!")
                        return
                
                # Проверяем существование пользователя в сети
                if self.network:
                    print(f"🔍 Проверка существования пользователя {target_username} в сети...")
                    user_info = self.network.find_user(target_username)
                    if not user_info:
                        # Проверяем локальный реестр
                        from src.core.user_manager import UserManager
                        um = UserManager()
                        if um.user_exists(target_username):
                            self.show_error(f"Пользователь {target_username} найден локально, но не активен в сети.\nЗапустите CyberLink на его устройстве.")
                        else:
                            self.show_error(f"Пользователь {target_username} не найден в сети")
                        return
                    print(f"✅ Пользователь {target_username} найден в сети")
                
                # Отправляем заявку
                if self.friends_manager.send_friend_request(target_username, msg_input.text().strip()):
                    self.show_success(f"Заявка {target_username} отправлена!")
                    self.load_friends()
                else:
                    self.show_error(f"Не удалось отправить заявку {target_username}")
            else:
                # Старый способ через ProfileManager
                contacts = self.profile_manager.get_contacts()
                if target_username in contacts.get("contacts", []):
                    self.show_error(f"{target_username} уже в друзьях!")
                    return
                if target_username in contacts.get("pending", []):
                    self.show_error(f"Заявка {target_username} уже отправлена!")
                    return
                
                if self.profile_manager.add_contact(target_username):
                    welcome_msg = msg_input.text().strip()
                    if welcome_msg:
                        contacts = self.profile_manager.get_contacts()
                        if "welcome_messages" not in contacts:
                            contacts["welcome_messages"] = {}
                        contacts["welcome_messages"][target_username] = welcome_msg
                        with open(self.profile_manager.contacts_file, 'w', encoding='utf-8') as f:
                            json.dump(contacts, f, indent=2, ensure_ascii=False)
                    
                    self.show_success(f"Заявка {target_username} отправлена!")
                    self.load_friends()
                else:
                    self.show_error(f"Не удалось отправить заявку {target_username}")
    
    def accept_friend(self, username):
        if self.friends_manager:
            if self.friends_manager.accept_friend_request(username):
                self.show_success(f"{username} добавлен в друзья!")
                self.load_friends()
            else:
                self.show_error(f"Не удалось принять заявку от {username}")
        else:
            if self.profile_manager.accept_contact(username):
                self.show_success(f"{username} добавлен в друзья!")
                self.load_friends()
            else:
                self.show_error(f"Не удалось принять заявку от {username}")
    
    def reject_friend(self, username):
        reply = QMessageBox.question(
            self,
            "Отклонить заявку",
            f"Вы уверены, что хотите отклонить заявку от {username}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.friends_manager:
                if self.friends_manager.reject_friend_request(username):
                    self.show_success(f"Заявка от {username} отклонена")
                    self.load_friends()
            else:
                contacts = self.profile_manager.get_contacts()
                if username in contacts.get("pending", []):
                    contacts["pending"].remove(username)
                    with open(self.profile_manager.contacts_file, 'w', encoding='utf-8') as f:
                        json.dump(contacts, f, indent=2, ensure_ascii=False)
                    self.show_success(f"Заявка от {username} отклонена")
                    self.load_friends()
    
    def remove_friend(self, username):
        reply = QMessageBox.question(
            self,
            "Удалить друга",
            f"Вы уверены, что хотите удалить {username} из друзей?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.friends_manager:
                if self.friends_manager.remove_friend(username):
                    self.show_success(f"{username} удалён из друзей")
                    self.load_friends()
            else:
                if self.profile_manager.remove_contact(username):
                    self.show_success(f"{username} удалён из друзей")
                    self.load_friends()
    
    def open_chat(self, username):
        main_window = self.window()
        if hasattr(main_window, 'switch_mode'):
            main_window.switch_mode('chats')
            if hasattr(main_window, 'chat_page'):
                main_window.chat_page.open_chat(username)
    
    def save_welcome_message(self):
        text = self.welcome_input.text().strip()
        if self.profile_manager:
            self.profile_manager.update_profile({"welcome_message": text[:100]})
    
    def show_success(self, message):
        show_cyber_message(self, "Успех", f"✅ {message}", QMessageBox.Information)
    
    def show_error(self, message):
        show_cyber_message(self, "Ошибка", f"❌ {message}", QMessageBox.Critical)