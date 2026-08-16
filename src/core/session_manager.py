# src/core/session_manager.py
# Упрощенное управление сессией

import os
import json
import time
from datetime import datetime, timedelta


class SessionManager:
    """Управление сессией пользователя (упрощенное)"""
    
    def __init__(self):
        self.data_dir = os.path.join("data", "sessions")
        os.makedirs(self.data_dir, exist_ok=True)
        self.session_file = os.path.join(self.data_dir, "session.json")
        self.last_login_file = os.path.join(self.data_dir, "last_login.json")
    
    def save_session(self, username: str) -> bool:
        """Сохранение сессии (без пароля)"""
        try:
            data = {
                'username': username,
                'created_at': time.time()
            }
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Сохраняем время последнего входа
            with open(self.last_login_file, 'w', encoding='utf-8') as f:
                json.dump({'last_login': time.time()}, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения сессии: {e}")
            return False
    
    def load_session(self) -> str | None:
        """Загрузка сессии"""
        try:
            if not os.path.exists(self.session_file):
                return None
            
            with open(self.session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data.get('username')
        except Exception as e:
            print(f"❌ Ошибка загрузки сессии: {e}")
            return None
    
    def clear_session(self):
        """Удаление сессии (выход)"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            if os.path.exists(self.last_login_file):
                os.remove(self.last_login_file)
            return True
        except Exception as e:
            print(f"❌ Ошибка удаления сессии: {e}")
            return False
    
    def has_session(self) -> bool:
        """Проверка наличия сохраненной сессии"""
        return os.path.exists(self.session_file)
    
    def needs_password(self) -> bool:
        """Проверка, нужен ли пароль (раз в день)"""
        try:
            if not os.path.exists(self.last_login_file):
                return True  # Если файла нет - нужен пароль
            
            with open(self.last_login_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            last_login = data.get('last_login', 0)
            # Прошло больше 24 часов?
            return (time.time() - last_login) > 86400  # 24 часа в секундах
            
        except Exception as e:
            print(f"❌ Ошибка проверки времени: {e}")
            return True  # В случае ошибки - просим пароль