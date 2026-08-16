#!/usr/bin/env python3
"""
CyberLink - Космический P2P Мессенджер
"""

import sys
import os
import warnings
import json
from pathlib import Path

warnings.filterwarnings("ignore")

# ===== ФИКС ДЛЯ QT НА WINDOWS =====
if sys.platform == 'win32':
    try:
        import PyQt5
        qt_path = os.path.dirname(PyQt5.__file__)
        plugin_path = os.path.join(qt_path, 'Qt5', 'plugins')
        if os.path.exists(plugin_path):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
    except:
        pass

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

from PyQt5.QtGui import QFontDatabase

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.views.main_view import MainView
from src.views.login_view import LoginView
from src.core.user_manager import UserManager
from src.core.network import P2PNetwork
from src.core.encrypted_storage import EncryptedStorage
from src.core.friends_manager import FriendsManager
from src.widgets.custom_cursor_widget import CustomCursorWidget


def load_fonts():
    """Загрузка шрифтов"""
    fonts_dir = Path("assets/fonts")
    if not fonts_dir.exists():
        fonts_dir = Path(r"C:\CyberLink\assets\fonts")
    if not fonts_dir.exists():
        return
    font_files = []
    for ext in ['*.ttf', '*.otf']:
        font_files.extend(list(fonts_dir.rglob(ext)))
    for font_file in font_files:
        try:
            QFontDatabase.addApplicationFont(str(font_file))
        except:
            pass


def migrate_old_data(username: str):
    """Перенос старых данных из папки с @ в папку без @"""
    try:
        old_dir = Path("data") / "users" / f"@{username}"
        new_dir = Path("data") / "users" / username
        
        if old_dir.exists() and not new_dir.exists():
            print(f"📦 Перенос данных из {old_dir} в {new_dir}")
            import shutil
            shutil.copytree(old_dir, new_dir)
            # После переноса можно удалить старую папку
            # shutil.rmtree(old_dir)
            return True
        
        # Если новая папка уже существует, удаляем старую
        if old_dir.exists() and new_dir.exists():
            print(f"🗑️ Удаляем старую папку с @: {old_dir}")
            import shutil
            shutil.rmtree(old_dir)
            return True
            
        return False
    except Exception as e:
        print(f"⚠️ Ошибка миграции данных: {e}")
        return False


class CyberLinkApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("CyberLink")
        self.app.setOverrideCursor(Qt.BlankCursor)
        load_fonts()
        
        self.cursor = None
        self.main_window = None
        self.network = None
        self.friends_manager = None
        self.session_file = Path("data/session.json")
        
        # Создаём папку data если её нет
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Пытаемся загрузить сессию (автовход)
        if self._try_auto_login():
            return
        
        # Если автовход не удался - показываем окно входа
        self.show_login()
    
    def _try_auto_login(self) -> bool:
        """Попытка автоматического входа"""
        if not self.session_file.exists():
            return False
        
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            username = data.get('username')
            password = data.get('password')
            
            if username and password:
                # Проверяем, существует ли пользователь
                user_manager = UserManager()
                if user_manager.user_exists(username):
                    print(f"🔄 Автовход для {username}...")
                    self.start_messenger(username, password, auto_login=True)
                    return True
        except Exception as e:
            print(f"⚠️ Ошибка автовхода: {e}")
        
        return False
    
    def _save_session(self, username: str, password: str):
        """Сохранение сессии для автовхода"""
        try:
            self.session_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'username': username,
                    'password': password,
                    'saved_at': str(__import__('time').time())
                }, f, indent=2, ensure_ascii=False)
            print(f"💾 Сессия сохранена для {username}")
        except Exception as e:
            print(f"⚠️ Ошибка сохранения сессии: {e}")
    
    def show_login(self):
        """Показ окна входа"""
        self.login_view = LoginView()
        if self.login_view.exec_():
            username = self.login_view.get_username()
            password = self.login_view.get_password()
            if username and password:
                self._save_session(username, password)
                self.start_messenger(username, password)
            else:
                sys.exit()
        else:
            sys.exit()
    
    def start_messenger(self, username: str, password: str, auto_login: bool = False):
        """Запуск главного окна"""
        try:
            print(f"🚀 Запуск мессенджера для {username}")
            
            # Мигрируем старые данные из папки с @
            migrate_old_data(username)
            
            # Создаём зашифрованное хранилище (БЕЗ @)
            storage = EncryptedStorage(username, password)
            
            # Запускаем P2P сеть
            self.network = P2PNetwork(username)
            
            # Создаём менеджер друзей
            self.friends_manager = FriendsManager(username, storage, self.network)
            
            # Создаём главное окно с передачей всех данных
            self.main_window = MainView(
                username=username,
                password=password,
                network=self.network,
                friends_manager=self.friends_manager,
                storage=storage
            )
            self.main_window.show()
            
            # Создаём кастомный курсор
            try:
                self.cursor = CustomCursorWidget(self.main_window)
                self.cursor.raise_()
                self.main_window.set_cursor_widget(self.cursor)
            except Exception as e:
                print(f"⚠️ Ошибка курсора: {e}")
                self.app.restoreOverrideCursor()
            
            # Закрываем окно входа если это не автовход
            if not auto_login and hasattr(self, 'login_view'):
                self.login_view.close()
            
        except Exception as e:
            print(f"❌ Ошибка запуска: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def run(self):
        return self.app.exec_()


if __name__ == "__main__":
    app = CyberLinkApp()
    sys.exit(app.run())