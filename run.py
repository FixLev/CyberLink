#!/usr/bin/env python3
# CyberLink - Автоматический установщик и запускатор

# run.py - добавьте в самое начало
import sys
import os

# Проверяем, что QApplication создан
if 'QT_QPA_PLATFORM_PLUGIN_PATH' not in os.environ:
    # Устанавливаем путь к плагинам Qt
    try:
        import PyQt5
        qt_path = os.path.dirname(PyQt5.__file__)
        plugin_path = os.path.join(qt_path, 'Qt5', 'plugins')
        if os.path.exists(plugin_path):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
    except:
        pass
# Фикс для Qt на Windows
if sys.platform == 'win32':
    try:
        import PyQt5
        qt_path = os.path.dirname(PyQt5.__file__)
        plugin_path = os.path.join(qt_path, 'Qt5', 'plugins')
        if os.path.exists(plugin_path):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
    except:
        pass

import subprocess
import platform
import importlib
import json
import shutil
from pathlib import Path

class CyberLinkInstaller:
    """Автоматическая установка и запуск CyberLink"""
    
    def __init__(self):
        self.required_packages = [
            'PyQt5',
            'kademlia',
            'aiohttp',
            'pycryptodome'
        ]
        
        self.optional_packages = [
            'Pillow',
            'qdarkstyle',
            'plyer'
        ]
        
        self.is_mobile = self.check_mobile_platform()
    
    def check_mobile_platform(self) -> bool:
        """Проверка мобильной платформы"""
        system = platform.system().lower()
        if 'android' in system or os.path.exists('/data/data/com.termux'):
            return True
        if 'ios' in system or os.path.exists('/private/var/mobile'):
            return True
        return False
    
    def print_banner(self):
        """Вывод баннера"""
        banner = """
   ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██╗     ██╗███╗   ██╗██╗  ██╗
  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██║     ██║████╗  ██║██║ ██╔╝
  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██║     ██║██╔██╗ ██║█████╔╝ 
  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██║     ██║██║╚██╗██║██╔═██╗ 
  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║███████╗██║██║ ╚████║██║  ██╗
   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
        """
        print("\033[96m" + "=" * 70 + "\033[0m")
        print("\033[96m" + banner + "\033[0m")
        print("\033[92m" + "=" * 70 + "\033[0m")
        print("\033[93m" + "🚀 CyberLink v1.0.0 - Децентрализованный P2P Мессенджер" + "\033[0m")
        print("\033[93m" + "📦 Репозиторий: https://github.com/FixLev/CyberLink" + "\033[0m")
        print("\033[92m" + "=" * 70 + "\033[0m\n")
    
    def check_python_version(self):
        """Проверка версии Python"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"\033[91m❌ Требуется Python 3.8 или выше! (у вас {version.major}.{version.minor})\033[0m")
            return False
        print(f"\033[92m✅ Python {version.major}.{version.minor}.{version.micro} - OK\033[0m")
        return True
    
    def check_and_install_package(self, package_name):
        """Проверка и установка пакета"""
        try:
            importlib.import_module(package_name)
            print(f"\033[92m✅ {package_name} уже установлен\033[0m")
            return True
        except ImportError:
            print(f"\033[93m📦 Устанавливаю {package_name}...\033[0m")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                print(f"\033[92m✅ {package_name} установлен успешно\033[0m")
                return True
            except subprocess.CalledProcessError:
                print(f"\033[91m❌ Не удалось установить {package_name}\033[0m")
                return False
    
    def install_requirements(self):
        """Установка зависимостей"""
        print("\n" + "=" * 50)
        print("\033[94m📦 Проверка и установка зависимостей...\033[0m")
        print("=" * 50)
        
        for package in self.required_packages:
            if not self.check_and_install_package(package):
                return False
        
        print("\n\033[94m📦 Дополнительные пакеты:\033[0m")
        for package in self.optional_packages:
            self.check_and_install_package(package)
        
        return True
    
    def create_data_dirs(self):
        """Создание папок"""
        directories = ['data', 'logs', 'temp', 'profiles']
        for dir_name in directories:
            Path(dir_name).mkdir(exist_ok=True)
            print(f"\033[92m✅ Создана папка: {dir_name}/\033[0m")
    
    def create_config(self):
        """Создание конфига"""
        config_path = Path("config.json")
        if not config_path.exists():
            default_config = {
                "version": "1.0.0",
                "first_run": True,
                "theme": "cyberpunk",
                "language": "ru",
                "notifications": True,
                "auto_update": False,  # Отключаем автообновление
                "check_updates_on_start": False,  # Отключаем проверку
                "save_password": False,
                "port": 10000,
                "data_dir": "data",
                "logs_dir": "logs",
                "max_messages_stored": 1000,
                "sync_interval": 30
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print("\033[92m✅ Создан файл конфигурации: config.json\033[0m")
            return default_config
        else:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def check_for_updates(self):
        """Проверка обновлений"""
        print("\n" + "=" * 50)
        print("\033[94m🔄 Проверка обновлений...\033[0m")
        print("=" * 50)
        
        try:
            import urllib.request
            url = "https://api.github.com/repos/FixLev/CyberLink/releases/latest"
            req = urllib.request.Request(url, headers={'User-Agent': 'CyberLink'})
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get('tag_name', 'v1.0.0').replace('v', '')
                
                with open('version.txt', 'r') as f:
                    current_version = f.read().strip()
                
                if latest_version > current_version:
                    print(f"\033[93m⚠️ Новая версия: {latest_version} (текущая: {current_version})\033[0m")
                else:
                    print(f"\033[92m✅ У вас последняя версия: {current_version}\033[0m")
        except Exception as e:
            print(f"\033[91m⚠️ Не удалось проверить обновления: {e}\033[0m")
    
    def run_main(self):
        """Запуск приложения"""
        print("\n" + "=" * 50)
        print("\033[94m🚀 Запуск CyberLink...\033[0m")
        print("=" * 50 + "\n")
        
        try:
            # Добавляем путь к проекту
            sys.path.insert(0, os.getcwd())
            
            from main import CyberLinkApp
            app = CyberLinkApp()
            sys.exit(app.run())
        except ImportError as e:
            print(f"\033[91m❌ Ошибка импорта: {e}\033[0m")
            print("\033[93m💡 Проверьте структуру файлов:\033[0m")
            print("   - main.py должен быть в корне")
            print("   - Папки core/ и gui/ должны существовать")
            sys.exit(1)
        except Exception as e:
            print(f"\033[91m❌ Ошибка: {e}\033[0m")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def main(self):
        """Основной процесс"""
        self.print_banner()
        
        if not self.check_python_version():
            sys.exit(1)
        
        self.create_data_dirs()
        self.create_config()
        
        if not self.install_requirements():
            print("\033[91m❌ Ошибка установки зависимостей\033[0m")
            sys.exit(1)
        
        self.check_for_updates()
        self.run_main()

if __name__ == "__main__":
    installer = CyberLinkInstaller()
    installer.main()