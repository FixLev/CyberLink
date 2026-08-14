# gui/main_window.py
# CyberLink - Главное окно

import sys
import asyncio
import webbrowser
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from gui.styles import (
    COLORS,
    MAIN_STYLE,
    DIALOG_STYLE,
    MESSAGEBOX_STYLE,
    INPUTDIALOG_STYLE,
    BUTTON_STYLE
)


class MainWindow(QMainWindow):
    """Главное окно CyberLink"""
    
    def __init__(self, username, network, database):
        super().__init__()
        self.username = username
        self.network = network
        self.database = database
        self.current_chat = None
        self.auto_update_enabled = True
        self.is_dark_theme = True
        
        # Настройка стилей
        self.setup_dialog_style()
        
        self.init_ui()
        self.load_contacts()
        self.load_messages()
        
        # Таймер обновления
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_contacts)
        self.timer.start(5000)
        
        # Статус
        self.statusBar().showMessage(f"🔗 CyberLink активен | Пользователь: @{self.username}")
    
    def setup_dialog_style(self):
        """Настройка стиля для всех диалогов"""
        try:
            # Применяем стиль Fusion ко всему приложению
            QApplication.setStyle(QStyleFactory.create('Fusion'))
        except:
            pass
        
        # Устанавливаем тёмную палитру
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(10, 10, 26))
        palette.setColor(QPalette.WindowText, QColor(224, 224, 255))
        palette.setColor(QPalette.Base, QColor(26, 26, 58))
        palette.setColor(QPalette.AlternateBase, QColor(18, 18, 42))
        palette.setColor(QPalette.ToolTipBase, QColor(10, 10, 26))
        palette.setColor(QPalette.ToolTipText, QColor(224, 224, 255))
        palette.setColor(QPalette.Text, QColor(224, 224, 255))
        palette.setColor(QPalette.Button, QColor(26, 26, 58))
        palette.setColor(QPalette.ButtonText, QColor(224, 224, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 45, 85))
        palette.setColor(QPalette.Link, QColor(0, 212, 255))
        palette.setColor(QPalette.Highlight, QColor(255, 45, 85))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        QApplication.setPalette(palette)
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle(f"CyberLink - @{self.username}")
        self.setGeometry(100, 100, 1300, 800)
        self.setMinimumSize(1000, 600)
        self.setStyleSheet(MAIN_STYLE)
        
        # Создаем меню
        self.create_menu()
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Левая панель
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)
        
        # Правая панель
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel)
        
        # Соотношение размеров
        main_layout.setStretchFactor(left_panel, 1)
        main_layout.setStretchFactor(right_panel, 2)
    
    def create_menu(self):
        """Создание меню"""
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {COLORS['dark_bg']};
                color: {COLORS['text_primary']};
                border-bottom: 2px solid {COLORS['neon_blue']};
                padding: 5px 10px;
            }}
            QMenuBar::item {{
                padding: 8px 15px;
                border-radius: 8px;
                font-size: 13px;
            }}
            QMenuBar::item:selected {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['neon_pink']}, 
                    stop:1 {COLORS['neon_purple']});
                color: white;
            }}
            QMenu {{
                background-color: {COLORS['dark_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['neon_blue']};
                border-radius: 10px;
                padding: 8px;
            }}
            QMenu::item {{
                padding: 8px 30px;
                border-radius: 6px;
                font-size: 13px;
            }}
            QMenu::item:selected {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['neon_pink']}, 
                    stop:1 {COLORS['neon_purple']});
                color: white;
            }}
            QMenu::separator {{
                height: 1px;
                background: {COLORS['neon_blue']};
                margin: 5px 10px;
            }}
        """)
        
        # Файл
        file_menu = menubar.addMenu("📁 Файл")
        
        new_chat_action = QAction("💬 Новый чат", self)
        new_chat_action.setShortcut("Ctrl+N")
        new_chat_action.triggered.connect(self.new_chat)
        file_menu.addAction(new_chat_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Выйти", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Настройки
        settings_menu = menubar.addMenu("⚙️ Настройки")
        
        theme_action = QAction("🌙 Тёмная тема", self)
        theme_action.setCheckable(True)
        theme_action.setChecked(True)
        theme_action.triggered.connect(self.toggle_theme)
        settings_menu.addAction(theme_action)
        
        settings_menu.addSeparator()
        
        update_action = QAction("🔄 Проверить обновления", self)
        update_action.triggered.connect(self.check_updates)
        settings_menu.addAction(update_action)
        
        # Помощь
        help_menu = menubar.addMenu("❓ Помощь")
        
        about_action = QAction("ℹ️ О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        help_menu.addSeparator()
        
        github_action = QAction("🐙 GitHub", self)
        github_action.triggered.connect(self.open_github)
        help_menu.addAction(github_action)
    
    def create_left_panel(self):
        """Создание левой панели"""
        panel = QWidget()
        panel.setFixedWidth(340)
        panel.setStyleSheet(f"""
            background-color: {COLORS['dark_bg']};
            border-right: 2px solid {COLORS['neon_blue']};
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Логотип
        header = QLabel("⚡ CYBERLINK")
        header.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {COLORS['neon_pink']};
            font-family: 'Consolas', monospace;
            letter-spacing: 5px;
            padding: 12px;
            border-bottom: 2px solid {COLORS['neon_blue']};
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Информация о пользователе
        user_frame = QFrame()
        user_frame.setStyleSheet(f"""
            background-color: {COLORS['dark_card']};
            border-radius: 15px;
            padding: 12px;
            border: 1px solid {COLORS['neon_blue']};
        """)
        user_layout = QHBoxLayout(user_frame)
        user_layout.setSpacing(12)
        
        user_avatar = QLabel("👤")
        user_avatar.setStyleSheet("font-size: 32px;")
        user_layout.addWidget(user_avatar)
        
        user_info_layout = QVBoxLayout()
        user_info_layout.setSpacing(4)
        
        user_name = QLabel(f"@{self.username}")
        user_name.setStyleSheet(f"""
            color: {COLORS['neon_blue']};
            font-size: 17px;
            font-weight: bold;
        """)
        user_info_layout.addWidget(user_name)
        
        self.status_label = QLabel("🟢 Онлайн")
        self.status_label.setStyleSheet(f"""
            color: {COLORS['neon_green']};
            font-size: 12px;
            font-family: 'Consolas', monospace;
        """)
        user_info_layout.addWidget(self.status_label)
        
        user_layout.addLayout(user_info_layout)
        user_layout.addStretch()
        
        layout.addWidget(user_frame)
        
        # Поиск
        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 Поиск контактов...")
        search_input.textChanged.connect(self.filter_contacts)
        search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['dark_input']};
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['neon_blue']};
                border-radius: 12px;
                padding: 12px 18px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['neon_pink']};
                background-color: #1a1a4a;
            }}
        """)
        layout.addWidget(search_input)
        
        # Кнопки действий
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        
        new_chat_btn = QPushButton("💬 Новый чат")
        new_chat_btn.setStyleSheet(BUTTON_STYLE)
        new_chat_btn.clicked.connect(self.new_chat)
        actions_layout.addWidget(new_chat_btn)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['dark_card']};
                color: {COLORS['neon_blue']};
                border: 2px solid {COLORS['neon_blue']};
                border-radius: 12px;
                padding: 8px 12px;
                font-size: 18px;
                min-height: 36px;
                min-width: 44px;
            }}
            QPushButton:hover {{
                background: {COLORS['neon_blue']};
                color: white;
            }}
        """)
        refresh_btn.clicked.connect(self.refresh_contacts)
        actions_layout.addWidget(refresh_btn)
        
        layout.addLayout(actions_layout)
        
        # Список контактов
        self.contacts_list = QListWidget()
        self.contacts_list.itemClicked.connect(self.select_contact)
        layout.addWidget(self.contacts_list)
        
        # Счетчик контактов
        self.contact_count_label = QLabel("📊 Контактов: 0")
        self.contact_count_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 12px;
            padding: 8px;
            font-family: 'Consolas', monospace;
        """)
        layout.addWidget(self.contact_count_label)
        
        # Кнопка выхода
        logout_btn = QPushButton("🚪 Выход")
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff0044, 
                    stop:1 #cc0033);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 20px;
                font-size: 15px;
                font-weight: bold;
                min-height: 44px;
                margin-top: 5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff2266, 
                    stop:1 #ee0044);
            }}
            QPushButton:pressed {{
                background: #990022;
            }}
        """)
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        return panel
    
    def create_right_panel(self):
        """Создание правой панели с чатом"""
        panel = QWidget()
        panel.setStyleSheet(f"background-color: #0a0a1a;")
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Заголовок чата
        self.chat_header = QFrame()
        self.chat_header.setStyleSheet(f"""
            background-color: {COLORS['dark_card']};
            border: 1px solid {COLORS['neon_blue']};
            border-radius: 15px;
            padding: 15px;
        """)
        header_layout = QHBoxLayout(self.chat_header)
        header_layout.setSpacing(12)
        
        chat_avatar = QLabel("💬")
        chat_avatar.setStyleSheet("font-size: 32px;")
        header_layout.addWidget(chat_avatar)
        
        chat_info_layout = QVBoxLayout()
        chat_info_layout.setSpacing(4)
        
        self.chat_title = QLabel("Выберите контакт")
        self.chat_title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 18px;
            font-weight: bold;
        """)
        chat_info_layout.addWidget(self.chat_title)
        
        self.online_status = QLabel("🟢 Выберите собеседника")
        self.online_status.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 13px;
        """)
        chat_info_layout.addWidget(self.online_status)
        
        header_layout.addLayout(chat_info_layout)
        header_layout.addStretch()
        
        # Кнопка очистки
        clear_btn = QPushButton("🗑️")
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['text_secondary']};
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 18px;
                min-height: 36px;
                min-width: 40px;
            }}
            QPushButton:hover {{
                background: #ff0044;
                color: white;
                border-color: #ff0044;
            }}
        """)
        clear_btn.clicked.connect(self.clear_chat)
        clear_btn.setToolTip("Очистить историю чата")
        header_layout.addWidget(clear_btn)
        
        layout.addWidget(self.chat_header)
        
        # Область сообщений
        self.messages_area = QTextEdit()
        self.messages_area.setReadOnly(True)
        self.messages_area.setPlaceholderText("💭 Начните диалог...")
        layout.addWidget(self.messages_area)
        
        # Панель ввода
        input_panel = QFrame()
        input_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['dark_card']};
                border: 2px solid {COLORS['neon_blue']};
                border-radius: 15px;
                padding: 5px;
            }}
            QFrame:focus-within {{
                border-color: {COLORS['neon_pink']};
            }}
        """)
        input_layout = QHBoxLayout(input_panel)
        input_layout.setSpacing(10)
        input_layout.setContentsMargins(8, 8, 8, 8)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("✏️ Введите сообщение...")
        self.message_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                border: none;
                color: {COLORS['text_primary']};
                padding: 12px 18px;
                font-size: 15px;
            }}
            QLineEdit:focus {{
                border: none;
                outline: none;
            }}
        """)
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)
        
        send_btn = QPushButton("📤")
        send_btn.setFixedSize(55, 55)
        send_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['neon_pink']}, 
                    stop:1 {COLORS['neon_purple']});
                border-radius: 28px;
                font-size: 24px;
                padding: 0px;
                border: none;
                color: white;
                min-width: 55px;
                min-height: 55px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff4d7a, 
                    stop:1 #8b4ffc);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #cc1a44, 
                    stop:1 #6a1fcc);
            }}
        """)
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        
        layout.addWidget(input_panel)
        
        return panel
    
    # ============================================
    # МЕТОДЫ ДЛЯ ДИАЛОГОВ (ТЁМНАЯ ТЕМА)
    # ============================================
    
    def show_message_box(self, title, message, icon=QMessageBox.Information, buttons=QMessageBox.Ok):
        """Показ кастомного MessageBox с тёмной темой"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(buttons)
        msg_box.setStyleSheet(MESSAGEBOX_STYLE)
        return msg_box.exec_()
    
    def show_input_dialog(self, title, label, text=""):
        """Показ кастомного InputDialog с тёмной темой"""
        dialog = QInputDialog(self)
        dialog.setWindowTitle(title)
        dialog.setLabelText(label)
        dialog.setTextValue(text)
        dialog.setModal(True)
        dialog.setStyleSheet(INPUTDIALOG_STYLE)
        result = dialog.exec_()
        return result, dialog.textValue()
    
    # ============================================
    # ОСНОВНЫЕ МЕТОДЫ
    # ============================================
    
    def load_contacts(self):
        """Загрузка контактов"""
        self.contacts_list.clear()
        contacts = self.database.get_all_contacts()
        
        self.contact_count_label.setText(f"📊 Контактов: {len(contacts)}")
        
        if not contacts:
            empty_label = QLabel("Нет контактов\n\nНажмите \"Новый чат\"\nчтобы начать общение")
            empty_label.setStyleSheet(f"""
                color: {COLORS['text_secondary']};
                font-size: 14px;
                text-align: center;
                padding: 30px;
            """)
            empty_label.setAlignment(Qt.AlignCenter)
            
            item = QListWidgetItem()
            item.setSizeHint(empty_label.sizeHint())
            self.contacts_list.addItem(item)
            self.contacts_list.setItemWidget(item, empty_label)
            return
        
        for username, last_msg, last_time in contacts:
            unread = self.database.get_unread_count(username)
            
            item_widget = QWidget()
            item_widget.setStyleSheet("background-color: transparent;")
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(8, 8, 8, 8)
            item_layout.setSpacing(12)
            
            avatar = QLabel("👤")
            avatar.setStyleSheet("font-size: 26px;")
            item_layout.addWidget(avatar)
            
            info_layout = QVBoxLayout()
            info_layout.setSpacing(3)
            
            name_label = QLabel(f"@{username}")
            name_label.setStyleSheet(f"""
                color: {COLORS['text_primary']};
                font-weight: bold;
                font-size: 14px;
            """)
            info_layout.addWidget(name_label)
            
            if last_msg:
                msg_preview = last_msg[:35] + "..." if len(last_msg) > 35 else last_msg
                msg_label = QLabel(msg_preview)
                msg_label.setStyleSheet(f"""
                    color: {COLORS['text_secondary']};
                    font-size: 12px;
                """)
                info_layout.addWidget(msg_label)
            
            item_layout.addLayout(info_layout)
            item_layout.addStretch()
            
            if unread > 0:
                badge = QLabel(str(unread))
                badge.setStyleSheet(f"""
                    background-color: {COLORS['neon_pink']};
                    color: white;
                    border-radius: 12px;
                    padding: 3px 10px;
                    font-size: 12px;
                    font-weight: bold;
                    min-width: 20px;
                    text-align: center;
                """)
                badge.setAlignment(Qt.AlignCenter)
                item_layout.addWidget(badge)
            
            if last_time:
                try:
                    time_obj = datetime.fromisoformat(last_time)
                    time_str = time_obj.strftime("%H:%M")
                    time_label = QLabel(time_str)
                    time_label.setStyleSheet(f"""
                        color: {COLORS['text_secondary']};
                        font-size: 10px;
                        font-family: 'Consolas', monospace;
                    """)
                    item_layout.addWidget(time_label)
                except:
                    pass
            
            item_widget.setLayout(item_layout)
            
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
                for child in widget.findChildren(QLabel):
                    if child.text().startswith("@"):
                        username = child.text()[1:]
                        item.setHidden(text.lower() not in username.lower())
                        break
    
    def select_contact(self, item):
        """Выбор контакта"""
        username = item.data(Qt.UserRole)
        if not username:
            return
            
        self.current_chat = username
        self.chat_title.setText(f"💬 @{username}")
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
                f"<div style='text-align: center; padding: 50px 20px;'>"
                f"<div style='font-size: 48px; margin-bottom: 15px;'>💭</div>"
                f"<div style='color: {COLORS['text_secondary']}; font-size: 18px;'>"
                f"Нет сообщений с @{username}</div>"
                f"<div style='color: {COLORS['text_dark']}; font-size: 13px; margin-top: 8px;'>"
                f"Начните диалог прямо сейчас!</div>"
                f"</div>"
            )
            return
        
        current_date = None
        
        for from_user, to_user, content, timestamp, is_read in messages:
            try:
                msg_time = datetime.fromisoformat(timestamp)
                msg_date = msg_time.strftime("%d %B %Y")
                
                if msg_date != current_date:
                    current_date = msg_date
                    self.messages_area.append(
                        f"<div style='text-align: center; margin: 20px 0 10px 0;'>"
                        f"<span style='color: {COLORS['text_secondary']}; "
                        f"font-size: 11px; font-family: 'Consolas', monospace;"
                        f"background-color: {COLORS['dark_card']}; padding: 4px 12px; "
                        f"border-radius: 10px;'>"
                        f"─── {msg_date} ───</span>"
                        f"</div>"
                    )
                
                time_str = msg_time.strftime("%H:%M")
            except:
                time_str = timestamp[:5] if len(timestamp) > 5 else timestamp
            
            if from_user == self.username:
                self.messages_area.append(f"""
                    <div style='text-align: right; margin: 8px 0;'>
                        <div style='display: inline-block; 
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {COLORS['neon_pink']}, 
                                stop:1 {COLORS['neon_purple']});
                            color: white; 
                            padding: 12px 18px; 
                            border-radius: 18px 18px 5px 18px; 
                            max-width: 75%;
                            text-align: left;
                            font-size: 14px;
                            line-height: 1.5;'>
                            {content}
                            <div style='font-size: 10px; color: rgba(255,255,255,0.7); margin-top: 6px;'>
                                {time_str} {"" if is_read else "✓✓"}
                            </div>
                        </div>
                    </div>
                """)
            else:
                self.messages_area.append(f"""
                    <div style='text-align: left; margin: 8px 0;'>
                        <div style='display: inline-block; 
                            background: {COLORS['dark_card']};
                            border: 1px solid {COLORS['neon_blue']};
                            color: {COLORS['text_primary']}; 
                            padding: 12px 18px; 
                            border-radius: 18px 18px 18px 5px; 
                            max-width: 75%;
                            text-align: left;
                            font-size: 14px;
                            line-height: 1.5;'>
                            <b style='color: {COLORS['neon_blue']}; font-size: 13px;'>
                                @{from_user}
                            </b><br>
                            {content}
                            <div style='font-size: 10px; color: {COLORS['text_secondary']}; margin-top: 6px;'>
                                {time_str}
                            </div>
                        </div>
                    </div>
                """)
        
        scrollbar = self.messages_area.verticalScrollBar()
        QTimer.singleShot(100, lambda: scrollbar.setValue(scrollbar.maximum()))
    
    def send_message(self):
        """Отправка сообщения"""
        if not self.current_chat:
            self.show_message_box(
                "Ошибка", 
                "Выберите контакт для отправки сообщения",
                QMessageBox.Warning
            )
            return
        
        content = self.message_input.text().strip()
        if not content:
            return
        
        sync_hash = self.database.save_message(self.username, self.current_chat, content)
        self.database.update_contact(self.current_chat, content)
        
        try:
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
            self.show_message_box(
                "Ошибка", 
                f"Не удалось отправить сообщение:\n{str(e)}",
                QMessageBox.Critical
            )
    
    def refresh_contacts(self):
        """Обновление контактов"""
        self.load_contacts()
        if self.current_chat:
            self.load_messages()
    
    def show_notification(self, title, message):
        """Показ уведомления"""
        self.statusBar().showMessage(f"📨 {title}: {message}", 5000)
    
    def setup_auto_update(self, enabled):
        """Настройка автообновления"""
        self.auto_update_enabled = enabled
    
    def new_chat(self):
        """Новый чат"""
        result, username = self.show_input_dialog(
            "Новый чат",
            "Введите логин пользователя (@никнейм):"
        )
        
        if result and username:
            username = username.strip().lstrip('@')
            if not username:
                return
                
            if username == self.username:
                self.show_message_box(
                    "Ошибка", 
                    "Нельзя создать чат с самим собой!",
                    QMessageBox.Warning
                )
                return
            
            from core.user_manager import UserManager
            um = UserManager()
            if um.user_exists(username):
                self.current_chat = username
                self.chat_title.setText(f"💬 @{username}")
                self.online_status.setText("🟢 Онлайн")
                self.load_messages(username)
                self.load_contacts()
                self.statusBar().showMessage(f"💬 Чат с @{username} создан", 3000)
            else:
                self.show_message_box(
                    "Ошибка", 
                    f"Пользователь @{username} не найден!",
                    QMessageBox.Warning
                )
    
    def clear_chat(self):
        """Очистка чата"""
        if not self.current_chat:
            return
        
        result = self.show_message_box(
            "Очистка чата",
            f"Вы уверены, что хотите очистить всю историю чата с @{self.current_chat}?",
            QMessageBox.Question,
            QMessageBox.Yes | QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            self.database.clear_chat(self.current_chat)
            self.load_messages()
            self.load_contacts()
            self.statusBar().showMessage(f"🗑️ Чат с @{self.current_chat} очищен", 3000)
    
    def toggle_theme(self, checked):
        """Переключение темы"""
        self.is_dark_theme = checked
        self.statusBar().showMessage(
            f"🌙 Тема: {'Тёмная' if self.is_dark_theme else 'Светлая'}", 3000
        )
    
    def check_updates(self):
        """Проверка обновлений"""
        try:
            from updater import check_and_prompt_update
            check_and_prompt_update(self)
        except ImportError:
            self.show_message_box(
                "Обновления",
                "Функция проверки обновлений будет доступна в следующей версии.\n\n"
                "Посетите GitHub для получения последней версии:\n"
                "https://github.com/FixLev/CyberLink",
                QMessageBox.Information
            )
    
    def open_github(self):
        """Открыть GitHub"""
        webbrowser.open("https://github.com/FixLev/CyberLink")
    
    def show_about(self):
        """О программе"""
        self.show_message_box(
            "О CyberLink",
            """
            ⚡ CyberLink v1.0.0
            
            Децентрализованный P2P Мессенджер
            
            🌟 Особенности:
            • Полная децентрализация
            • P2P соединения
            • Данные только на ваших устройствах
            • Безопасная передача
            • Кроссплатформенность
            
            © 2024 CyberLink Team
            https://github.com/FixLev/CyberLink
            """,
            QMessageBox.Information
        )
    
    def logout(self):
        """Выход"""
        result = self.show_message_box(
            "Выход", 
            "Вы уверены что хотите выйти из CyberLink?",
            QMessageBox.Question,
            QMessageBox.Yes | QMessageBox.No
        )
        if result == QMessageBox.Yes:
            self.close()
    
    def closeEvent(self, event):
        """Закрытие окна"""
        result = self.show_message_box(
            "Выход", 
            "Завершить работу CyberLink?",
            QMessageBox.Question,
            QMessageBox.Yes | QMessageBox.No
        )
        if result == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()