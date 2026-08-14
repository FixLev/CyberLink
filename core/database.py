# core/database.py
# CyberLink - Работа с базой данных

import sqlite3
import json
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

class Database:
    """Класс для работы с базой данных CyberLink"""
    
    def __init__(self, username: str = None):
        """Инициализация базы данных"""
        Path("data").mkdir(exist_ok=True)
        
        if username:
            self.db_path = f"data/{username}.db"
        else:
            self.db_path = "data/system.db"
        
        self._username = username
        self.init_db()
    
    def init_db(self):
        """Инициализация структуры базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица сообщений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user TEXT NOT NULL,
                to_user TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                sync_hash TEXT UNIQUE
            )
        ''')
        
        # Таблица контактов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                username TEXT PRIMARY KEY,
                last_message TEXT,
                last_message_time TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_message(self, from_user: str, to_user: str, content: str, sync_hash: str = None) -> str:
        """Сохранение сообщения"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        if sync_hash is None:
            sync_hash = hashlib.md5(
                f"{from_user}{to_user}{timestamp}{content}".encode()
            ).hexdigest()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO messages 
                (from_user, to_user, content, timestamp, sync_hash, is_read)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (from_user, to_user, content, timestamp, sync_hash, 0))
            conn.commit()
        except Exception as e:
            print(f"⚠️ Ошибка сохранения: {e}")
        finally:
            conn.close()
        
        return sync_hash
    
    def get_messages_with(self, username: str, limit: int = 100) -> List[Tuple]:
        """Получение сообщений с пользователем"""
        current_user = self.get_current_user()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT from_user, to_user, content, timestamp, is_read
            FROM messages
            WHERE (from_user = ? AND to_user = ?) OR (from_user = ? AND to_user = ?)
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (username, current_user, current_user, username, limit))
        
        messages = cursor.fetchall()
        conn.close()
        return list(reversed(messages))
    
    def get_current_user(self) -> str:
        """Получение текущего пользователя"""
        return os.path.basename(self.db_path).replace('.db', '')
    
    def get_all_contacts(self) -> List[Tuple]:
        """Получение всех контактов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, last_message, last_message_time
            FROM contacts
            ORDER BY last_message_time DESC
        ''')
        
        contacts = cursor.fetchall()
        conn.close()
        return contacts
    
    def update_contact(self, username: str, last_message: str):
        """Обновление контакта"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        cursor.execute('''
            INSERT OR REPLACE INTO contacts (username, last_message, last_message_time)
            VALUES (?, ?, ?)
        ''', (username, last_message, timestamp))
        
        conn.commit()
        conn.close()
    
    def get_unread_count(self, username: str) -> int:
        """Количество непрочитанных сообщений"""
        current_user = self.get_current_user()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM messages
            WHERE from_user = ? AND to_user = ? AND is_read = 0
        ''', (username, current_user))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def mark_as_read(self, from_user: str):
        """Отметить как прочитанные"""
        current_user = self.get_current_user()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE messages
            SET is_read = 1
            WHERE from_user = ? AND to_user = ? AND is_read = 0
        ''', (from_user, current_user))
        
        conn.commit()
        conn.close()

# Экспорт класса
__all__ = ['Database']