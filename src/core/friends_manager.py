# src/core/friends_manager.py
# Менеджер друзей - только локальные данные

import time
from typing import Dict, List, Optional
from PyQt5.QtCore import QObject, pyqtSignal


class FriendStatus:
    ONLINE = "online"
    OFFLINE = "offline"


class FriendsManager(QObject):
    """Менеджер друзей - хранит только друзей пользователя"""
    
    friend_added = pyqtSignal(str, str)
    friend_removed = pyqtSignal(str)
    friend_status_changed = pyqtSignal(str, str)
    friend_request_received = pyqtSignal(str, str, str)
    friend_request_responded = pyqtSignal(str, bool)
    
    def __init__(self, username: str, storage, network=None):
        super().__init__()
        self.username = username
        self.storage = storage
        self.network = network
        
        self.friends: Dict[str, dict] = {}
        self.pending_requests: Dict[str, dict] = {}
        self.online_friends: set = set()
        self.blocked_users: set = set()
        
        self._load_data()
        
        if self.network:
            self._connect_signals()
    
    def _connect_signals(self):
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
    
    def _load_data(self):
        data = self.storage.load('friends.json')
        self.friends = data.get('friends', {})
        self.blocked_users = set(data.get('blocked', []))
        
        requests_data = self.storage.load('friend_requests.json')
        self.pending_requests = requests_data.get('pending', {})
    
    def _save_data(self):
        data = {'friends': self.friends, 'blocked': list(self.blocked_users)}
        self.storage.save('friends.json', data)
    
    def _save_requests(self):
        data = {'pending': self.pending_requests}
        self.storage.save('friend_requests.json', data)
    
    def add_friend(self, friend_id: str, display_name: str = None) -> bool:
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
        self._save_data()
        self.friend_added.emit(friend_id, self.friends[friend_id]['display_name'])
        return True
    
    def remove_friend(self, friend_id: str) -> bool:
        if friend_id not in self.friends:
            return False
        
        del self.friends[friend_id]
        self.online_friends.discard(friend_id)
        self._save_data()
        self.friend_removed.emit(friend_id)
        return True
    
    def send_friend_request(self, target: str, message: str = "") -> bool:
        if target in self.friends or target in self.blocked_users:
            return False
        
        for req in self.pending_requests.values():
            if req.get('from') == target:
                return False
        
        if self.network:
            return self.network.send_friend_request(target, message)
        return False
    
    def accept_friend_request(self, from_id: str) -> bool:
        if from_id not in self.pending_requests:
            return False
        
        if self.add_friend(from_id):
            del self.pending_requests[from_id]
            self._save_requests()
            if self.network:
                self.network.respond_friend_request(from_id, True)
            self.friend_request_responded.emit(from_id, True)
            return True
        return False
    
    def reject_friend_request(self, from_id: str) -> bool:
        if from_id not in self.pending_requests:
            return False
        
        del self.pending_requests[from_id]
        self._save_requests()
        if self.network:
            self.network.respond_friend_request(from_id, False)
        self.friend_request_responded.emit(from_id, False)
        return True
    
    def get_friends_list(self) -> List[dict]:
        return list(self.friends.values())
    
    def get_pending_requests(self) -> List[dict]:
        return list(self.pending_requests.values())
    
    def get_friend_status(self, friend_id: str) -> str:
        if friend_id in self.friends:
            return self.friends[friend_id].get('status', FriendStatus.OFFLINE)
        return FriendStatus.OFFLINE
    
    def get_friend_display_name(self, friend_id: str) -> str:
        if friend_id in self.friends:
            return self.friends[friend_id].get('display_name', friend_id)
        return friend_id
    
    def is_friend(self, user_id: str) -> bool:
        return user_id in self.friends
    
    def is_online(self, user_id: str) -> bool:
        return user_id in self.online_friends
    
    def save_chat_history(self, friend_id: str, message: dict):
        if friend_id in self.friends:
            if 'chat_history' not in self.friends[friend_id]:
                self.friends[friend_id]['chat_history'] = []
            self.friends[friend_id]['chat_history'].append(message)
            self._save_data()
    
    def get_chat_history(self, friend_id: str) -> List[dict]:
        if friend_id in self.friends:
            return self.friends[friend_id].get('chat_history', [])
        return []
    
    def restore_chat_history(self, friend_id: str, history: List[dict]):
        if friend_id in self.friends:
            self.friends[friend_id]['chat_history'] = history
            self._save_data()
    
    def _on_friend_request(self, from_id: str, message: str, display_name: str):
        if from_id in self.blocked_users:
            return
        
        self.pending_requests[from_id] = {
            'from': from_id,
            'message': message,
            'display_name': display_name or from_id,
            'timestamp': time.time()
        }
        self._save_requests()
        self.friend_request_received.emit(from_id, display_name or from_id, message)
    
    def _on_friend_response(self, from_id: str, accepted: bool):
        if accepted:
            self.add_friend(from_id)
        self.friend_request_responded.emit(from_id, accepted)
    
    def _on_online(self, friend_id: str):
        self.online_friends.add(friend_id)
        if friend_id in self.friends:
            self.friends[friend_id]['status'] = FriendStatus.ONLINE
            self.friend_status_changed.emit(friend_id, FriendStatus.ONLINE)
            self._save_data()
    
    def _on_offline(self, friend_id: str):
        self.online_friends.discard(friend_id)
        if friend_id in self.friends:
            self.friends[friend_id]['status'] = FriendStatus.OFFLINE
            self.friend_status_changed.emit(friend_id, FriendStatus.OFFLINE)
            self._save_data()
    
    def _on_message(self, chat_id: str, message: dict):
        users = chat_id.split('_')
        friend_id = users[0] if users[1] == self.username else users[1]
        self.save_chat_history(friend_id, message)