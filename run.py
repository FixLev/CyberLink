#!/usr/bin/env python3
"""
CyberLink - Космический P2P Мессенджер
"""

import sys
import os
import warnings
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

# Устанавливаем DPI scaling ДО создания QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.views.main_view import MainView
from src.views.login_view import LoginView
from src.core.user_manager import UserManager


def load_fonts():
    """Загрузка шрифтов из папки assets/fonts/"""
    fonts_dir = Path("assets/fonts")
    
    if not fonts_dir.exists():
        fonts_dir = Path(r"C:\CyberLink\assets\fonts")
    
    print(f"🔍 Поиск шрифтов в: {fonts_dir}")
    
    if not fonts_dir.exists():
        print("❌ Папка со шрифтами не найдена!")
        return
    
    font_files = []
    for ext in ['*.ttf', '*.otf']:
        font_files.extend(list(fonts_dir.rglob(ext)))
    
    if not font_files:
        print("❌ В папке нет файлов шрифтов!")
        return
    
    print(f"📦 Найдено файлов шрифтов: {len(font_files)}")
    
    loaded = []
    for font_file in font_files:
        try:
            font_id = QFontDatabase.addApplicationFont(str(font_file))
            if font_id != -1:
                loaded.append(font_file.name)
                print(f"   ✅ {font_file.name}")
            else:
                print(f"   ⚠️ Не удалось загрузить: {font_file.name}")
        except Exception as e:
            print(f"   ❌ Ошибка: {font_file.name} - {e}")
    
    print(f"✅ Загружено шрифтов: {len(loaded)}")


class CyberLinkApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("CyberLink")
        
        # ===== ГЛОБАЛЬНОЕ СГЛАЖИВАНИЕ =====
        # Включаем сглаживание для всего приложения
        self.app.setStyleSheet("""
            * {
                font-smooth: always;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }
        """)
        
        # Загружаем шрифты
        load_fonts()
        
        self.show_login()
    
    def show_login(self):
        self.login_view = LoginView()
        if self.login_view.exec_():
            username = self.login_view.get_username()
            self.start_messenger(username)
        else:
            sys.exit()
    
    def start_messenger(self, username):
        from src.core.database import Database
        from src.core.network import P2PNetwork
        
        self.database = Database(username)
        self.network = P2PNetwork(username)
        
        self.main_window = MainView(username, self.network, self.database)
        self.main_window.show()
        self.login_view.close()
    
    def run(self):
        return self.app.exec_()


if __name__ == "__main__":
    app = CyberLinkApp()
    sys.exit(app.run())