# core/user_manager.py
# CyberLink - Менеджер пользователей

import sqlite3
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional, Dict, List

class UserManager:
    """Класс для управления пользователями в CyberLink"""
    
    def __init__(self):
        """Инициализация менеджера пользователей"""
        # Создаем папку data если её нет
        Path("data").mkdir(exist_ok=True)
        self.db_path = "data/users.db"
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных пользователей"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Создаем таблицу пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                is_online INTEGER DEFAULT 0,
                last_seen TEXT,
                avatar TEXT DEFAULT '👤',
                status TEXT DEFAULT 'В сети'
            )
        ''')
        
        # Создаем таблицу для друзей/контактов (в будущем)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS friends (
                user1 TEXT,
                user2 TEXT,
                added_at TEXT,
                PRIMARY KEY (user1, user2)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def validate_username(self, username: str) -> Tuple[bool, str]:
        """
        Проверка валидности имени пользователя
        
        Args:
            username: Проверяемое имя пользователя
            
        Returns:
            Tuple[bool, str]: (валидность, сообщение)
        """
        # Проверяем, что имя не пустое
        if not username or not username.strip():
            return False, "Имя пользователя не может быть пустым"
        
        username = username.strip()
        
        # Проверяем длину
        if len(username) < 3:
            return False, "Имя должно быть от 3 до 24 символов (сейчас {})".format(len(username))
        
        if len(username) > 24:
            return False, "Имя должно быть от 3 до 24 символов (сейчас {})".format(len(username))
        
        # Проверяем допустимые символы (латиница, цифры, подчеркивание)
        pattern = r'^[a-zA-Z0-9_]+$'
        if not re.match(pattern, username):
            return False, "Разрешены только латиница (A-Z, a-z), цифры (0-9) и подчеркивание (_)"
        
        # Проверяем, что не начинается с подчеркивания
        if username.startswith('_'):
            return False, "Имя не может начинаться с подчеркивания (_)"
        
        # Проверяем, что не заканчивается подчеркиванием
        if username.endswith('_'):
            return False, "Имя не может заканчиваться подчеркиванием (_)"
        
        # Проверяем, что нет двойных подчеркиваний
        if '__' in username:
            return False, "Имя не может содержать двойное подчеркивание (__)"
        
        # Проверяем, что не содержит только цифры
        if username.isdigit():
            return False, "Имя не может состоять только из цифр"
        
        return True, "OK"
    
    def register_user(self, username: str) -> Tuple[bool, str]:
        """
        Регистрация нового пользователя
        
        Args:
            username: Имя пользователя для регистрации
            
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        username = username.strip()
        
        # Проверяем валидность
        valid, message = self.validate_username(username)
        if not valid:
            return False, message
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Проверяем, не занят ли логин
            cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                conn.close()
                return False, f"Логин @{username} уже занят"
            
            # Регистрируем пользователя
            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO users (username, created_at, is_online, last_seen, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, now, 1, now, "В сети"))
            
            conn.commit()
            conn.close()
            
            # Создаем базу данных для пользователя
            from .database import Database
            Database(username)
            
            return True, f"Пользователь @{username} успешно зарегистрирован!"
            
        except sqlite3.IntegrityError:
            conn.close()
            return False, f"Ошибка: логин @{username} уже существует"
        except Exception as e:
            conn.close()
            return False, f"Ошибка регистрации: {str(e)}"
    
    def login_user(self, username: str) -> Tuple[bool, str]:
        """
        Вход пользователя в систему
        
        Args:
            username: Имя пользователя
            
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        username = username.strip()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Проверяем существование пользователя
            cursor.execute('SELECT username, is_online FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False, f"Пользователь @{username} не найден"
            
            # Проверяем, не залогинен ли уже
            if user[1] == 1:
                conn.close()
                return True, f"Добро пожаловать назад, @{username}!"
            
            # Обновляем статус онлайн
            now = datetime.now().isoformat()
            cursor.execute('''
                UPDATE users 
                SET is_online = 1, last_seen = ?, status = 'В сети'
                WHERE username = ?
            ''', (now, username))
            
            conn.commit()
            conn.close()
            
            return True, f"Добро пожаловать в CyberLink, @{username}!"
            
        except Exception as e:
            conn.close()
            return False, f"Ошибка входа: {str(e)}"
    
    def logout_user(self, username: str) -> Tuple[bool, str]:
        """
        Выход пользователя из системы
        
        Args:
            username: Имя пользователя
            
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        username = username.strip()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            now = datetime.now().isoformat()
            cursor.execute('''
                UPDATE users 
                SET is_online = 0, last_seen = ?, status = 'Не в сети'
                WHERE username = ?
            ''', (now, username))
            
            conn.commit()
            conn.close()
            
            return True, f"До свидания, @{username}!"
            
        except Exception as e:
            conn.close()
            return False, f"Ошибка выхода: {str(e)}"
    
    def user_exists(self, username: str) -> bool:
        """
        Проверка существования пользователя
        
        Args:
            username: Имя пользователя
            
        Returns:
            bool: True если пользователь существует
        """
        username = username.strip()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """
        Получение информации о пользователе
        
        Args:
            username: Имя пользователя
            
        Returns:
            Optional[Dict]: Информация о пользователе или None
        """
        username = username.strip()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, created_at, is_online, last_seen, status, avatar
            FROM users 
            WHERE username = ?
        ''', (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'username': user[0],
                'created_at': user[1],
                'is_online': bool(user[2]),
                'last_seen': user[3],
                'status': user[4],
                'avatar': user[5]
            }
        return None
    
    def get_all_users(self, include_offline: bool = True) -> List[Dict]:
        """
        Получение всех пользователей
        
        Args:
            include_offline: Включать ли оффлайн пользователей
            
        Returns:
            List[Dict]: Список пользователей
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if include_offline:
            cursor.execute('''
                SELECT username, is_online, last_seen, status, avatar
                FROM users 
                ORDER BY is_online DESC, username
            ''')
        else:
            cursor.execute('''
                SELECT username, is_online, last_seen, status, avatar
                FROM users 
                WHERE is_online = 1
                ORDER BY username
            ''')
        
        users = cursor.fetchall()
        conn.close()
        
        return [
            {
                'username': u[0],
                'is_online': bool(u[1]),
                'last_seen': u[2],
                'status': u[3],
                'avatar': u[4]
            }
            for u in users
        ]
    
    def get_online_users(self) -> List[str]:
        """
        Получение списка онлайн пользователей
        
        Returns:
            List[str]: Список имен онлайн пользователей
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username
            FROM users 
            WHERE is_online = 1
            ORDER BY username
        ''')
        
        users = cursor.fetchall()
        conn.close()
        
        return [u[0] for u in users]
    
    def update_status(self, username: str, status: str) -> bool:
        """
        Обновление статуса пользователя
        
        Args:
            username: Имя пользователя
            status: Новый статус
            
        Returns:
            bool: Успех операции
        """
        username = username.strip()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users 
                SET status = ?
                WHERE username = ?
            ''', (status, username))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            conn.close()
            return False
    
    def get_user_count(self) -> int:
        """
        Получение общего количества пользователей
        
        Returns:
            int: Количество пользователей
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def get_online_count(self) -> int:
        """
        Получение количества онлайн пользователей
        
        Returns:
            int: Количество онлайн пользователей
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_online = 1')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def search_users(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Поиск пользователей по имени
        
        Args:
            query: Поисковый запрос
            limit: Максимальное количество результатов
            
        Returns:
            List[Dict]: Список найденных пользователей
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, is_online, status
            FROM users 
            WHERE username LIKE ?
            ORDER BY is_online DESC, username
            LIMIT ?
        ''', (f'%{query}%', limit))
        
        users = cursor.fetchall()
        conn.close()
        
        return [
            {
                'username': u[0],
                'is_online': bool(u[1]),
                'status': u[2]
            }
            for u in users
        ]
    
    def add_friend(self, user1: str, user2: str) -> bool:
        """
        Добавление друга в список контактов
        
        Args:
            user1: Имя первого пользователя
            user2: Имя второго пользователя
            
        Returns:
            bool: Успех операции
        """
        user1 = user1.strip()
        user2 = user2.strip()
        
        # Проверяем, что пользователи существуют
        if not self.user_exists(user1) or not self.user_exists(user2):
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT OR IGNORE INTO friends (user1, user2, added_at)
                VALUES (?, ?, ?)
            ''', (user1, user2, now))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            conn.close()
            return False
    
    def get_friends(self, username: str) -> List[str]:
        """
        Получение списка друзей пользователя
        
        Args:
            username: Имя пользователя
            
        Returns:
            List[str]: Список друзей
        """
        username = username.strip()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user2 FROM friends WHERE user1 = ?
            UNION
            SELECT user1 FROM friends WHERE user2 = ?
        ''', (username, username))
        
        friends = cursor.fetchall()
        conn.close()
        
        return [f[0] for f in friends]
    
    def delete_user(self, username: str) -> Tuple[bool, str]:
        """
        Удаление пользователя и всех его данных
        
        Args:
            username: Имя пользователя
            
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        username = username.strip()
        
        if not self.user_exists(username):
            return False, f"Пользователь @{username} не найден"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Удаляем пользователя
            cursor.execute('DELETE FROM users WHERE username = ?', (username,))
            
            # Удаляем связи друзей
            cursor.execute('DELETE FROM friends WHERE user1 = ? OR user2 = ?', (username, username))
            
            conn.commit()
            conn.close()
            
            # Удаляем базу данных сообщений
            import os
            db_file = f"data/{username}.db"
            if os.path.exists(db_file):
                os.remove(db_file)
            
            return True, f"Пользователь @{username} удален"
            
        except Exception as e:
            conn.close()
            return False, f"Ошибка удаления: {str(e)}"
    
    def cleanup_offline(self, timeout_minutes: int = 30):
        """
        Очистка пользователей, которые долго не активны
        
        Args:
            timeout_minutes: Время бездействия в минутах
        """
        from datetime import timedelta
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(minutes=timeout_minutes)).isoformat()
        
        cursor.execute('''
            UPDATE users 
            SET is_online = 0, status = 'Не в сети'
            WHERE is_online = 1 AND last_seen < ?
        ''', (cutoff,))
        
        conn.commit()
        conn.close()

# Небольшой тест, если файл запущен напрямую
if __name__ == "__main__":
    # Тестирование UserManager
    um = UserManager()
    
    print("🔧 Тестирование UserManager...")
    print("=" * 50)
    
    # Тест валидации
    test_names = [
        "user", "User123", "user_name", "_test", "test_", "user__name", 
        "ab", "this_is_a_very_long_username_that_exceeds_24_chars",
        "123user", "user@name", "user-name"
    ]
    
    for name in test_names:
        valid, msg = um.validate_username(name)
        print(f"  {name}: {'✅' if valid else '❌'} {msg}")
    
    print("\n" + "=" * 50)
    
    # Тест регистрации
    test_user = "testuser"
    success, msg = um.register_user(test_user)
    print(f"Регистрация {test_user}: {'✅' if success else '❌'} {msg}")
    
    # Тест входа
    if success:
        success, msg = um.login_user(test_user)
        print(f"Вход {test_user}: {'✅' if success else '❌'} {msg}")
    
    # Тест получения информации
    info = um.get_user_info(test_user)
    if info:
        print(f"Информация о {test_user}:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено!")