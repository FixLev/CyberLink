# src/core/database.py
# Работа с базой данных (С ШИФРОВАНИЕМ)

import json
import os
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from src.core.encrypted_storage import EncryptedStorage


class Database:
    """Класс для работы с данными (с шифрованием)"""
    
    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Создаём зашифрованное хранилище
        if username and password:
            self.storage = EncryptedStorage(username, password)
        else:
            self.storage = None
    
    def _get_storage(self) -> EncryptedStorage:
        """Получение хранилища"""
        if not self.storage:
            raise Exception("Хранилище не инициализировано. Передайте username и password.")
        return self.storage
    
    # ============================================
    # Работа с профилем (зашифровано)
    # ============================================
    
    def get_profile(self) -> Dict:
        """Получение профиля пользователя (зашифровано)"""
        storage = self._get_storage()
        profile = storage.load('profile.json')
        if not profile:
            profile = self._default_profile()
            storage.save('profile.json', profile)
        return profile
    
    def save_profile(self, profile: Dict):
        """Сохранение профиля (зашифровано)"""
        storage = self._get_storage()
        storage.save('profile.json', profile)
    
    def _default_profile(self) -> Dict:
        """Профиль по умолчанию"""
        return {
            "username": self.username,
            "display_name": self.username,
            "status": "В сети",
            "bio": "",
            "avatar": None,
            "phone": "",
            "email": "",
            "birth_date": "",
            "city": "",
            "country": "",
            "occupation": "",
            "company": "",
            "gender": "Не указан",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
    
    # ============================================
    # Работа с контактами (зашифровано)
    # ============================================
    
    def get_contacts(self) -> Dict:
        """Получение списка контактов (зашифровано)"""
        storage = self._get_storage()
        contacts = storage.load('contacts.json')
        if not contacts:
            contacts = {"contacts": {}, "pending": [], "blocked": []}
            storage.save('contacts.json', contacts)
        return contacts
    
    def save_contacts(self, contacts: Dict):
        """Сохранение контактов (зашифровано)"""
        storage = self._get_storage()
        storage.save('contacts.json', contacts)
    
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
            "added_at": datetime.now().isoformat(),
        }
        self.save_contacts(contacts)
    
    def remove_contact(self, username: str):
        """Удаление контакта"""
        contacts = self.get_contacts()
        if username in contacts["contacts"]:
            del contacts["contacts"][username]
            self.save_contacts(contacts)
            return True
        return False
    
    def get_contact(self, username: str) -> Optional[Dict]:
        """Получение информации о контакте"""
        contacts = self.get_contacts()
        return contacts["contacts"].get(username)
    
    # ============================================
    # Работа с настройками (зашифровано)
    # ============================================
    
    def get_settings(self) -> Dict:
        """Получение настроек пользователя (зашифровано)"""
        storage = self._get_storage()
        settings = storage.load('settings.json')
        if not settings:
            settings = self._default_settings()
            storage.save('settings.json', settings)
        return settings
    
    def save_settings(self, settings: Dict):
        """Сохранение настроек (зашифровано)"""
        storage = self._get_storage()
        storage.save('settings.json', settings)
    
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
    # Работа с приватностью (зашифровано)
    # ============================================
    
    def get_privacy(self) -> Dict:
        """Получение настроек приватности (зашифровано)"""
        storage = self._get_storage()
        privacy = storage.load('privacy.json')
        if not privacy:
            privacy = self._default_privacy()
            storage.save('privacy.json', privacy)
        return privacy
    
    def save_privacy(self, privacy: Dict):
        """Сохранение настроек приватности (зашифровано)"""
        storage = self._get_storage()
        storage.save('privacy.json', privacy)
    
    def _default_privacy(self) -> Dict:
        """Настройки приватности по умолчанию"""
        return {
            "status": "online",
            "last_seen": {"level": "contacts", "selected": []},
            "profile_photo": {"level": "everyone", "selected": []},
            "phone": {"level": "contacts", "selected": []},
            "email": {"level": "contacts", "selected": []},
            "gender": {"level": "contacts", "selected": []},
            "birth_date": {"level": "contacts", "selected": []},
            "city": {"level": "contacts", "selected": []},
            "country": {"level": "contacts", "selected": []},
            "occupation": {"level": "contacts", "selected": []},
            "company": {"level": "contacts", "selected": []},
            "bio": {"level": "everyone", "selected": []},
            "read_receipts": True,
            "who_can_add_me": "everyone",
            "who_can_message_me": "everyone",
            "who_can_call_me": "contacts",
        }
    
    # ============================================
    # Работа с чатами (зашифровано)
    # ============================================
    
    def get_chat_messages(self, chat_id: str) -> List[Dict]:
        """Получение сообщений из чата (зашифровано)"""
        storage = self._get_storage()
        chat_data = storage.load(f'chat_{chat_id}.json')
        if not chat_data:
            return []
        return chat_data.get('messages', [])
    
    def save_message(self, chat_id: str, username: str, content: str, message_type: str = "text"):
        """Сохранение сообщения в чат (зашифровано)"""
        storage = self._get_storage()
        filename = f'chat_{chat_id}.json'
        
        chat_data = storage.load(filename)
        if not chat_data:
            chat_data = {
                'chat_id': chat_id,
                'created_at': datetime.now().isoformat(),
                'messages': []
            }
        
        message = {
            'id': f"{int(datetime.now().timestamp() * 1000)}_{username}",
            'sender': username,
            'content': content,
            'type': message_type,
            'timestamp': datetime.now().isoformat(),
            'status': 'sent'
        }
        
        chat_data['messages'].append(message)
        chat_data['updated_at'] = datetime.now().isoformat()
        
        storage.save(filename, chat_data)
        return message
    
    def get_chat_history(self, chat_id: str, limit: int = 50) -> List[Dict]:
        """Получение истории чата"""
        messages = self.get_chat_messages(chat_id)
        return messages[-limit:] if messages else []
    
    # ============================================
    # Работа с группами (зашифровано)
    # ============================================
    
    def get_groups(self) -> Dict:
        """Получение групп (зашифровано)"""
        storage = self._get_storage()
        groups = storage.load('groups.json')
        if not groups:
            groups = {"groups": []}
            storage.save('groups.json', groups)
        return groups
    
    def save_groups(self, groups: Dict):
        """Сохранение групп (зашифровано)"""
        storage = self._get_storage()
        storage.save('groups.json', groups)
    
    def add_group(self, group_name: str, members: List[str]) -> Dict:
        """Создание группы"""
        groups = self.get_groups()
        
        group = {
            'id': f"g_{int(datetime.now().timestamp())}",
            'name': group_name,
            'members': members,
            'admin': self.username,
            'created_at': datetime.now().isoformat(),
            'messages': []
        }
        
        groups['groups'].append(group)
        self.save_groups(groups)
        return group
    
    # ============================================
    # Работа с файлами
    # ============================================
    
    def get_file_path(self, chat_id: str, file_id: str, filename: str) -> Path:
        """Путь к файлу в чате (НЕ зашифровано - файлы большие)"""
        file_dir = self.data_dir / "files" / chat_id
        file_dir.mkdir(parents=True, exist_ok=True)
        return file_dir / f"{file_id}_{filename}"
    
    def save_file_metadata(self, chat_id: str, file_id: str, metadata: Dict):
        """Сохранение метаданных файла (зашифровано)"""
        storage = self._get_storage()
        files = storage.load('files_metadata.json')
        if not files:
            files = {}
        
        if chat_id not in files:
            files[chat_id] = {}
        
        files[chat_id][file_id] = metadata
        storage.save('files_metadata.json', files)
    
    def get_file_metadata(self, chat_id: str, file_id: str) -> Optional[Dict]:
        """Получение метаданных файла (зашифровано)"""
        storage = self._get_storage()
        files = storage.load('files_metadata.json')
        if not files:
            return None
        return files.get(chat_id, {}).get(file_id)