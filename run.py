#!/usr/bin/env python3
# CyberLink - Автоматический установщик и запускатор

import os
import sys
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
            'Pillow',  # Для работы с изображениями
            'qdarkstyle',  # Темная тема
            'plyer'  # Для уведомлений
        ]
        
        self.is_mobile = self.check_mobile_platform()
        self.venv_path = Path("venv") if not self.is_mobile else None
    
    def check_mobile_platform(self) -> bool:
        """Проверка, запущено ли на мобильном устройстве"""
        # Проверяем по платформе и окружению
        system = platform.system().lower()
        
        # Android терминал (Termux)
        if 'android' in system or os.path.exists('/data/data/com.termux'):
            return True
        
        # iOS (через Pythonista или другие среды)
        if 'ios' in system or os.path.exists('/private/var/mobile'):
            return True
        
        # Проверяем переменные окружения
        if os.environ.get('PREFIX', '').startswith('/data/data/com.termux'):
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
        print("\033[96m" + banner + "\033[0m")
        print("\033[93m" + "=" * 60 + "\033[0m")
        print("\033[92m" + "🚀 CyberLink - Децентрализованный P2P Мессенджер" + "\033[0m")
        print("\033[92m" + "📱 Версия для мобильных устройств" + "\033[0m" if self.is_mobile else "")
        print("\033[93m" + "=" * 60 + "\033[0m\n")
    
    def check_python_version(self):
        """Проверка версии Python"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("\033[91m❌ Требуется Python 3.8 или выше!\033[0m")
            print(f"   Ваша версия: {version.major}.{version.minor}")
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
                # Учет зависимостей для разных платформ
                if self.is_mobile:
                    # Для мобильных версий используем pip с ограничениями
                    cmd = [sys.executable, "-m", "pip", "install", "--user", package_name]
                else:
                    cmd = [sys.executable, "-m", "pip", "install", package_name]
                
                subprocess.check_call(cmd)
                print(f"\033[92m✅ {package_name} установлен успешно\033[0m")
                return True
            except subprocess.CalledProcessError:
                print(f"\033[91m❌ Не удалось установить {package_name}\033[0m")
                return False
    
    def install_requirements(self):
        """Установка всех зависимостей"""
        print("\n" + "=" * 50)
        print("\033[94m📦 Проверка и установка зависимостей...\033[0m")
        print("=" * 50)
        
        # Основные пакеты
        for package in self.required_packages:
            if not self.check_and_install_package(package):
                return False
        
        # Опциональные пакеты
        print("\n\033[94m📦 Дополнительные пакеты:\033[0m")
        for package in self.optional_packages:
            self.check_and_install_package(package)
        
        return True
    
    def create_data_dirs(self):
        """Создание необходимых директорий"""
        directories = ['data', 'logs', 'temp', 'profiles']
        for dir_name in directories:
            Path(dir_name).mkdir(exist_ok=True)
            print(f"\033[92m✅ Создана папка: {dir_name}/\033[0m")
    
    def create_config(self):
        """Создание файла конфигурации"""
        config_path = Path("config.json")
        if not config_path.exists():
            default_config = {
                "version": "1.0.0",
                "first_run": True,
                "theme": "cyberpunk",
                "language": "ru",
                "mobile_mode": self.is_mobile,
                "notifications": True,
                "auto_update": True,
                "check_updates_on_start": True,
                "save_password": False,
                "port": 10000,
                "bootstrap_peers": [
                    "127.0.0.1:9999"
                ],
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
    
    def create_mobile_shortcut(self):
        """Создание ярлыка для мобильных устройств"""
        if not self.is_mobile:
            return
        
        # Создаем скрипт для Termux
        if os.path.exists('/data/data/com.termux'):
            script_path = Path("~/../usr/bin/cyberlink").expanduser()
            script_content = f'''#!/data/data/com.termux/files/usr/bin/bash
cd {os.getcwd()}
python3 run.py "$@"
'''
            with open(script_path, 'w') as f:
                f.write(script_content)
            os.chmod(script_path, 0o755)
            print("\033[92m✅ Создан ярлык 'cyberlink' для Termux\033[0m")
            print("\033[96m💡 Теперь можно запускать командой: cyberlink\033[0m")
    
    def check_for_updates(self):
        """Проверка обновлений с GitHub"""
        print("\n" + "=" * 50)
        print("\033[94m🔄 Проверка обновлений...\033[0m")
        print("=" * 50)
        
        try:
            import urllib.request
            import json
            
            # Получаем информацию о последней версии с GitHub
            url = "https://api.github.com/repos/cyberlink/cyberlink/releases/latest"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'CyberLink'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get('tag_name', 'v1.0.0').replace('v', '')
                
                # Читаем текущую версию
                with open('version.txt', 'r') as f:
                    current_version = f.read().strip()
                
                if latest_version > current_version:
                    print(f"\033[93m⚠️ Новая версия доступна: {latest_version}\033[0m")
                    print(f"\033[93m   Текущая версия: {current_version}\033[0m")
                    
                    # Спрашиваем об обновлении
                    response = input("\n\033[96mХотите обновить CyberLink? (y/N): \033[0m")
                    if response.lower() == 'y':
                        self.update_from_github()
                        return True
                else:
                    print(f"\033[92m✅ У вас последняя версия: {current_version}\033[0m")
        except Exception as e:
            print(f"\033[91m⚠️ Не удалось проверить обновления: {e}\033[0m")
            print("\033[93m💡 Обновления можно проверить позже через меню 'Помощь' → 'Проверить обновления'\033[0m")
        
        return False
    
    def update_from_github(self):
        """Обновление с GitHub"""
        print("\n\033[93m⏳ Загрузка обновления...\033[0m")
        
        try:
            import zipfile
            import urllib.request
            import tempfile
            
            # Скачиваем архив с GitHub
            url = "https://github.com/cyberlink/cyberlink/archive/main.zip"
            zip_path = Path(tempfile.gettempdir()) / "cyberlink_update.zip"
            
            urllib.request.urlretrieve(url, zip_path)
            
            # Распаковываем во временную папку
            extract_path = Path(tempfile.gettempdir()) / "cyberlink_update"
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # Копируем новые файлы
            source_dir = extract_path / "cyberlink-main"
            for file_path in source_dir.iterdir():
                if file_path.is_file():
                    shutil.copy2(file_path, Path.cwd())
                elif file_path.is_dir() and file_path.name not in ['data', 'logs', '__pycache__']:
                    shutil.copytree(file_path, Path.cwd() / file_path.name, dirs_exist_ok=True)
            
            print("\033[92m✅ Обновление установлено!\033[0m")
            print("\033[93m⚠️ Для применения обновления перезапустите CyberLink\033[0m")
            
            # Очистка
            shutil.rmtree(extract_path)
            zip_path.unlink()
            
            return True
        except Exception as e:
            print(f"\033[91m❌ Ошибка обновления: {e}\033[0m")
            return False
    
    def run_main(self):
        """Запуск основного приложения"""
        print("\n" + "=" * 50)
        print("\033[94m🚀 Запуск CyberLink...\033[0m")
        print("=" * 50 + "\n")
        
        try:
            # Импортируем и запускаем main
            from main import CyberLinkApp
            app = CyberLinkApp()
            sys.exit(app.app.exec_())
        except ImportError as e:
            print(f"\033[91m❌ Ошибка импорта модуля: {e}\033[0m")
            print("\033[93m💡 Попробуйте переустановить зависимости:\033[0m")
            print("   python3 -m pip install -r requirements.txt")
            sys.exit(1)
        except Exception as e:
            print(f"\033[91m❌ Критическая ошибка: {e}\033[0m")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def main(self):
        """Основной процесс"""
        self.print_banner()
        
        # Проверяем Python
        if not self.check_python_version():
            sys.exit(1)
        
        # Создаем папки
        self.create_data_dirs()
        
        # Создаем конфиг
        config = self.create_config()
        
        # Устанавливаем зависимости
        if not self.install_requirements():
            print("\033[91m❌ Ошибка установки зависимостей\033[0m")
            print("\033[93m💡 Попробуйте установить вручную:\033[0m")
            print("   pip install -r requirements.txt")
            sys.exit(1)
        
        # Создаем ярлык для мобильных
        self.create_mobile_shortcut()
        
        # Проверяем обновления
        if config.get('check_updates_on_start', True):
            self.check_for_updates()
        
        # Запускаем приложение
        self.run_main()

if __name__ == "__main__":
    installer = CyberLinkInstaller()
    installer.main()