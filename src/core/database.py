# src/core/database.py
# Работа с базой данных (чистая логика, без GUI)

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class Database:
    """Класс для работы с данными (без GUI зависимостей)"""
    
    def __init__(self, username: str = None):
        self.username = username
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        if username:
            self.user_dir = self.data_dir / "users" / username
            self.user_dir.mkdir(parents=True, exist_ok=True)
    
    # ============================================
    # Работа с профилем
    # ============================================
    
    def get_profile(self) -> Dict:
        """Получение профиля пользователя"""
        profile_path = self.user_dir / "profile.json"
        if profile_path.exists():
            with open(profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._default_profile()
    
    def save_profile(self, profile: Dict):
        """Сохранение профиля"""
        profile_path = self.user_dir / "profile.json"
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
    
    def _default_profile(self) -> Dict:
        """Профиль по умолчанию"""
        return {
            "username": self.username,
            "display_name": self.username,
            "status": "В сети",
            "bio": "",
            "avatar": None,
            "phone": None,
            "email": None,
            "birth_date": None,
            "city": None,
            "country": None,
            "occupation": None,
            "company": None,
        }
    
    # ============================================
    # Работа с контактами
    # ============================================
    
    def get_contacts(self) -> Dict:
        """Получение списка контактов"""
        contacts_path = self.user_dir / "contacts.json"
        if contacts_path.exists():
            with open(contacts_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"contacts": {}}
    
    def save_contacts(self, contacts: Dict):
        """Сохранение контактов"""
        contacts_path = self.user_dir / "contacts.json"
        with open(contacts_path, 'w', encoding='utf-8') as f:
            json.dump(contacts, f, indent=2, ensure_ascii=False)
    
    def add_contact(self, username: str, display_name: str = None):
        """Добавление контакта"""
        contacts = self.get_contacts()
        contacts["contacts"][username] = {
            "display_name": display_name or username,
            "nickname": None,
            "notes": None,
            "color": None,
            "mute": False,
            "pinned": False,
            "folder": None,
        }
        self.save_contacts(contacts)
    
    # ============================================
    # Работа с настройками
    # ============================================
    
    def get_settings(self) -> Dict:
        """Получение настроек пользователя"""
        settings_path = self.user_dir / "settings.json"
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._default_settings()
    
    def save_settings(self, settings: Dict):
        """Сохранение настроек"""
        settings_path = self.user_dir / "settings.json"
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    
    def _default_settings(self) -> Dict:
        """Настройки по умолчанию"""
        return {
            "theme": "dark",
            "font_size": 14,
            "font_family": "Mussels",
            "show_avatars": True,
            "show_timestamps": True,
            "enter_to_send": True,
            "notifications": {
                "sound": True,
                "popup": True,
                "vibration": True,
            },
            "privacy": {
                "last_seen": "contacts",
                "read_receipts": True,
                "online_status": "contacts",
            },
        }
    
    # ============================================
    # Работа с чатами
    # ============================================
    
    def get_chat_path(self, chat_id: str) -> Path:
        """Путь к файлу чата"""
        chat_dir = self.data_dir / "chats"
        chat_dir.mkdir(exist_ok=True)
        return chat_dir / f"{chat_id}.txt"
    
    def get_chat_messages(self, chat_id: str) -> List[Dict]:
        """Получение сообщений из чата"""
        chat_path = self.get_chat_path(chat_id)
        if not chat_path.exists():
            return []
        
        messages = []
        with open(chat_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Формат: [timestamp] @username: message
                    try:
                        timestamp = line[1:20]  # Примерная обработка
                        rest = line[22:]
                        if rest.startswith('@'):
                            username = rest.split(':')[0][1:]
                            content = ':'.join(rest.split(':')[1:]).strip()
                            messages.append({
                                'timestamp': timestamp,
                                'username': username,
                                'content': content,
                            })
                    except:
                        continue
        return messages
    
    def save_message(self, chat_id: str, username: str, content: str):
        """Сохранение сообщения в чат"""
        chat_path = self.get_chat_path(chat_id)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(chat_path, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] @{username}: {content}\n")
    
    # ============================================
    # Работа с файлами
    # ============================================
    
    def get_file_path(self, chat_id: str, file_id: str, filename: str) -> Path:
        """Путь к файлу в чате"""
        file_dir = self.data_dir / "files" / chat_id
        file_dir.mkdir(parents=True, exist_ok=True)
        return file_dir / f"{file_id}_{filename}"