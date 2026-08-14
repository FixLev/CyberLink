import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional

class MessageSync:
    """Синхронизация сообщений между узлами"""
    
    def __init__(self, database, network):
        self.database = database
        self.network = network
    
    async def sync_with_user(self, username: str):
        """Синхронизация сообщений с конкретным пользователем"""
        # Получаем последние сообщения
        messages = self.database.get_messages_with(username, limit=50)
        
        # Формируем контрольную сумму
        sync_data = {
            'username': self.database.get_current_user(),
            'last_messages': messages,
            'timestamp': datetime.now().isoformat()
        }
        
        # Отправляем запрос на синхронизацию
        # В реальной реализации здесь был бы обмен данными
        # Для демонстрации просто возвращаем данные
        return sync_data
    
    async def merge_messages(self, sync_data: Dict):
        """Объединение полученных сообщений с локальными"""
        if not sync_data or 'last_messages' not in sync_data:
            return
        
        for msg in sync_data['last_messages']:
            from_user, to_user, content, timestamp, is_read = msg
            current_user = self.database.get_current_user()
            
            # Проверяем, есть ли уже такое сообщение
            # Используем комбинацию полей как уникальный идентификатор
            sync_hash = hashlib.md5(
                f"{from_user}{to_user}{timestamp}{content}".encode()
            ).hexdigest()
            
            # Сохраняем, если такого сообщения нет
            existing = self.database.save_message(
                from_user, to_user, content, sync_hash
            )
            
            # Обновляем контакт
            if from_user != current_user:
                self.database.update_contact(from_user, content)
            elif to_user != current_user:
                self.database.update_contact(to_user, content)
    
    def get_messages_hash(self, username: str) -> str:
        """Получение хэша всех сообщений с пользователем"""
        messages = self.database.get_messages_with(username)
        if not messages:
            return ""
        
        # Создаем строку из всех сообщений и хэшируем
        msg_string = "".join([
            f"{m[0]}{m[1]}{m[2]}{m[3]}" 
            for m in messages
        ])
        return hashlib.md5(msg_string.encode()).hexdigest()
    
    def find_missing_messages(self, username: str, remote_hash: str) -> List:
        """Поиск отсутствующих сообщений"""
        local_hash = self.get_messages_hash(username)
        if local_hash == remote_hash:
            return []  # Все синхронизировано
        
        # Если хэши не совпадают, отправляем все сообщения
        # В реальной реализации здесь был бы более сложный алгоритм
        return self.database.get_messages_with(username)