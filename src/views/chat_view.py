# src/views/chat_view.py
# Страница чатов

import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ChatView(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.current_chat = None
        self.friends_manager = None
        self.network = None
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Заголовок
        header = QFrame()
        header.setFixedHeight(50)
        header.setStyleSheet("border-bottom: 1px solid rgba(79, 195, 247, 0.06);")
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        self.chat_info = QLabel("💬 Чаты")
        self.chat_info.setStyleSheet("font-size: 16px; font-weight: bold; color: #f5f5f5; font-family: 'TT Mussels', 'Arial', sans-serif;")
        header_layout.addWidget(self.chat_info)
        
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        # Область сообщений
        self.messages_area = QTextEdit()
        self.messages_area.setReadOnly(True)
        self.messages_area.setStyleSheet("""
            QTextEdit {
                background: transparent;
                color: #f5f5f5;
                border: none;
                padding: 15px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
                font-size: 15px;
                line-height: 1.6;
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
        self.messages_area.setPlaceholderText("💫 Выберите чат, чтобы начать общение")
        layout.addWidget(self.messages_area)
        
        # Поле ввода
        input_container = QFrame()
        input_container.setFixedHeight(56)
        input_container.setStyleSheet("border-top: 1px solid rgba(79, 195, 247, 0.06);")
        
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(15, 8, 15, 8)
        input_layout.setSpacing(8)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите сообщение...")
        self.input_field.setEnabled(False)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(30, 30, 48, 0.4);
                color: #f5f5f5;
                border: 1px solid rgba(79, 195, 247, 0.08);
                border-radius: 20px;
                padding: 10px 16px;
                font-size: 15px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
            }
            QLineEdit:focus {
                border-color: rgba(79, 195, 247, 0.25);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.25);
            }
            QLineEdit:disabled {
                color: rgba(255, 255, 255, 0.3);
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        self.send_btn = QPushButton("📤")
        self.send_btn.setFixedSize(36, 36)
        self.send_btn.setEnabled(False)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: rgba(79, 195, 247, 0.15);
                color: #4fc3f7;
                border: none;
                border-radius: 18px;
                font-size: 18px;
            }
            QPushButton:hover {
                background: rgba(79, 195, 247, 0.25);
            }
            QPushButton:disabled {
                background: rgba(79, 195, 247, 0.05);
                color: rgba(79, 195, 247, 0.3);
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        
        layout.addWidget(input_container)
    
    def set_managers(self, friends_manager, network):
        self.friends_manager = friends_manager
        self.network = network
        
        if network:
            network.message_received.connect(self.on_message_received)
    
    def open_chat(self, friend_id):
        self.current_chat = friend_id
        
        display_name = self.friends_manager.get_friend_display_name(friend_id) if self.friends_manager else friend_id
        self.chat_info.setText(f"💬 {display_name}")
        
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.input_field.setFocus()
    
    def send_message(self):
        if not self.current_chat or not self.network:
            return
        
        text = self.input_field.text().strip()
        if not text:
            return
        
        message = {
            'id': f"{int(time.time())}_{self.username}",
            'sender': self.username,
            'content': text,
            'timestamp': time.time(),
            'type': 'text'
        }
        
        if self.friends_manager:
            self.friends_manager.save_chat_history(self.current_chat, message)
        
        self._append_message(message)
        self._scroll_to_bottom()
        
        chat_id = self._get_chat_id(self.current_chat)
        self.network.send_message(chat_id, message)
        
        self.input_field.clear()
    
    def _append_message(self, message):
        sender = message.get('sender', '')
        content = message.get('content', '')
        timestamp = message.get('timestamp', 0)
        
        time_str = QDateTime.fromSecsSinceEpoch(int(timestamp)).toString("HH:mm")
        is_own = sender == self.username
        
        color = "#4fc3f7" if is_own else "#f5f5f5"
        align = "right" if is_own else "left"
        bg = "rgba(79, 195, 247, 0.1)" if is_own else "rgba(255, 255, 255, 0.05)"
        name = "Вы" if is_own else sender
        
        html = f'''
        <div style="text-align: {align}; margin: 6px 0;">
            <div style="display: inline-block; 
                        background: {bg}; 
                        border-radius: 10px; 
                        padding: 6px 12px; 
                        max-width: 70%;
                        text-align: left;">
                <div style="color: {color}; font-size: 14px; word-wrap: break-word;">
                    {content}
                </div>
                <div style="color: #666688; font-size: 10px; margin-top: 2px;">
                    {name} • {time_str}
                </div>
            </div>
        </div>
        '''
        self.messages_area.insertHtml(html)
    
    def _scroll_to_bottom(self):
        scroll = self.messages_area.verticalScrollBar()
        scroll.setValue(scroll.maximum())
    
    def on_message_received(self, chat_id, message):
        if not self.current_chat:
            return
        
        users = chat_id.split('_')
        friend_id = users[0] if users[1] == self.username else users[1]
        
        if friend_id == self.current_chat:
            self._append_message(message)
            self._scroll_to_bottom()
    
    def _get_chat_id(self, friend_id):
        users = sorted([self.username, friend_id])
        return f"{users[0]}_{users[1]}"