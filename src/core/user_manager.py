# src/core/user_manager.py
# Управление пользователями (БЕЗ @)

import re
import json
import hashlib
import secrets
import os
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional, Dict, List


class UserManager:
    """Класс для управления пользователями (без @)"""
    
    def __init__(self):
        self.data_dir = Path("data/users")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Файл со списком всех пользователей
        self.users_file = self.data_dir.parent / "users_registry.json"
        
        # Загружаем реестр
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Загрузка реестра пользователей"""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"users": {}}
        return {"users": {}}
    
    def _save_registry(self):
        """Сохранение реестра пользователей"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
            print(f"💾 Реестр сохранён: {list(self.registry['users'].keys())}")
        except Exception as e:
            print(f"❌ Ошибка сохранения реестра: {e}")
    
    def validate_username(self, username: str) -> Tuple[bool, str]:
        """Проверка валидности имени пользователя"""
        if not username or not username.strip():
            return False, "Имя пользователя не может быть пустым"
        
        username = username.strip()
        
        # Убираем @ если есть
        if username.startswith('@'):
            username = username[1:]
        
        if len(username) < 3 or len(username) > 24:
            return False, "Имя должно быть от 3 до 24 символов"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Разрешены только латиница, цифры и подчеркивание"
        
        if username.startswith('_') or username.endswith('_'):
            return False, "Имя не может начинаться или заканчиваться на _"
        
        if '__' in username:
            return False, "Имя не может содержать двойное подчеркивание"
        
        if username.isdigit():
            return False, "Имя не может состоять только из цифр"
        
        return True, username
    
    def _create_profile(self, username: str):
        """Создание профиля пользователя"""
        user_dir = self.data_dir / username
        user_dir.mkdir(parents=True, exist_ok=True)
        
        profile = {
            "username": username,
            "display_name": username,
            "status": "В сети",
            "bio": "",
            "phone": "",
            "email": "",
            "birth_date": "",
            "city": "",
            "country": "",
            "occupation": "",
            "company": "",
            "gender": "Не указан",
            "has_avatar": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        with open(user_dir / "profile.json", 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        # Создаём другие файлы
        contacts = {"contacts": [], "pending": [], "blocked": []}
        with open(user_dir / "contacts.json", 'w', encoding='utf-8') as f:
            json.dump(contacts, f, indent=2, ensure_ascii=False)
        
        groups = {"groups": []}
        with open(user_dir / "groups.json", 'w', encoding='utf-8') as f:
            json.dump(groups, f, indent=2, ensure_ascii=False)
        
        settings = {
            "theme": "dark",
            "language": "ru",
            "notifications": True,
            "sound": True,
            "font_size": 14,
        }
        with open(user_dir / "settings.json", 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        
        privacy = {
            "status": "online",
            "last_seen": {"level": "contacts", "selected": []},
            "phone": {"level": "contacts", "selected": []},
            "email": {"level": "contacts", "selected": []},
            "gender": {"level": "contacts", "selected": []},
            "birth_date": {"level": "contacts", "selected": []},
            "city": {"level": "contacts", "selected": []},
            "country": {"level": "contacts", "selected": []},
            "occupation": {"level": "contacts", "selected": []},
            "company": {"level": "contacts", "selected": []},
            "bio": {"level": "everyone", "selected": []},
            "who_can_message_me": "everyone",
        }
        with open(user_dir / "privacy.json", 'w', encoding='utf-8') as f:
            json.dump(privacy, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Создан профиль для {username}")
    
    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Регистрация нового пользователя"""
        username = username.strip()
        
        # Убираем @ если есть
        if username.startswith('@'):
            username = username[1:]
        
        # Проверяем валидность
        valid, result = self.validate_username(username)
        if not valid:
            return False, result
        username = result
        
        # Проверяем, не занят ли логин
        if username in self.registry["users"]:
            return False, f"Логин {username} уже занят"
        
        # Проверяем пароль
        if len(password) < 6:
            return False, "Пароль должен быть не менее 6 символов"
        
        # Хешируем пароль
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        ).hex()
        
        # Сохраняем пользователя в реестр
        self.registry["users"][username] = {
            "created_at": datetime.now().isoformat(),
            "salt": salt,
            "password_hash": password_hash,
        }
        self._save_registry()
        
        # Создаём профиль и все файлы
        self._create_profile(username)
        
        print(f"✅ Пользователь {username} зарегистрирован")
        return True, f"Пользователь {username} успешно зарегистрирован!"
    
    def login_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Вход пользователя"""
        username = username.strip()
        
        # Убираем @ если есть
        if username.startswith('@'):
            username = username[1:]
        
        if username not in self.registry["users"]:
            return False, f"Пользователь {username} не найден"
        
        user_data = self.registry["users"][username]
        salt = user_data["salt"]
        stored_hash = user_data["password_hash"]
        
        # Проверяем пароль
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        ).hex()
        
        if password_hash != stored_hash:
            return False, "Неверный пароль"
        
        print(f"✅ Вход выполнен для {username}")
        return True, f"Добро пожаловать в CyberLink, {username}!"
    
    def user_exists(self, username: str) -> bool:
        """Проверка существования пользователя"""
        username = username.strip()
        if username.startswith('@'):
            username = username[1:]
        return username in self.registry["users"]
    
    def get_all_users(self) -> List[str]:
        """Получение списка всех пользователей"""
        return list(self.registry["users"].keys())
    
    def create_session(self, username: str) -> str:
        """Создание сессионного токена для автоматического входа"""
        token = secrets.token_urlsafe(32)
        session_file = self.data_dir.parent / "session.json"
        
        session_data = {}
        if session_file.exists():
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
            except:
                pass
        
        session_data[username] = {
            "token": token,
            "created_at": datetime.now().isoformat(),
        }
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        return token
    
    def validate_session(self, token: str) -> Optional[str]:
        """Проверка сессионного токена"""
        session_file = self.data_dir.parent / "session.json"
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            for username, data in session_data.items():
                if data.get("token") == token:
                    return username
        except:
            pass
        
        return None
    
    def clear_session(self, username: str):
        """Очистка сессии пользователя"""
        session_file = self.data_dir.parent / "session.json"
        if not session_file.exists():
            return
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            if username in session_data:
                del session_data[username]
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        except:
            pass