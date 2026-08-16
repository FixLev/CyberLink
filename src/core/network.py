# src/core/network.py
# P2P сеть - только между активными собеседниками

import json
import time
import socket
import threading
import os
import hashlib
from typing import Optional, Dict
from PyQt5.QtCore import QObject, pyqtSignal


class P2PNetwork(QObject):
    """P2P сеть - соединения только с активными собеседниками"""
    
    # Сигналы
    friend_request_received = pyqtSignal(str, str, str)  # (from_id, message, display_name)
    friend_request_response = pyqtSignal(str, bool)  # (from_id, accepted)
    message_received = pyqtSignal(str, dict)  # (chat_id, message)
    friend_online = pyqtSignal(str)  # (friend_id)
    friend_offline = pyqtSignal(str)  # (friend_id)
    history_requested = pyqtSignal(str)  # (from_id)
    history_received = pyqtSignal(str, list)  # (from_id, history)
    
    def __init__(self, username: str):
        super().__init__()
        self.username = username
        self.is_running = False
        
        # Активные соединения
        self.active_connections: Dict[str, dict] = {}  # peer_id -> {ip, port, last_ping}
        
        # Очередь сообщений для оффлайн
        self.pending_messages: Dict[str, list] = {}
        
        # Локальные данные
        self.local_ip = self._get_local_ip()
        self.port = 6881
        
        # Ключи (упрощенные для демо)
        self.public_key = hashlib.sha256(username.encode()).digest()[:16]
        
        self.start_network()
    
    def _get_local_ip(self) -> str:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
    
    def start_network(self):
        """Запуск сети"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Запускаем сервер для приема сообщений
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        
        # Запускаем обработку очереди
        self.process_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.process_thread.start()
        
        print(f"🚀 P2P сеть запущена для @{self.username} на порту {self.port}")
    
    def _run_server(self):
        """Сервер для приема сообщений"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', self.port))
                s.listen(5)
                s.settimeout(1)
                
                while self.is_running:
                    try:
                        conn, addr = s.accept()
                        threading.Thread(target=self._handle_connection, args=(conn, addr), daemon=True).start()
                    except socket.timeout:
                        continue
                    except Exception as e:
                        print(f"⚠️ Ошибка сервера: {e}")
                        break
        except Exception as e:
            print(f"❌ Не удалось запустить сервер: {e}")
    
    def _handle_connection(self, conn, addr):
        """Обработка входящего соединения"""
        try:
            data = conn.recv(65536)
            if data:
                message = json.loads(data.decode())
                self._process_incoming_message(message, addr[0])
            conn.close()
        except Exception as e:
            print(f"⚠️ Ошибка обработки соединения: {e}")
    
    def _process_loop(self):
        """Обработка очереди сообщений"""
        while self.is_running:
            try:
                # Отправляем накопившиеся сообщения
                for peer_id, messages in list(self.pending_messages.items()):
                    if peer_id in self.active_connections:
                        for msg in messages:
                            self._send_direct(peer_id, msg)
                        self.pending_messages[peer_id] = []
                
                # Проверяем активные соединения (пинг)
                for peer_id in list(self.active_connections.keys()):
                    if time.time() - self.active_connections[peer_id].get('last_ping', 0) > 30:
                        # Пробуем пинг
                        if not self._ping_peer(peer_id):
                            del self.active_connections[peer_id]
                            self.friend_offline.emit(peer_id)
                
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Ошибка в цикле обработки: {e}")
                time.sleep(2)
    
    def _process_incoming_message(self, data: dict, from_ip: str = None):
        """Обработка входящего сообщения"""
        try:
            msg_type = data.get('type')
            from_id = data.get('from')
            
            if not from_id:
                return
            
            # Обновляем активное соединение
            if from_id not in self.active_connections:
                self.active_connections[from_id] = {
                    'ip': from_ip or data.get('ip', ''),
                    'last_ping': time.time()
                }
                self.friend_online.emit(from_id)
            else:
                self.active_connections[from_id]['last_ping'] = time.time()
            
            if msg_type == 'friend_request':
                self.friend_request_received.emit(
                    from_id,
                    data.get('content', {}).get('message', ''),
                    from_id
                )
            
            elif msg_type == 'friend_response':
                self.friend_request_response.emit(
                    from_id,
                    data.get('content', {}).get('accepted', False)
                )
            
            elif msg_type == 'message':
                self.message_received.emit(
                    data.get('content', {}).get('chat_id'),
                    data.get('content', {}).get('message', {})
                )
            
            elif msg_type == 'history_request':
                self.history_requested.emit(from_id)
            
            elif msg_type == 'history_response':
                history = data.get('content', {}).get('history', [])
                self.history_received.emit(from_id, history)
            
            elif msg_type == 'ping':
                # Ответ на пинг
                response = {'type': 'pong', 'from': self.username, 'to': from_id}
                self._send_direct(from_id, response)
            
            elif msg_type == 'pong':
                # Обновляем статус
                self.friend_online.emit(from_id)
                
        except Exception as e:
            print(f"❌ Ошибка обработки сообщения: {e}")
    
    def _send_direct(self, peer_id: str, data: dict) -> bool:
        """Отправка данных напрямую"""
        try:
            # Ищем пользователя в активных соединениях
            if peer_id in self.active_connections:
                ip = self.active_connections[peer_id].get('ip')
                if ip:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(3)
                        s.connect((ip, self.port))
                        s.send(json.dumps(data).encode())
                        return True
            
            # Если нет активного соединения - сохраняем в очередь
            if peer_id not in self.pending_messages:
                self.pending_messages[peer_id] = []
            self.pending_messages[peer_id].append(data)
            return False
            
        except Exception as e:
            print(f"⚠️ Ошибка отправки {peer_id}: {e}")
            # Сохраняем в очередь
            if peer_id not in self.pending_messages:
                self.pending_messages[peer_id] = []
            self.pending_messages[peer_id].append(data)
            return False
    
    def _ping_peer(self, peer_id: str) -> bool:
        """Пинг пира"""
        try:
            data = {'type': 'ping', 'from': self.username}
            return self._send_direct(peer_id, data)
        except:
            return False
    
    def find_user(self, username: str) -> Optional[dict]:
        """Поиск пользователя (проверяем существование)"""
        # Для демо - проверяем, есть ли в публичном списке
        from src.core.user_manager import UserManager
        um = UserManager()
        if um.user_exists(username):
            return {
                'username': username,
                'exists': True
            }
        return None
    
    def connect_to_peer(self, peer_id: str, ip: str):
        """Установка соединения с пиром"""
        self.active_connections[peer_id] = {
            'ip': ip,
            'last_ping': time.time()
        }
        self.friend_online.emit(peer_id)
        
        # Отправляем пинг для подтверждения
        self._ping_peer(peer_id)
    
    def send_friend_request(self, target: str, message: str = "") -> bool:
        """Отправка заявки"""
        user_info = self.find_user(target)
        if not user_info:
            print(f"❌ Пользователь @{target} не найден")
            return False
        
        data = {
            'type': 'friend_request',
            'from': self.username,
            'to': target,
            'content': {'message': message}
        }
        return self._send_direct(target, data)
    
    def respond_friend_request(self, target: str, accepted: bool) -> bool:
        """Ответ на заявку"""
        data = {
            'type': 'friend_response',
            'from': self.username,
            'to': target,
            'content': {'accepted': accepted}
        }
        return self._send_direct(target, data)
    
    def send_message(self, chat_id: str, message: dict) -> bool:
        """Отправка сообщения"""
        users = chat_id.split('_')
        recipient = users[0] if users[1] == self.username else users[1]
        
        data = {
            'type': 'message',
            'from': self.username,
            'to': recipient,
            'content': {
                'chat_id': chat_id,
                'message': message,
                'timestamp': time.time()
            }
        }
        return self._send_direct(recipient, data)
    
    def request_chat_history(self, friend_id: str) -> bool:
        """Запрос истории"""
        data = {
            'type': 'history_request',
            'from': self.username,
            'to': friend_id,
            'timestamp': time.time()
        }
        return self._send_direct(friend_id, data)
    
    def send_chat_history(self, friend_id: str, history: list) -> bool:
        """Отправка истории"""
        data = {
            'type': 'history_response',
            'from': self.username,
            'to': friend_id,
            'content': {
                'history': history,
                'count': len(history)
            },
            'timestamp': time.time()
        }
        return self._send_direct(friend_id, data)
    
    def get_peer_ip(self, peer_id: str) -> Optional[str]:
        """Получение IP пира"""
        if peer_id in self.active_connections:
            return self.active_connections[peer_id].get('ip')
        return None
    
    def stop(self):
        """Остановка сети"""
        self.is_running = False
        print("🛑 P2P сеть остановлена")