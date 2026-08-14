import sys
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from gui.styles import MAIN_STYLE, COLORS

class MainWindow(QMainWindow):
    """Главное окно CyberLink"""
    
    def __init__(self, username, network, database):
        super().__init__()
        self.username = username
        self.network = network
        self.database = database
        self.current_chat = None
        
        self.init_ui()
        self.load_contacts()
        self.load_messages()
        
        # Таймер обновления
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_contacts)
        self.timer.start(5000)  # Каждые 5 секунд
        
        # Показываем приветствие
        self.statusBar().showMessage(f"🔗 CyberLink активен | Пользователь: @{self.username}")
    
    def init_ui(self):
        self.setWindowTitle(f"CyberLink - @{self.username}")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(MAIN_STYLE)
        
        # Меню
        menubar = self.menuBar()
        file_menu = menubar.addMenu("💻 Файл")
        
        exit_action = QAction("🚪 Выйти", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = menubar.addMenu("❓ Помощь")
        about_action = QAction("ℹ️ О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Левая панель (контакты)
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)
        
        # Правая панель (чат)
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel)
        
        # Устанавливаем соотношение размеров
        main_layout.setStretchFactor(left_panel, 1)
        main_layout.setStretchFactor(right_panel, 2)
    
    def create_left_panel(self):
        """Создание левой панели с контактами"""
        panel = QWidget()
        panel.setFixedWidth(320)
        panel.setStyleSheet(f"""
            background-color: {COLORS['dark_bg']};
            border-right: 2px solid {COLORS['neon_blue']};
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Заголовок с логотипом
        header = QLabel("⚡ CYBERLINK")
        header.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['neon_pink']};
            font-family: 'Consolas', monospace;
            letter-spacing: 3px;
            padding: 10px;
            border-bottom: 2px solid {COLORS['neon_blue']};
        """)
        layout.addWidget(header)
        
        # Информация о пользователе
        user_info = QLabel(f"👤 @{self.username}")
        user_info.setStyleSheet(f"""
            color: {COLORS['neon_blue']};
            font-size: 14px;
            font-weight: bold;
            padding: 5px 10px;
            background-color: {COLORS['dark_card']};
            border-radius: 8px;
        """)
        layout.addWidget(user_info)
        
        # Статус сети
        self.status_label = QLabel("🟢 Онлайн")
        self.status_label.setStyleSheet(f"""
            color: {COLORS['neon_green']};
            font-size: 12px;
            font-family: 'Consolas', monospace;
        """)
        layout.addWidget(self.status_label)
        
        # Поиск
        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 Поиск контактов...")
        search_input.textChanged.connect(self.filter_contacts)
        layout.addWidget(search_input)
        
        # Список контактов
        self.contacts_list = QListWidget()
        self.contacts_list.itemClicked.connect(self.select_contact)
        layout.addWidget(self.contacts_list)
        
        # Информация о контактах
        contact_count = QLabel("Контакты: 0")
        contact_count.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        contact_count.setObjectName("contact_count")
        layout.addWidget(contact_count)
        
        # Кнопка выхода
        logout_btn = QPushButton("🚪 Выход")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        return panel
    
    def create_right_panel(self):
        """Создание правой панели с чатом"""
        panel = QWidget()
        panel.setStyleSheet(f"background-color: #0a0a1a;")
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Заголовок чата
        self.chat_header = QFrame()
        self.chat_header.setStyleSheet(f"""
            background-color: {COLORS['dark_card']};
            border: 1px solid {COLORS['neon_blue']};
            border-radius: 10px;
            padding: 15px;
        """)
        header_layout = QHBoxLayout(self.chat_header)
        
        chat_icon = QLabel("💬")
        chat_icon.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(chat_icon)
        
        self.chat_title = QLabel("Выберите контакт для общения")
        self.chat_title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 16px;
            font-weight: bold;
        """)
        header_layout.addWidget(self.chat_title)
        
        self.online_status = QLabel("")
        self.online_status.setStyleSheet(f"""
            color: {COLORS['neon_green']};
            font-size: 12px;
            font-family: 'Consolas', monospace;
        """)
        header_layout.addWidget(self.online_status, alignment=Qt.AlignRight)
        
        layout.addWidget(self.chat_header)
        
        # Область сообщений
        self.messages_area = QTextEdit()
        self.messages_area.setReadOnly(True)
        self.messages_area.setPlaceholderText("💭 Начните диалог...")
        layout.addWidget(self.messages_area)
        
        # Панель ввода
        input_panel = QWidget()
        input_panel.setStyleSheet(f"""
            background-color: {COLORS['dark_card']};
            border: 1px solid {COLORS['neon_blue']};
            border-radius: 15px;
            padding: 5px;
        """)
        input_layout = QHBoxLayout(input_panel)
        input_layout.setSpacing(5)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("✏️ Введите сообщение...")
        self.message_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                border: none;
                color: {COLORS['text_primary']};
                padding: 10px 15px;
                font-size: 14px;
            }}
        """)
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)
        
        send_btn = QPushButton("📤")
        send_btn.setFixedSize(45, 45)
        send_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['neon_pink']}, stop:1 {COLORS['neon_purple']});
                border-radius: 22px;
                font-size: 18px;
                padding: 0px;
            }}
            QPushButton:hover {{
                box-shadow: 0 0 20px rgba(255, 45, 85, 0.3);
            }}
        """)
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        
        layout.addWidget(input_panel)
        
        return panel
    
    def load_contacts(self):
        """Загрузка контактов"""
        self.contacts_list.clear()
        contacts = self.database.get_all_contacts()
        
        # Обновляем счетчик
        contact_count = self.findChild(QLabel, "contact_count")
        if contact_count:
            contact_count.setText(f"Контакты: {len(contacts)}")
        
        for username, last_msg, last_time in contacts:
            unread = self.database.get_unread_count(username)
            
            # Создаем виджет для контакта
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(5, 5, 5, 5)
            
            # Аватар
            avatar = QLabel("👤")
            avatar.setStyleSheet(f"font-size: 20px;")
            item_layout.addWidget(avatar)
            
            # Информация
            info_layout = QVBoxLayout()
            
            name_label = QLabel(f"@{username}")
            name_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: bold;")
            info_layout.addWidget(name_label)
            
            if last_msg:
                msg_preview = last_msg[:25] + "..." if len(last_msg) > 25 else last_msg
                msg_label = QLabel(msg_preview)
                msg_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
                info_layout.addWidget(msg_label)
            
            item_layout.addLayout(info_layout)
            
            # Непрочитанные
            if unread > 0:
                badge = QLabel(str(unread))
                badge.setStyleSheet(f"""
                    background-color: {COLORS['neon_pink']};
                    color: white;
                    border-radius: 10px;
                    padding: 2px 8px;
                    font-size: 11px;
                    font-weight: bold;
                """)
                item_layout.addWidget(badge)
            
            item_widget.setLayout(item_layout)
            
            # Добавляем в список
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            item.setData(Qt.UserRole, username)
            
            self.contacts_list.addItem(item)
            self.contacts_list.setItemWidget(item, item_widget)
    
    def filter_contacts(self, text):
        """Фильтрация контактов"""
        for i in range(self.contacts_list.count()):
            item = self.contacts_list.item(i)
            widget = self.contacts_list.itemWidget(item)
            if widget:
                # Ищем лейбл с именем
                for child in widget.findChildren(QLabel):
                    if child.text().startswith("@"):
                        username = child.text()[1:]  # Убираем @
                        item.setHidden(text.lower() not in username.lower())
                        break
    
    def select_contact(self, item):
        """Выбор контакта"""
        username = item.data(Qt.UserRole)
        self.current_chat = username
        self.chat_title.setText(f"💬 Чат с @{username}")
        
        # Статус онлайн (в реальности нужно проверять через сеть)
        self.online_status.setText("🟢 Онлайн")
        
        self.load_messages(username)
        self.database.mark_as_read(username)
        self.load_contacts()
    
    def load_messages(self, username=None):
        """Загрузка сообщений"""
        if not username:
            username = self.current_chat
        
        if not username:
            return
        
        messages = self.database.get_messages_with(username)
        self.messages_area.clear()
        
        if not messages:
            self.messages_area.append(
                f"<center><i style='color: {COLORS['text_secondary']};'>💭 Нет сообщений. Начните диалог с @{username}!</i></center>"
            )
            return
        
        # Группируем по датам
        current_date = None
        
        for from_user, to_user, content, timestamp, is_read in messages:
            msg_time = datetime.fromisoformat(timestamp)
            msg_date = msg_time.strftime("%d %B %Y")
            
            # Добавляем разделитель дат
            if msg_date != current_date:
                current_date = msg_date
                self.messages_area.append(
                    f"<center><span style='color: {COLORS['text_secondary']}; font-size: 12px;'>"
                    f"─── {msg_date} ───</span></center>"
                )
            
            time_str = msg_time.strftime("%H:%M")
            
            if from_user == self.username:
                # Мои сообщения
                self.messages_area.append(f"""
                    <div style='text-align: right; margin: 5px 0;'>
                        <div style='display: inline-block; 
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {COLORS['neon_pink']}, stop:1 {COLORS['neon_purple']});
                            color: white; 
                            padding: 10px 15px; 
                            border-radius: 15px 15px 5px 15px; 
                            max-width: 70%;'>
                            {content}
                            <div style='font-size: 10px; color: #ffccdd; margin-top: 5px;'>
                                {time_str} {"" if is_read else "✓✓"}
                            </div>
                        </div>
                    </div>
                """)
            else:
                # Сообщения собеседника
                self.messages_area.append(f"""
                    <div style='text-align: left; margin: 5px 0;'>
                        <div style='display: inline-block; 
                            background: {COLORS['dark_card']};
                            border: 1px solid {COLORS['neon_blue']};
                            color: {COLORS['text_primary']}; 
                            padding: 10px 15px; 
                            border-radius: 15px 15px 15px 5px; 
                            max-width: 70%;'>
                            <b style='color: {COLORS['neon_blue']};'>@{from_user}</b><br>
                            {content}
                            <div style='font-size: 10px; color: {COLORS['text_secondary']}; margin-top: 5px;'>
                                {time_str}
                            </div>
                        </div>
                    </div>
                """)
        
        # Прокручиваем вниз
        scrollbar = self.messages_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        """Отправка сообщения"""
        if not self.current_chat:
            QMessageBox.warning(self, "Ошибка", "Выберите контакт для отправки сообщения")
            return
        
        content = self.message_input.text().strip()
        if not content:
            return
        
        # Сохраняем в локальную БД
        sync_hash = self.database.save_message(self.username, self.current_chat, content)
        self.database.update_contact(self.current_chat, content)
        
        # Отправляем через сеть
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                self.network.send_message(self.current_chat, content, sync_hash)
            )
            loop.close()
            
            self.message_input.clear()
            self.load_messages()
            self.load_contacts()
            
            self.statusBar().showMessage(f"✅ Сообщение отправлено @{self.current_chat}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось отправить сообщение: {str(e)}")
    
    def refresh_contacts(self):
        """Обновление контактов"""
        self.load_contacts()
        if self.current_chat:
            self.load_messages()
    
    def show_notification(self, title, message):
        """Показ уведомления"""
        # В будущем можно добавить системные уведомления
        self.statusBar().showMessage(f"📨 {title}: {message}", 5000)
    
    def show_about(self):
        """О программе"""
        QMessageBox.about(self, "О CyberLink",
            """
            <h1 style='color: #ff2d55;'>⚡ CyberLink</h1>
            <p><b>Версия:</b> 1.0.0</p>
            <p><b>Тип:</b> Децентрализованный P2P Мессенджер</p>
            <p><b>Особенности:</b></p>
            <ul>
                <li>🔒 Полная децентрализация</li>
                <li>📡 P2P соединения</li>
                <li>💾 Данные только на ваших устройствах</li>
                <li>🔐 Безопасная передача</li>
            </ul>
            <p style='color: #8888aa;'><i>© 2024 CyberLink Team</i></p>
            """
        )
    
    def logout(self):
        """Выход"""
        reply = QMessageBox.question(self, "Выход", 
            "Вы уверены что хотите выйти из CyberLink?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
    
    def closeEvent(self, event):
        """Закрытие окна"""
        reply = QMessageBox.question(self, "Выход", 
            "Завершить работу CyberLink?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()