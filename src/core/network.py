# src/core/network.py
# P2P сеть - С ЛОКАЛЬНЫМ РЕЕСТРОМ IP

import json
import time
import socket
import threading
import os
from typing import Optional, Dict
from PyQt5.QtCore import QObject, pyqtSignal


class P2PNetwork(QObject):
    """P2P сеть - с локальным реестром IP"""
    
    # Сигналы
    friend_request_received = pyqtSignal(str, str, str)
    friend_request_response = pyqtSignal(str, bool)
    message_received = pyqtSignal(str, dict)
    friend_online = pyqtSignal(str)
    friend_offline = pyqtSignal(str)
    
    def __init__(self, username: str):
        super().__init__()
        self.username = username
        self.is_running = False
        
        # Подключения
        self.connections: Dict[str, dict] = {}  # username -> {ip, port, connected}
        self.pending_requests: Dict[str, list] = {}  # username -> [messages]
        
        # Порт
        self.port = 3333
        self.host = ""
        
        # Сокет сервера
        self.server_socket = None
        
        self.local_ip = self._get_local_ip()
        
        # Файл с IP пользователей
        self.registry_file = os.path.join("data", "user_ips.json")
        self._load_registry()
        
        # Сохраняем свой IP
        self._save_my_ip()
        
        print(f"🌐 IP: {self.local_ip}")
        print(f"🔌 ПОРТ: {self.port}")
        
        self.start_network()
    
    def _get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _load_registry(self):
        """Загрузка реестра IP"""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    self.registry = json.load(f)
                print(f"📋 Загружено {len(self.registry)} IP-адресов")
                return
            except:
                pass
        self.registry = {}
    
    def _save_registry(self):
        """Сохранение реестра IP"""
        try:
            os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения реестра: {e}")
    
    def _save_my_ip(self):
        """Сохранение своего IP"""
        self.registry[self.username] = {
            'ip': self.local_ip,
            'port': self.port,
            'last_seen': time.time()
        }
        self._save_registry()
        print(f"💾 Сохранён IP: {self.username} -> {self.local_ip}:{self.port}")
    
    def start_network(self):
        """Запуск сети"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Запускаем сервер
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        
        # Запускаем обработку очереди
        self.process_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.process_thread.start()
        
        print(f"🚀 P2P сеть запущена на порту {self.port}")
    
    def _run_server(self):
        """Сервер для приема сообщений"""
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
                try:
                    message = json.loads(data.decode())
                    from_user = message.get('from')
                    
                    if from_user:
                        # Сохраняем IP отправителя
                        if from_user not in self.connections:
                            self.connections[from_user] = {
                                'ip': addr[0],
                                'connected': True,
                                'last_seen': time.time()
                            }
                            print(f"🔗 ПОДКЛЮЧИЛСЯ {from_user} ({addr[0]})")
                            self.friend_online.emit(from_user)
                            
                            # Обновляем реестр
                            self.registry[from_user] = {
                                'ip': addr[0],
                                'port': self.port,
                                'last_seen': time.time()
                            }
                            self._save_registry()
                        
                        self._process_message(message)
                        
                except json.JSONDecodeError:
                    print(f"⚠️ Некорректные данные от {addr[0]}")
            
            conn.close()
        except Exception as e:
            print(f"⚠️ Ошибка обработки соединения: {e}")
    
    def _process_loop(self):
        """Обработка очереди сообщений"""
        while self.is_running:
            try:
                # Отправляем накопившиеся сообщения
                for user, messages in list(self.pending_requests.items()):
                    if user in self.connections and self.connections[user].get('connected'):
                        for msg in messages:
                            self._send_direct(user, msg)
                        self.pending_requests[user] = []
                
                # Проверяем соединения
                for user in list(self.connections.keys()):
                    if time.time() - self.connections[user].get('last_seen', 0) > 60:
                        self.connections[user]['connected'] = False
                        self.friend_offline.emit(user)
                
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Ошибка в цикле обработки: {e}")
                time.sleep(2)
    
    def _process_message(self, data: dict):
        """Обработка входящего сообщения"""
        try:
            msg_type = data.get('type')
            from_user = data.get('from')
            
            if not from_user:
                return
            
            # Обновляем время последнего контакта
            if from_user in self.connections:
                self.connections[from_user]['last_seen'] = time.time()
                self.connections[from_user]['connected'] = True
            
            if msg_type == 'friend_request':
                print(f"📨 ЗАЯВКА ОТ {from_user}")
                self.friend_request_received.emit(
                    from_user,
                    data.get('content', {}).get('message', ''),
                    from_user
                )
            
            elif msg_type == 'friend_response':
                print(f"📨 ОТВЕТ ОТ {from_user}: {data.get('content', {}).get('accepted', False)}")
                self.friend_request_response.emit(
                    from_user,
                    data.get('content', {}).get('accepted', False)
                )
            
            elif msg_type == 'message':
                print(f"💬 СООБЩЕНИЕ ОТ {from_user}")
                self.message_received.emit(
                    data.get('content', {}).get('chat_id'),
                    data.get('content', {}).get('message', {})
                )
            
            elif msg_type == 'ping':
                response = {'type': 'pong', 'from': self.username}
                self._send_direct(from_user, response)
            
            elif msg_type == 'pong':
                if from_user in self.connections:
                    self.connections[from_user]['connected'] = True
                    self.friend_online.emit(from_user)
                    
        except Exception as e:
            print(f"❌ Ошибка обработки сообщения: {e}")
    
    def _send_direct(self, target_user: str, data: dict) -> bool:
        """Отправка данных напрямую"""
        try:
            # Проверяем соединение
            if target_user in self.connections:
                ip = self.connections[target_user].get('ip')
                if ip:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(3)
                        s.connect((ip, self.port))
                        s.send(json.dumps(data).encode())
                        return True
            
            # Если нет соединения, но есть IP в реестре
            if target_user in self.registry:
                ip = self.registry[target_user].get('ip')
                if ip:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(3)
                        s.connect((ip, self.port))
                        s.send(json.dumps(data).encode())
                        # Сохраняем соединение
                        self.connections[target_user] = {
                            'ip': ip,
                            'connected': True,
                            'last_seen': time.time()
                        }
                        print(f"🔗 ПОДКЛЮЧЕНО К {target_user} ({ip})")
                        return True
            
            return False
        except Exception as e:
            print(f"⚠️ Ошибка отправки {target_user}: {e}")
            return False
    
    def find_user(self, username: str) -> Optional[dict]:
        """Поиск пользователя"""
        try:
            if username.startswith('@'):
                username = username[1:]
            
            # Проверяем локальный реестр пользователей
            from src.core.user_manager import UserManager
            um = UserManager()
            if not um.user_exists(username):
                print(f"❌ {username} НЕ СУЩЕСТВУЕТ")
                return None
            
            # Проверяем, есть ли IP в реестре
            if username in self.registry:
                ip = self.registry[username].get('ip')
                if ip:
                    print(f"✅ Найден IP для {username}: {ip}")
                    # Добавляем в соединения
                    if username not in self.connections:
                        self.connections[username] = {
                            'ip': ip,
                            'connected': False,
                            'last_seen': 0
                        }
                    return {'username': username, 'exists': True, 'ip': ip}
            
            # Если IP не найден, но пользователь существует
            print(f"⚠️ IP для {username} не найден, будет попытка подключения")
            if username not in self.connections:
                self.connections[username] = {
                    'ip': None,
                    'connected': False,
                    'last_seen': 0
                }
            
            return {'username': username, 'exists': True}
            
        except Exception as e:
            print(f"⚠️ Ошибка поиска {username}: {e}")
            return None
    
    def send_friend_request(self, target: str, message: str = "") -> bool:
        """Отправка заявки - С АВТОМАТИЧЕСКИМ ПОДКЛЮЧЕНИЕМ"""
        if target.startswith('@'):
            target = target[1:]
        
        print(f"📨 ОТПРАВКА ЗАЯВКИ {target}")
        
        # Проверяем существование пользователя
        user_info = self.find_user(target)
        if not user_info:
            print(f"❌ {target} НЕ НАЙДЕН")
            return False
        
        # Если есть IP, пробуем подключиться и отправить
        if user_info.get('ip'):
            print(f"✅ Найден IP для {target}: {user_info['ip']}")
            data = {
                'type': 'friend_request',
                'from': self.username,
                'to': target,
                'content': {'message': message}
            }
            success = self._send_direct(target, data)
            if success:
                print(f"✅ Заявка отправлена {target}")
                return True
            else:
                print(f"⚠️ Не удалось отправить заявку {target}, сохраняем в очередь")
        
        # Если нет IP или не удалось отправить - в очередь
        if target not in self.pending_requests:
            self.pending_requests[target] = []
        
        self.pending_requests[target].append({
            'type': 'friend_request',
            'from': self.username,
            'to': target,
            'content': {'message': message}
        })
        
        print(f"⏳ Заявка в очереди для {target}")
        return True
    
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
        
        # Пробуем отправить сразу
        if target in self.connections and self.connections[target].get('connected'):
            return self._send_direct(target, data)
        
        # Если нет соединения - в очередь
        if target not in self.pending_requests:
            self.pending_requests[target] = []
        self.pending_requests[target].append(data)
        
        return True
    
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
        
        if recipient in self.connections and self.connections[recipient].get('connected'):
            return self._send_direct(recipient, data)
        
        # В очередь
        if recipient not in self.pending_requests:
            self.pending_requests[recipient] = []
        self.pending_requests[recipient].append(data)
        
        return True
    
    def stop(self):
        self.is_running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print("🛑 P2P сеть остановлена")