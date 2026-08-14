#!/usr/bin/env python3
"""
CyberLink - Децентрализованный P2P Мессенджер
Версия 1.0.0
Репозиторий: https://github.com/FixLev/CyberLink
"""

import sys
import os
import asyncio
import threading
import json
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from core.database import Database
from core.network import P2PNetwork
from core.user_manager import UserManager
from core.message_sync import MessageSync
from gui.login_window import LoginWindow
from gui.main_window import MainWindow
from gui.styles import CYBERLINK_ASCII, COLORS

class CyberLinkApp:
    """Главный класс приложения CyberLink"""
    
    def __init__(self):
        # Создаем приложение Qt
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("CyberLink")
        self.app.setApplicationDisplayName("CyberLink P2P Messenger")
        self.app.setOrganizationName("CyberLink")
        
        # Устанавливаем иконку приложения
        self.set_app_icon()
        
        # Показываем ASCII арт при запуске
        self.print_banner()
        
        # Инициализация компонентов
        self.user_manager = UserManager()
        self.network = None
        self.database = None
        self.main_window = None
        self.message_sync = None
        self.config = self.load_config()
        
        # Запускаем окно входа
        self.show_login()
    
    def set_app_icon(self):
        """Установка иконки приложения"""
        try:
            # Пытаемся загрузить иконку из assets
            icon_path = Path("assets/logo.png")
            if icon_path.exists():
                icon = QIcon(str(icon_path))
                self.app.setWindowIcon(icon)
            else:
                # Используем эмодзи как иконку
                self.app.setWindowIcon(QIcon())
        except:
            pass
    
    def print_banner(self):
        """Вывод баннера в консоль"""
        print("\033[96m" + "=" * 70 + "\033[0m")
        print("\033[96m" + CYBERLINK_ASCII + "\033[0m")
        print("\033[92m" + "=" * 70 + "\033[0m")
        print("\033[93m" + "🚀 CyberLink v1.0.0 - Децентрализованный P2P Мессенджер" + "\033[0m")
        print("\033[93m" + "📦 Репозиторий: https://github.com/FixLev/CyberLink" + "\033[0m")
        print("\033[92m" + "=" * 70 + "\033[0m\n")
        
        print("\033[96m💡 Особенности:\033[0m")
        print("   🔗 Полная децентрализация (P2P)")
        print("   📱 Кроссплатформенность (Windows, Linux, macOS, Android, iOS)")
        print("   🔒 Безопасное шифрование")
        print("   🔄 Автообновление через GitHub")
        print("   🌙 Стильный киберпанк дизайн\n")
    
    def load_config(self) -> dict:
        """Загрузка конфигурации"""
        config_path = Path("config.json")
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Создаем конфиг по умолчанию
        default_config = {
            "version": "1.0.0",
            "first_run": True,
            "theme": "cyberpunk",
            "language": "ru",
            "notifications": True,
            "auto_update": True,
            "check_updates_on_start": True,
            "save_password": False,
            "port": 10000,
            "data_dir": "data",
            "logs_dir": "logs",
            "max_messages_stored": 1000,
            "sync_interval": 30,
            "bootstrap_peers": [
                "127.0.0.1:9999"
            ]
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        return default_config
    
    def show_login(self):
        """Показ окна входа"""
        self.login_window = LoginWindow(self.user_manager)
        
        # Центрируем окно
        self.center_window(self.login_window)
        
        if self.login_window.exec_() == QDialog.Accepted:
            username = self.login_window.get_username()
            if username:
                self.start_messenger(username)
            else:
                self.quit_app()
        else:
            self.quit_app()
    
    def center_window(self, window):
        """Центрирование окна на экране"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        window_geometry = window.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        window.move(window_geometry.topLeft())
    
    def start_messenger(self, username):
        """Запуск мессенджера"""
        try:
            print(f"\n\033[96m🔗 Инициализация CyberLink для @{username}...\033[0m")
            
            # Создаем папки для данных
            Path("data").mkdir(exist_ok=True)
            Path("logs").mkdir(exist_ok=True)
            
            # Инициализация БД
            self.database = Database(username)
            print("\033[92m✅ База данных инициализирована\033[0m")
            
            # Инициализация сети
            self.network = P2PNetwork(username, self.config.get('port', 10000))
            
            # Инициализация синхронизации
            self.message_sync = MessageSync(self.database, self.network)
            
            # Запускаем P2P сеть в отдельном потоке
            def run_network():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.network.start())
                    print("\033[92m✅ P2P сеть запущена\033[0m")
                    loop.run_forever()
                except Exception as e:
                    print(f"\033[91m❌ Ошибка P2P сети: {e}\033[0m")
                finally:
                    loop.close()
            
            network_thread = threading.Thread(target=run_network, daemon=True)
            network_thread.start()
            
            # Устанавливаем callback для получения сообщений
            def on_message(message):
                try:
                    if message['from'] != username:
                        # Сохраняем полученное сообщение
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
                except Exception as e:
                    print(f"⚠️ Ошибка обработки сообщения: {e}")
            
            self.network.set_message_callback(on_message)
            
            # Запускаем фоновую синхронизацию
            def run_sync():
                import time
                while True:
                    try:
                        time.sleep(self.config.get('sync_interval', 30))
                        # Синхронизация с контактами
                        contacts = self.database.get_all_contacts()
                        for contact_username, _, _ in contacts:
                            if self.network:
                                # В реальной реализации здесь была бы синхронизация
                                pass
                    except Exception as e:
                        print(f"⚠️ Ошибка синхронизации: {e}")
            
            sync_thread = threading.Thread(target=run_sync, daemon=True)
            sync_thread.start()
            
            # Запускаем главное окно
            self.main_window = MainWindow(username, self.network, self.database)
            self.main_window.setup_auto_update(self.config.get('auto_update', True))
            self.main_window.show()
            
            # Центрируем главное окно
            self.center_window(self.main_window)
            
            # Закрываем окно входа
            self.login_window.close()
            
            print(f"\033[92m✅ CyberLink успешно запущен для @{username}\033[0m")
            print(f"\033[96m💡 Версия: {self.config.get('version', '1.0.0')}\033[0m")
            print(f"\033[96m💡 Для выхода закройте главное окно\033[0m\n")
            
        except Exception as e:
            print(f"\033[91m❌ Ошибка запуска: {str(e)}\033[0m")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                None, 
                "Ошибка запуска CyberLink", 
                f"Не удалось запустить мессенджер:\n\n{str(e)}"
            )
            self.quit_app()
    
    def quit_app(self):
        """Корректное завершение приложения"""
        print("\n\033[96m👋 Завершение работы CyberLink...\033[0m")
        
        # Останавливаем сеть
        if self.network:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.network.stop())
                loop.close()
            except:
                pass
        
        # Выход из приложения
        self.app.quit()
        sys.exit(0)
    
    def run(self):
        """Запуск приложения"""
        return self.app.exec_()

if __name__ == "__main__":
    try:
        # Создаем и запускаем приложение
        app = CyberLinkApp()
        sys.exit(app.run())
    except KeyboardInterrupt:
        print("\n\n\033[93m⚠️ Приложение остановлено пользователем\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\n\033[91m❌ Критическая ошибка: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)