# src/core/network.py
# P2P сеть - с разными портами для разных пользователей

import json
import time
import socket
import threading
import os
import hashlib
import random
from typing import Optional, Dict
from PyQt5.QtCore import QObject, pyqtSignal


class P2PNetwork(QObject):
    """P2P сеть - соединения только с активными собеседниками"""
    
    # Сигналы
    friend_request_received = pyqtSignal(str, str, str)
    friend_request_response = pyqtSignal(str, bool)
    message_received = pyqtSignal(str, dict)
    friend_online = pyqtSignal(str)
    friend_offline = pyqtSignal(str)
    history_requested = pyqtSignal(str)
    history_received = pyqtSignal(str, list)
    
    def __init__(self, username: str):
        super().__init__()
        self.username = username
        self.is_running = False
        
        # Активные соединения
        self.active_connections: Dict[str, dict] = {}
        self.pending_messages: Dict[str, list] = {}
        
        # Локальные данные
        self.local_ip = self._get_local_ip()
        self.port = self._find_free_port()
        
        # Ключи (упрощенные для демо)
        self.public_key = hashlib.sha256(username.encode()).digest()[:16]
        
        # Реестр пользователей (локальный кэш)
        self.user_cache = {}
        
        self.start_network()
    
    def _get_local_ip(self) -> str:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
    
    def _find_free_port(self) -> int:
        """Поиск свободного порта"""
        # Начинаем с 6881, но если занят - ищем дальше
        start_port = 6881
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except:
                continue
        # Если ничего не нашли - случайный порт
        return random.randint(10000, 60000)
    
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
        
        # Запускаем обновление реестра
        self.registry_thread = threading.Thread(target=self._registry_loop, daemon=True)
        self.registry_thread.start()
        
        print(f"🚀 P2P сеть запущена для {self.username} на порту {self.port}")
        print(f"   🌐 IP: {self.local_ip}")
    
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
                for peer_id, messages in list(self.pending_messages.items()):
                    if peer_id in self.active_connections:
                        for msg in messages:
                            self._send_direct(peer_id, msg)
                        self.pending_messages[peer_id] = []
                
                for peer_id in list(self.active_connections.keys()):
                    if time.time() - self.active_connections[peer_id].get('last_ping', 0) > 30:
                        if not self._ping_peer(peer_id):
                            del self.active_connections[peer_id]
                            self.friend_offline.emit(peer_id)
                
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Ошибка в цикле обработки: {e}")
                time.sleep(2)
    
    def _registry_loop(self):
        """Обновление локального реестра пользователей"""
        while self.is_running:
            try:
                # Обновляем информацию о себе
                from src.core.user_manager import UserManager
                um = UserManager()
                if um.user_exists(self.username):
                    # Сохраняем информацию о себе в кэш
                    self.user_cache[self.username] = {
                        'username': self.username,
                        'ip': self.local_ip,
                        'port': self.port,
                        'online': True,
                        'last_seen': time.time()
                    }
                
                # Получаем список всех пользователей
                all_users = um.get_all_users()
                for user in all_users:
                    if user != self.username and user not in self.user_cache:
                        # Пробуем найти пользователя в сети
                        self._discover_user(user)
                
                time.sleep(10)
            except Exception as e:
                print(f"⚠️ Ошибка обновления реестра: {e}")
                time.sleep(10)
    
    def _discover_user(self, username: str):
        """Обнаружение пользователя в сети"""
        try:
            # Пробуем разные порты
            for port in range(6881, 6891):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.5)
                        s.connect((self.local_ip, port))
                        # Отправляем запрос на идентификацию
                        ping_data = {
                            'type': 'discover',
                            'from': self.username,
                            'to': username,
                            'timestamp': time.time()
                        }
                        s.send(json.dumps(ping_data).encode())
                        # Ждём ответ
                        response = s.recv(1024)
                        if response:
                            data = json.loads(response.decode())
                            if data.get('type') == 'discover_response' and data.get('from') == username:
                                self.user_cache[username] = {
                                    'username': username,
                                    'ip': self.local_ip,
                                    'port': port,
                                    'online': True,
                                    'last_seen': time.time()
                                }
                                self.active_connections[username] = {
                                    'ip': self.local_ip,
                                    'last_ping': time.time()
                                }
                                print(f"✅ Обнаружен пользователь {username} на порту {port}")
                                self.friend_online.emit(username)
                                return
                except:
                    continue
        except Exception as e:
            pass
    
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
                print(f"📡 Новое соединение от {from_id}")
                self.friend_online.emit(from_id)
            else:
                self.active_connections[from_id]['last_ping'] = time.time()
            
            # Обрабатываем discovery
            if msg_type == 'discover':
                # Ответ на запрос обнаружения
                if data.get('to') == self.username:
                    response = {
                        'type': 'discover_response',
                        'from': self.username,
                        'to': from_id,
                        'timestamp': time.time()
                    }
                    self._send_direct(from_id, response)
                return
            
            if msg_type == 'discover_response':
                # Обнаружен пользователь
                if from_id not in self.user_cache:
                    self.user_cache[from_id] = {
                        'username': from_id,
                        'ip': from_ip,
                        'online': True,
                        'last_seen': time.time()
                    }
                    print(f"✅ Обнаружен пользователь {from_id}")
                    self.friend_online.emit(from_id)
                return
            
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
                response = {'type': 'pong', 'from': self.username, 'to': from_id}
                self._send_direct(from_id, response)
            
            elif msg_type == 'pong':
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
            
            # Если нет активного соединения - пробуем найти порт
            for port in range(6881, 6891):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(1)
                        s.connect((self.local_ip, port))
                        s.send(json.dumps(data).encode())
                        # Сохраняем порт для будущих соединений
                        self.active_connections[peer_id] = {
                            'ip': self.local_ip,
                            'last_ping': time.time()
                        }
                        return True
                except:
                    continue
            
            # Сохраняем в очередь
            if peer_id not in self.pending_messages:
                self.pending_messages[peer_id] = []
            self.pending_messages[peer_id].append(data)
            return False
            
        except Exception as e:
            print(f"⚠️ Ошибка отправки {peer_id}: {e}")
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
        """Поиск пользователя в сети"""
        try:
            if username.startswith('@'):
                username = username[1:]
            
            print(f"🔍 Поиск пользователя {username}...")
            
            # Проверяем кэш
            if username in self.user_cache:
                print(f"✅ Пользователь {username} найден в кэше")
                return self.user_cache[username]
            
            # Проверяем локальный реестр
            from src.core.user_manager import UserManager
            um = UserManager()
            if um.user_exists(username):
                print(f"✅ Пользователь {username} найден локально")
                # Пробуем обнаружить пользователя
                self._discover_user(username)
                if username in self.user_cache:
                    return self.user_cache[username]
                return {'username': username, 'exists': True, 'local': True}
            
            # Проверяем активные соединения
            if username in self.active_connections:
                print(f"✅ Пользователь {username} в активных соединениях")
                return {'username': username, 'exists': True, 'active': True}
            
            print(f"❌ Пользователь {username} не найден")
            return None
            
        except Exception as e:
            print(f"⚠️ Ошибка поиска {username}: {e}")
            return None
    
    def connect_to_peer(self, peer_id: str, ip: str):
        """Установка соединения с пиром"""
        self.active_connections[peer_id] = {
            'ip': ip,
            'last_ping': time.time()
        }
        self.friend_online.emit(peer_id)
        self._ping_peer(peer_id)
    
    def send_friend_request(self, target: str, message: str = "") -> bool:
        """Отправка заявки"""
        if target.startswith('@'):
            target = target[1:]
        
        print(f"📨 Отправка заявки пользователю {target}...")
        
        user_info = self.find_user(target)
        if not user_info:
            print(f"❌ Пользователь {target} не найден")
            return False
        
        if user_info.get('local') and target != self.username:
            print(f"❌ Пользователь {target} не активен в сети")
            return False
        
        print(f"✅ Пользователь {target} найден, отправляем заявку...")
        
        data = {
            'type': 'friend_request',
            'from': self.username,
            'to': target,
            'content': {'message': message}
        }
        return self._send_direct(target, data)
    
    def respond_friend_request(self, target: str, accepted: bool) -> bool:
        """Ответ на заявку"""
        if target.startswith('@'):
            target = target[1:]
        
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