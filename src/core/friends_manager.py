# src/core/friends_manager.py
# Менеджер друзей и заявок

import json
import os
import time
from typing import Dict, List, Optional
from PyQt5.QtCore import QObject, pyqtSignal


class FriendStatus:
    ONLINE = "online"
    OFFLINE = "offline"


class FriendsManager(QObject):
    """Менеджер друзей - работа с заявками и контактами"""
    
    friend_added = pyqtSignal(str, str)  # (friend_id, display_name)
    friend_removed = pyqtSignal(str)  # (friend_id)
    friend_status_changed = pyqtSignal(str, str)  # (friend_id, status)
    friend_request_received = pyqtSignal(str, str, str)  # (from_id, display_name, message)
    friend_request_responded = pyqtSignal(str, bool)  # (friend_id, accepted)
    
    def __init__(self, username: str, storage=None, network=None):
        super().__init__()
        self.username = username
        self.storage = storage
        self.network = network
        
        self.friends: Dict[str, dict] = {}
        self.pending_requests: Dict[str, dict] = {}
        self.online_friends: set = set()
        self.blocked_users: set = set()
        
        # Папка данных
        self.data_dir = os.path.join("data", "users", username)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.friends_file = os.path.join(self.data_dir, "friends.json")
        self.requests_file = os.path.join(self.data_dir, "friend_requests.json")
        
        self.load_friends()
        self.load_pending_requests()
        
        if self.network:
            self._connect_signals()
    
    def _connect_signals(self):
        """Подключение сигналов сети"""
        if not self.network:
            return
        
        if hasattr(self.network, 'friend_request_received'):
            self.network.friend_request_received.connect(self._on_friend_request)
        
        if hasattr(self.network, 'friend_request_response'):
            self.network.friend_request_response.connect(self._on_friend_response)
        
        if hasattr(self.network, 'friend_online'):
            self.network.friend_online.connect(self._on_online)
        
        if hasattr(self.network, 'friend_offline'):
            self.network.friend_offline.connect(self._on_offline)
        
        if hasattr(self.network, 'message_received'):
            self.network.message_received.connect(self._on_message)
    
    def load_friends(self):
        """Загрузка списка друзей"""
        if os.path.exists(self.friends_file):
            try:
                with open(self.friends_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.friends = data.get('friends', {})
                    self.blocked_users = set(data.get('blocked', []))
            except Exception as e:
                print(f"❌ Ошибка загрузки друзей: {e}")
    
    def save_friends(self):
        """Сохранение списка друзей"""
        try:
            data = {
                'friends': self.friends,
                'blocked': list(self.blocked_users)
            }
            with open(self.friends_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Ошибка сохранения друзей: {e}")
    
    def load_pending_requests(self):
        """Загрузка входящих заявок"""
        if os.path.exists(self.requests_file):
            try:
                with open(self.requests_file, 'r', encoding='utf-8') as f:
                    self.pending_requests = json.load(f)
            except Exception as e:
                print(f"❌ Ошибка загрузки заявок: {e}")
                self.pending_requests = {}
    
    def save_pending_requests(self):
        """Сохранение входящих заявок"""
        try:
            with open(self.requests_file, 'w', encoding='utf-8') as f:
                json.dump(self.pending_requests, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Ошибка сохранения заявок: {e}")
    
    def add_friend(self, friend_id: str, display_name: str = None) -> bool:
        """Добавление друга"""
        if friend_id in self.friends:
            return False
        
        self.friends[friend_id] = {
            'id': friend_id,
            'display_name': display_name or friend_id,
            'nickname': display_name or friend_id,
            'added_at': time.time(),
            'status': FriendStatus.OFFLINE,
            'chat_history': []
        }
        
        self.save_friends()
        self.friend_added.emit(friend_id, self.friends[friend_id]['display_name'])
        return True
    
    def remove_friend(self, friend_id: str) -> bool:
        """Удаление друга"""
        if friend_id not in self.friends:
            return False
        
        del self.friends[friend_id]
        self.online_friends.discard(friend_id)
        self.save_friends()
        self.friend_removed.emit(friend_id)
        return True
    
    def send_friend_request(self, target: str, message: str = "") -> bool:
        """Отправка заявки"""
        if target in self.friends:
            return False
        
        if target in self.blocked_users:
            return False
        
        # Проверяем, есть ли уже заявка
        for req in self.pending_requests.values():
            if req.get('from') == target:
                return False
        
        if self.network:
            return self.network.send_friend_request(target, message)
        return False
    
    def accept_friend_request(self, from_id: str) -> bool:
        """Принятие заявки"""
        if from_id not in self.pending_requests:
            return False
        
        if self.add_friend(from_id):
            del self.pending_requests[from_id]
            self.save_pending_requests()
            if self.network:
                self.network.respond_friend_request(from_id, True)
            self.friend_request_responded.emit(from_id, True)
            return True
        return False
    
    def reject_friend_request(self, from_id: str) -> bool:
        """Отклонение заявки"""
        if from_id not in self.pending_requests:
            return False
        
        del self.pending_requests[from_id]
        self.save_pending_requests()
        if self.network:
            self.network.respond_friend_request(from_id, False)
        self.friend_request_responded.emit(from_id, False)
        return True
    
    def get_friends_list(self) -> List[dict]:
        """Список друзей"""
        return list(self.friends.values())
    
    def get_pending_requests(self) -> List[dict]:
        """Список входящих заявок"""
        return list(self.pending_requests.values())
    
    def get_friend_status(self, friend_id: str) -> str:
        """Статус друга"""
        if friend_id in self.friends:
            return self.friends[friend_id].get('status', FriendStatus.OFFLINE)
        return FriendStatus.OFFLINE
    
    def get_friend_display_name(self, friend_id: str) -> str:
        """Отображаемое имя друга"""
        if friend_id in self.friends:
            return self.friends[friend_id].get('display_name', friend_id)
        return friend_id
    
    def is_friend(self, user_id: str) -> bool:
        """Проверка, является ли пользователь другом"""
        return user_id in self.friends
    
    def is_online(self, user_id: str) -> bool:
        """Проверка, онлайн ли пользователь"""
        return user_id in self.online_friends
    
    def save_chat_history(self, friend_id: str, message: dict):
        """Сохранение сообщения в историю"""
        if friend_id in self.friends:
            if 'chat_history' not in self.friends[friend_id]:
                self.friends[friend_id]['chat_history'] = []
            self.friends[friend_id]['chat_history'].append(message)
            self.save_friends()
    
    def get_chat_history(self, friend_id: str) -> List[dict]:
        """Получение истории переписки"""
        if friend_id in self.friends:
            return self.friends[friend_id].get('chat_history', [])
        return []
    
    def restore_chat_history(self, friend_id: str, history: List[dict]):
        """Восстановление истории от друга"""
        if friend_id in self.friends:
            self.friends[friend_id]['chat_history'] = history
            self.save_friends()
    
    # ========== ОБРАБОТЧИКИ СИГНАЛОВ ==========
    
    def _on_friend_request(self, from_id: str, message: str, display_name: str):
        """Входящая заявка"""
        if from_id in self.blocked_users:
            return
        
        self.pending_requests[from_id] = {
            'from': from_id,
            'message': message,
            'display_name': display_name or from_id,
            'timestamp': time.time()
        }
        self.save_pending_requests()
        self.friend_request_received.emit(from_id, display_name or from_id, message)
    
    def _on_friend_response(self, from_id: str, accepted: bool):
        """Ответ на заявку"""
        if accepted:
            self.add_friend(from_id)
        self.friend_request_responded.emit(from_id, accepted)
    
    def _on_online(self, friend_id: str):
        """Друг онлайн"""
        self.online_friends.add(friend_id)
        if friend_id in self.friends:
            self.friends[friend_id]['status'] = FriendStatus.ONLINE
            self.friend_status_changed.emit(friend_id, FriendStatus.ONLINE)
            self.save_friends()
    
    def _on_offline(self, friend_id: str):
        """Друг оффлайн"""
        self.online_friends.discard(friend_id)
        if friend_id in self.friends:
            self.friends[friend_id]['status'] = FriendStatus.OFFLINE
            self.friend_status_changed.emit(friend_id, FriendStatus.OFFLINE)
            self.save_friends()
    
    def _on_message(self, chat_id: str, message: dict):
        """Входящее сообщение"""
        users = chat_id.split('_')
        friend_id = users[0] if users[1] == self.username else users[1]
        self.save_chat_history(friend_id, message)