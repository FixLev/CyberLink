#!/usr/bin/env python3
# CyberLink - Система автообновления

import os
import sys
import json
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from datetime import datetime
import threading
import queue

class CyberLinkUpdater:
    """Система автообновления CyberLink"""
    
    def __init__(self):
        self.config_path = Path("config.json")
        self.version_file = Path("version.txt")
        self.repo_url = "https://api.github.com/repos/FixLev/CyberLink"
        self.update_queue = queue.Queue()
        
        # Создаем версионный файл
        if not self.version_file.exists():
            with open(self.version_file, 'w') as f:
                f.write("1.0.0")
        
        self.current_version = self.get_current_version()
        self.load_config()
    
    def load_config(self):
        """Загрузка конфигурации"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"auto_update": True}
    
    def get_current_version(self) -> str:
        """Получение текущей версии"""
        with open(self.version_file, 'r') as f:
            return f.read().strip()
    
    def check_for_updates(self, silent: bool = False) -> dict:
        """Проверка наличия обновлений"""
        try:
            # Запрос к GitHub API
            url = f"{self.repo_url}/releases/latest"
            req = urllib.request.Request(url, headers={'User-Agent': 'CyberLink'})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                latest_version = data.get('tag_name', '').replace('v', '')
                download_url = data.get('zipball_url', '')
                release_notes = data.get('body', 'Нет описания изменений')
                
                return {
                    'current': self.current_version,
                    'latest': latest_version,
                    'download_url': download_url,
                    'release_notes': release_notes,
                    'has_update': latest_version > self.current_version
                }
        except Exception as e:
            if not silent:
                print(f"⚠️ Не удалось проверить обновления: {e}")
            return {'has_update': False, 'error': str(e)}
    
    def download_update(self, url: str, progress_callback=None) -> Path:
        """Скачивание обновления"""
        temp_dir = Path(tempfile.gettempdir()) / "cyberlink_update"
        temp_dir.mkdir(exist_ok=True)
        
        zip_path = temp_dir / "update.zip"
        
        print(f"📥 Скачивание обновления из {url}...")
        
        def report_progress(block_count, block_size, total_size):
            if progress_callback:
                progress = block_count * block_size / total_size if total_size > 0 else 0
                progress_callback(progress)
        
        urllib.request.urlretrieve(url, zip_path, report_progress)
        return zip_path
    
    def extract_update(self, zip_path: Path) -> Path:
        """Распаковка обновления"""
        extract_dir = zip_path.parent / "extracted"
        extract_dir.mkdir(exist_ok=True)
        
        print("📦 Распаковка обновления...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Находим папку с исходниками
        extracted_items = list(extract_dir.iterdir())
        if len(extracted_items) == 1 and extracted_items[0].is_dir():
            source_dir = extracted_items[0]
        else:
            source_dir = extract_dir
        
        return source_dir
    
    def apply_update(self, source_dir: Path) -> bool:
        """Применение обновления"""
        try:
            print("🔄 Применение обновления...")
            
            # Список файлов и папок для обновления
            items_to_update = [
                'core', 'gui', 'main.py', 'requirements.txt', 
                'run.py', 'updater.py', 'version.txt'
            ]
            
            for item in items_to_update:
                src_path = source_dir / item
                dst_path = Path.cwd() / item
                
                if src_path.exists():
                    if src_path.is_file():
                        shutil.copy2(src_path, dst_path)
                    elif src_path.is_dir():
                        # Обновляем только если это не data или logs
                        if item not in ['data', 'logs']:
                            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            
            print("✅ Обновление успешно установлено!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при обновлении: {e}")
            return False
    
    def update_in_background(self):
        """Фоновое обновление"""
        def update_thread():
            print("🔄 Проверка обновлений в фоне...")
            check_result = self.check_for_updates(silent=True)
            
            if check_result.get('has_update', False):
                self.update_queue.put(check_result)
        
        thread = threading.Thread(target=update_thread)
        thread.daemon = True
        thread.start()
    
    def perform_update(self, progress_callback=None) -> bool:
        """Выполнение полного обновления"""
        print("🔄 Начало обновления CyberLink...")
        
        # Проверяем обновления
        check_result = self.check_for_updates()
        
        if not check_result.get('has_update', False):
            print("✅ У вас последняя версия!")
            return True
        
        print(f"📌 Доступна новая версия: {check_result['latest']}")
        print(f"📌 Текущая версия: {check_result['current']}")
        
        if check_result.get('release_notes'):
            print("\n📝 Изменения:")
            print("-" * 40)
            print(check_result['release_notes'][:300] + "...")
            print("-" * 40)
        
        # Скачиваем обновление
        zip_path = self.download_update(check_result['download_url'], progress_callback)
        
        # Распаковываем
        source_dir = self.extract_update(zip_path)
        
        # Применяем
        success = self.apply_update(source_dir)
        
        # Очистка
        shutil.rmtree(zip_path.parent)
        
        if success:
            # Обновляем версию
            with open(self.version_file, 'w') as f:
                f.write(check_result['latest'])
            
            print("✅ CyberLink обновлен!")
            return True
        
        return False

# Функция для вызова из основного приложения
def check_and_prompt_update(parent=None):
    """Проверка обновлений с диалогом"""
    updater = CyberLinkUpdater()
    result = updater.check_for_updates()
    
    if result.get('has_update', False):
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            parent,
            "Обновление CyberLink",
            f"Доступна новая версия {result['latest']}!\n\n"
            f"Текущая версия: {result['current']}\n\n"
            f"Хотите обновить?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            return updater.perform_update()
    
    return False