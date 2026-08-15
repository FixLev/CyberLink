# src/core/user_manager.py
# Управление пользователями (без GUI)

import re
import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional, Dict, List


class UserManager:
    """Класс для управления пользователями (без GUI)"""
    
    def __init__(self):
        self.data_dir = Path("data/users")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Файл со списком всех пользователей
        self.users_file = self.data_dir.parent / "users_registry.json"
    
    def _load_registry(self) -> Dict:
        """Загрузка реестра пользователей"""
        if self.users_file.exists():
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"users": {}}
    
    def _save_registry(self, registry: Dict):
        """Сохранение реестра пользователей"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
    
    def validate_username(self, username: str) -> Tuple[bool, str]:
        """Проверка валидности имени пользователя"""
        if not username or not username.strip():
            return False, "Имя пользователя не может быть пустым"
        
        username = username.strip()
        
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
        
        return True, "OK"
    
    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Регистрация нового пользователя"""
        username = username.strip()
        
        # Проверяем валидность
        valid, message = self.validate_username(username)
        if not valid:
            return False, message
        
        # Проверяем, не занят ли логин
        registry = self._load_registry()
        if username in registry["users"]:
            return False, f"Логин @{username} уже занят"
        
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
        
        # Сохраняем пользователя
        registry["users"][username] = {
            "created_at": datetime.now().isoformat(),
            "salt": salt,
            "password_hash": password_hash,
        }
        self._save_registry(registry)
        
        # Создаем папку пользователя
        user_dir = self.data_dir / username
        user_dir.mkdir(exist_ok=True)
        
        # Создаем профиль
        profile = {
            "username": username,
            "display_name": username,
            "status": "В сети",
            "bio": "",
            "avatar": None,
        }
        with open(user_dir / "profile.json", 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        return True, f"Пользователь @{username} успешно зарегистрирован!"
    
    def login_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Вход пользователя"""
        username = username.strip()
        
        registry = self._load_registry()
        if username not in registry["users"]:
            return False, f"Пользователь @{username} не найден"
        
        user_data = registry["users"][username]
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
        
        return True, f"Добро пожаловать в CyberLink, @{username}!"
    
    def user_exists(self, username: str) -> bool:
        """Проверка существования пользователя"""
        registry = self._load_registry()
        return username in registry["users"]
    
    def get_all_users(self) -> List[str]:
        """Получение списка всех пользователей"""
        registry = self._load_registry()
        return list(registry["users"].keys())
    
    def create_session(self, username: str) -> str:
        """Создание сессионного токена для автоматического входа"""
        token = secrets.token_urlsafe(32)
        session_file = self.data_dir.parent / "session.json"
        
        session_data = {}
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
        
        session_data[username] = {
            "token": token,
            "created_at": datetime.now().isoformat(),
            "expires": datetime.now().isoformat(),  # Потом добавим срок
        }
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        return token
    
    def validate_session(self, token: str) -> Optional[str]:
        """Проверка сессионного токена"""
        session_file = self.data_dir.parent / "session.json"
        if not session_file.exists():
            return None
        
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        for username, data in session_data.items():
            if data.get("token") == token:
                return username
        
        return None
    
    def clear_session(self, username: str):
        """Очистка сессии пользователя"""
        session_file = self.data_dir.parent / "session.json"
        if not session_file.exists():
            return
        
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        if username in session_data:
            del session_data[username]
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)