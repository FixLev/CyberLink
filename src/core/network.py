# src/core/network.py
# P2P сеть - ПО РЕАЛЬНО РАБОТАЮЩЕМУ ПРИМЕРУ

import json
import time
import socket
import threading
import random
from typing import Optional, Dict
from PyQt5.QtCore import QObject, pyqtSignal


class P2PNetwork(QObject):
    """P2P сеть - по образу работающего чата с GitHub"""
    
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
        
        # Порт - ФИКСИРОВАННЫЙ 3333 (как в примере)
        self.port = 3333
        
        # Хост
        self.host = "0.0.0.0"
        
        # Локальный IP
        self.local_ip = self._get_local_ip()
        
        # Кэш найденных пользователей
        self.discovered_users: Dict[str, dict] = {}
        
        print(f"🔌 ПОРТ: {self.port}")
        print(f"🌐 IP: {self.local_ip}")
        
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
        
        # Запускаем сервер (как в примере)
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        
        # Запускаем клиент (как в примере)
        self.client_thread = threading.Thread(target=self._run_client, daemon=True)
        self.client_thread.start()
        
        print(f"🚀 P2P сеть запущена для {self.username} на порту {self.port}")
        print(f"   🌐 IP: {self.local_ip}")
        print("   💡 Используйте 'connect IP' для подключения к другому пользователю")
    
    def _run_server(self):
        """Сервер для приема сообщений (как в примере)"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1)
            
            print(f"✅ СЕРВЕР ЗАПУЩЕН НА ПОРТУ {self.port}")
            
            while self.is_running:
                try:
                    conn, addr = self.server_socket.accept()
                    print(f"📥 ПОДКЛЮЧЕНИЕ ОТ {addr[0]}:{addr[1]}")
                    threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"⚠️ Ошибка сервера: {e}")
                    break
        except Exception as e:
            print(f"❌ Не удалось запустить сервер: {e}")
    
    def _handle_client(self, conn, addr):
        """Обработка клиента (как в примере)"""
        try:
            # Получаем данные
            data = conn.recv(4096)
            if data:
                try:
                    message = json.loads(data.decode())
                    from_id = message.get('from')
                    
                    if from_id:
                        # Запоминаем соединение
                        if from_id not in self.active_connections:
                            self.active_connections[from_id] = {
                                'ip': addr[0],
                                'port': self.port,
                                'last_ping': time.time()
                            }
                            print(f"🔗 СОЕДИНЕНИЕ С {from_id}")
                            self.friend_online.emit(from_id)
                        
                        self._process_incoming_message(message, addr[0])
                except json.JSONDecodeError:
                    print(f"⚠️ Некорректные данные от {addr[0]}")
            
            conn.close()
        except Exception as e:
            print(f"⚠️ Ошибка обработки клиента: {e}")
    
    def _run_client(self):
        """Клиент для подключения к другим (как в примере)"""
        # Создаём клиентский сокет
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(1)
        
        while self.is_running:
            try:
                # Проверяем, есть ли сообщения для отправки
                for peer_id, messages in list(self.pending_messages.items()):
                    if peer_id in self.active_connections:
                        ip = self.active_connections[peer_id].get('ip')
                        if ip:
                            try:
                                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                                    s.settimeout(2)
                                    s.connect((ip, self.port))
                                    for msg in messages:
                                        s.send(json.dumps(msg).encode())
                                    self.pending_messages[peer_id] = []
                            except Exception as e:
                                print(f"⚠️ Ошибка отправки {peer_id}: {e}")
                
                # Проверяем активные соединения
                for peer_id in list(self.active_connections.keys()):
                    if time.time() - self.active_connections[peer_id].get('last_ping', 0) > 60:
                        del self.active_connections[peer_id]
                        self.friend_offline.emit(peer_id)
                
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ Ошибка клиента: {e}")
                time.sleep(1)
    
    def _process_incoming_message(self, data: dict, from_ip: str = None):
        """Обработка входящего сообщения"""
        try:
            msg_type = data.get('type')
            from_id = data.get('from')
            
            if not from_id:
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
                response = {'type': 'pong', 'from': self.username}
                self._send_direct(from_id, response)
            
            elif msg_type == 'pong':
                if from_id in self.active_connections:
                    self.active_connections[from_id]['last_ping'] = time.time()
                
        except Exception as e:
            print(f"❌ Ошибка обработки сообщения: {e}")
    
    def _send_direct(self, peer_id: str, data: dict) -> bool:
        """Отправка данных напрямую"""
        try:
            if peer_id in self.active_connections:
                ip = self.active_connections[peer_id].get('ip')
                if ip:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(3)
                        s.connect((ip, self.port))
                        s.send(json.dumps(data).encode())
                        return True
            
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
    
    def connect_to_peer(self, ip: str, port: int = 3333) -> bool:
        """Подключение к другому пользователю (как в примере)"""
        try:
            print(f"🔗 ПОДКЛЮЧЕНИЕ К {ip}:{port}")
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect((ip, port))
                
                # Отправляем информацию о себе
                init_data = {
                    'type': 'init',
                    'from': self.username,
                    'timestamp': time.time()
                }
                s.send(json.dumps(init_data).encode())
                
                # Сохраняем соединение
                self.active_connections[self.username] = {
                    'ip': ip,
                    'port': port,
                    'last_ping': time.time()
                }
                
                print(f"✅ ПОДКЛЮЧЕНО К {ip}:{port}")
                return True
                
        except Exception as e:
            print(f"❌ Ошибка подключения к {ip}:{port}: {e}")
            return False
    
    def find_user(self, username: str) -> Optional[dict]:
        """Поиск пользователя (проверяем активные соединения)"""
        try:
            if username.startswith('@'):
                username = username[1:]
            
            print(f"🔍 ПОИСК ПОЛЬЗОВАТЕЛЯ {username}")
            
            if username in self.active_connections:
                print(f"   ✅ {username} В АКТИВНЫХ СОЕДИНЕНИЯХ")
                return {'username': username, 'exists': True, 'active': True}
            
            print(f"   ❌ {username} НЕ НАЙДЕН")
            return None
            
        except Exception as e:
            print(f"⚠️ Ошибка поиска {username}: {e}")
            return None
    
    def send_friend_request(self, target: str, message: str = "") -> bool:
        """Отправка заявки"""
        if target.startswith('@'):
            target = target[1:]
        
        print(f"📨 ОТПРАВКА ЗАЯВКИ {target}")
        
        user_info = self.find_user(target)
        if not user_info:
            print(f"❌ {target} НЕ НАЙДЕН")
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
        if peer_id in self.active_connections:
            return self.active_connections[peer_id].get('ip')
        return None
    
    def stop(self):
        self.is_running = False
        if hasattr(self, 'server_socket'):
            try:
                self.server_socket.close()
            except:
                pass
        if hasattr(self, 'client_socket'):
            try:
                self.client_socket.close()
            except:
                pass
        print("🛑 P2P сеть остановлена")