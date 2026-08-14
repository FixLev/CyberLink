#!/usr/bin/env python3
"""
CyberLink - Децентрализованный P2P Мессенджер
Версия 1.0.0
"""

import sys
import asyncio
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from core.database import Database
from core.network import P2PNetwork
from core.user_manager import UserManager
from gui.login_window import LoginWindow
from gui.main_window import MainWindow
from gui.styles import CYBERLINK_ASCII

class CyberLinkApp:
    """Главный класс приложения CyberLink"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("CyberLink")
        self.app.setApplicationDisplayName("CyberLink P2P Messenger")
        
        # Устанавливаем иконку приложения (опционально)
        self.app.setWindowIcon(QIcon())
        
        # Показываем ASCII арт при запуске
        print("\033[96m" + CYBERLINK_ASCII + "\033[0m")
        print("\033[92m" + "="*60 + "\033[0m")
        print("\033[93m" + "🚀 CyberLink v1.0.0 - Децентрализованный P2P Мессенджер" + "\033[0m")
        print("\033[92m" + "="*60 + "\033[0m\n")
        
        self.user_manager = UserManager()
        self.network = None
        self.database = None
        self.main_window = None
        
        # Запускаем окно входа
        self.show_login()
    
    def show_login(self):
        """Показ окна входа"""
        self.login_window = LoginWindow(self.user_manager)
        if self.login_window.exec_() == QDialog.Accepted:
            username = self.login_window.get_username()
            self.start_messenger(username)
        else:
            print("\033[91m" + "👋 Выход из CyberLink" + "\033[0m")
            sys.exit()
    
    def start_messenger(self, username):
        """Запуск мессенджера"""
        try:
            print(f"\033[96m🔗 Инициализация CyberLink для @{username}...\033[0m")
            
            # Инициализация БД
            self.database = Database(username)
            print("\033[92m✅ База данных инициализирована\033[0m")
            
            # Инициализация сети
            self.network = P2PNetwork(username)
            
            # Запускаем P2P сеть в отдельном потоке
            def run_network():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.network.start())
                loop.run_forever()
            
            network_thread = threading.Thread(target=run_network, daemon=True)
            network_thread.start()
            print("\033[92m✅ P2P сеть запущена\033[0m")
            
            # Устанавливаем callback для получения сообщений
            def on_message(message):
                # Сохраняем полученное сообщение
                if message['from'] != username:  # Не сохраняем свои сообщения
                    self.database.save_message(
                        message['from'],
                        message['to'],
                        message['content'],
                        message.get('sync_hash')
                    )
                    self.database.update_contact(message['from'], message['content'])
                    
                    # Обновляем UI
                    if self.main_window:
                        self.main_window.refresh_contacts()
                        if self.main_window.current_chat == message['from']:
                            self.main_window.load_messages()
                        
                        # Всплывающее уведомление
                        if message['from'] != self.main_window.current_chat:
                            self.main_window.show_notification(
                                f"📨 Новое сообщение от @{message['from']}",
                                message['content'][:50] + "..."
                            )
            
            self.network.set_message_callback(on_message)
            
            # Запускаем главное окно
            self.main_window = MainWindow(username, self.network, self.database)
            self.main_window.show()
            
            # Закрываем окно входа
            self.login_window.close()
            
            print(f"\033[92m✅ CyberLink успешно запущен для @{username}\033[0m")
            print("\033[96m💡 Для выхода закройте главное окно\033[0m\n")
            
        except Exception as e:
            print(f"\033[91m❌ Ошибка запуска: {str(e)}\033[0m")
            QMessageBox.critical(None, "Ошибка", f"Не удалось запустить CyberLink: {str(e)}")
            sys.exit()

if __name__ == "__main__":
    app = CyberLinkApp()
    sys.exit(app.app.exec_())
