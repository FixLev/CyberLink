#!/usr/bin/env python3
# CyberLink - Адаптация для мобильных устройств

import os
import sys
import platform
import json
from pathlib import Path

class MobileAdapter:
    """Адаптация CyberLink для мобильных устройств"""
    
    def __init__(self):
        self.is_android = self.is_android()
        self.is_ios = self.is_ios()
        self.is_termux = self.is_termux()
        self.is_mobile = self.is_android or self.is_ios or self.is_termux
        
        self.config = self.load_config()
    
    @staticmethod
    def is_android() -> bool:
        """Проверка на Android"""
        if os.environ.get('ANDROID_ROOT'):
            return True
        
        # Проверка через build.prop
        try:
            with open('/system/build.prop', 'r') as f:
                content = f.read()
                if 'ro.build.version.release' in content:
                    return True
        except:
            pass
        
        return False
    
    @staticmethod
    def is_ios() -> bool:
        """Проверка на iOS"""
        if os.path.exists('/private/var/mobile'):
            return True
        if os.path.exists('/Applications/Pythonista.app'):
            return True
        return False
    
    @staticmethod
    def is_termux() -> bool:
        """Проверка на Termux"""
        if os.environ.get('PREFIX', '').startswith('/data/data/com.termux'):
            return True
        if os.path.exists('/data/data/com.termux'):
            return True
        return False
    
    def load_config(self) -> dict:
        """Загрузка конфигурации для мобильных устройств"""
        config_path = Path("config.json")
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Настройки по умолчанию для мобильных
        default_config = {
            "mobile_mode": True,
            "theme": "dark",
            "touch_support": True,
            "large_fonts": True,
            "small_interface": True,
            "save_bandwidth": True,
            "sync_interval": 60,  # Меньше синхронизации для экономии трафика
            "max_messages": 500,  # Меньше сообщений для экономии памяти
            "enable_notifications": True,
            "vibration": True,
            "backup_interval": 3600
        }
        
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def get_mobile_settings(self) -> dict:
        """Получение настроек для мобильных устройств"""
        if not self.is_mobile:
            return {}
        
        return {
            'screen_size': self.get_screen_size(),
            'touch_support': self.config.get('touch_support', True),
            'large_fonts': self.config.get('large_fonts', True),
            'small_interface': self.config.get('small_interface', True),
            'save_bandwidth': self.config.get('save_bandwidth', True)
        }
    
    def get_screen_size(self) -> tuple:
        """Получение размера экрана"""
        # Возвращаем стандартные значения для мобильных
        if self.is_android or self.is_termux:
            # Для Android Termux
            try:
                import subprocess
                result = subprocess.check_output(['wm', 'size']).decode()
                size = result.strip().split(': ')[1]
                width, height = map(int, size.split('x'))
                return width, height
            except:
                return 720, 1280  # Стандартное значение
        elif self.is_ios:
            return 750, 1334  # iPhone стандарт
        else:
            return 800, 600
    
    def get_mobile_styles(self) -> str:
        """Получение стилей для мобильных устройств"""
        if not self.is_mobile:
            return ""
        
        font_size = "14px" if self.config.get('large_fonts', True) else "12px"
        padding = "15px" if self.config.get('large_fonts', True) else "10px"
        
        return f"""
            /* Мобильные стили CyberLink */
            * {{
                -webkit-tap-highlight-color: transparent;
                touch-action: manipulation;
            }}
            
            QMainWindow {{
                padding: 0px !important;
                margin: 0px !important;
            }}
            
            QLineEdit {{
                font-size: {font_size};
                padding: {padding};
                min-height: 44px;
                border-radius: 22px;
            }}
            
            QPushButton {{
                font-size: {font_size};
                padding: {padding};
                min-height: 44px;
                min-width: 88px;
                border-radius: 22px;
            }}
            
            QListWidget::item {{
                padding: {padding};
                min-height: 55px;
            }}
            
            QTextEdit {{
                font-size: {font_size};
                padding: {padding};
            }}
            
            QScrollBar {{
                width: 30px;
                height: 30px;
            }}
            
            QScrollBar::handle {{
                border-radius: 15px;
                min-height: 30px;
                min-width: 30px;
            }}
            
            /* Экономия трафика - отключаем анимации */
            * {{
                transition: none !important;
                animation: none !important;
            }}
        """
    
    def setup_mobile_environment(self):
        """Настройка окружения для мобильных устройств"""
        if not self.is_mobile:
            return
        
        # Для Termux - устанавливаем дополнительные пакеты
        if self.is_termux:
            try:
                import subprocess
                print("📱 Настройка Termux...")
                
                # Устанавливаем необходимые пакеты
                packages = ['python', 'python-pip', 'openssl', 'libffi']
                subprocess.check_call(['pkg', 'install', '-y'] + packages)
                
                print("✅ Termux настроен")
            except:
                pass
        
        # Создаем папку для данных
        Path("data/mobile").mkdir(exist_ok=True, parents=True)
        Path("logs/mobile").mkdir(exist_ok=True, parents=True)
        
        print("📱 Мобильная среда настроена")
    
    def get_mobile_shortcut_command(self) -> str:
        """Получение команды для запуска на мобильных"""
        if self.is_termux:
            return "cyberlink"
        elif self.is_android:
            return "python3 run.py"
        elif self.is_ios:
            return "pythonista run.py"
        return "python3 run.py"

# Утилита для быстрой проверки
if __name__ == "__main__":
    mobile = MobileAdapter()
    print(f"📱 Мобильное устройство: {mobile.is_mobile}")
    print(f"   Android: {mobile.is_android}")
    print(f"   iOS: {mobile.is_ios}")
    print(f"   Termux: {mobile.is_termux}")
    print(f"   Настройки: {mobile.config}")
    print(f"   Команда запуска: {mobile.get_mobile_shortcut_command()}")