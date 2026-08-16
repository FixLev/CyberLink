# src/core/network.py
# P2P сеть - КАК RADMIN/HAMACHI (все видят всех)

import json
import time
import socket
import threading
import os
from typing import Optional, Dict
from PyQt5.QtCore import QObject, pyqtSignal


class P2PNetwork(QObject):
    """P2P сеть - как Radmin (все пользователи в общем реестре)"""
    
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
        self.connections: Dict[str, dict] = {}
        self.pending_requests: Dict[str, list] = {}
        
        # Порт
        self.port = 3333
        self.host = ""
        self.server_socket = None
        
        self.local_ip = self._get_local_ip()
        
        # ОБЩИЙ РЕЕСТР ВСЕХ ПОЛЬЗОВАТЕЛЕЙ
        self.registry_file = os.path.join("data", "network_registry.json")
        self._load_registry()
        
        # РЕГИСТРИРУЕМ СЕБЯ
        self._register_me()
        
        print(f"🌐 IP: {self.local_ip}")
        print(f"🔌 ПОРТ: {self.port}")
        print(f"📋 Всего пользователей в сети: {len(self.registry)}")
        
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
        """Загрузка общего реестра"""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    self.registry = json.load(f)
                print(f"📋 Загружен реестр: {len(self.registry)} пользователей")
                return
            except:
                pass
        self.registry = {}
    
    def _save_registry(self):
        """Сохранение общего реестра"""
        try:
            os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения реестра: {e}")
    
    def _register_me(self):
        """Регистрация себя в общем реестре"""
        self.registry[self.username] = {
            'ip': self.local_ip,
            'port': self.port,
            'online': True,
            'last_seen': time.time()
        }
        self._save_registry()
        print(f"✅ ЗАРЕГИСТРИРОВАН: {self.username} -> {self.local_ip}:{self.port}")
    
    def _unregister_me(self):
        """Удаление себя из реестра"""
        if self.username in self.registry:
            del self.registry[self.username]
            self._save_registry()
            print(f"❌ Удалён из реестра: {self.username}")
    
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
        
        # Запускаем обновление статуса
        self.status_thread = threading.Thread(target=self._status_loop, daemon=True)
        self.status_thread.start()
        
        print(f"🚀 P2P сеть запущена на порту {self.port}")
        print(f"📋 Пользователи в сети: {self._get_online_users()}")
    
    def _get_online_users(self) -> list:
        """Получение списка онлайн пользователей"""
        online = []
        for user, data in self.registry.items():
            if user != self.username and data.get('online', False):
                online.append(user)
        return online
    
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
                    
                    if from_user and from_user != self.username:
                        # Обновляем статус в реестре
                        if from_user in self.registry:
                            self.registry[from_user]['online'] = True
                            self.registry[from_user]['last_seen'] = time.time()
                            self._save_registry()
                        
                        # Сохраняем соединение
                        if from_user not in self.connections:
                            self.connections[from_user] = {
                                'ip': addr[0],
                                'connected': True,
                                'last_seen': time.time()
                            }
                            print(f"🔗 ПОДКЛЮЧИЛСЯ {from_user} ({addr[0]})")
                            self.friend_online.emit(from_user)
                        
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
                        if user in self.registry:
                            self.registry[user]['online'] = False
                            self._save_registry()
                
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Ошибка в цикле обработки: {e}")
                time.sleep(2)
    
    def _status_loop(self):
        """Обновление статуса в реестре"""
        while self.is_running:
            try:
                # Обновляем свой статус
                if self.username in self.registry:
                    self.registry[self.username]['online'] = True
                    self.registry[self.username]['last_seen'] = time.time()
                    self._save_registry()
                
                # Выводим список онлайн пользователей
                online = self._get_online_users()
                if online:
                    print(f"👥 Онлайн: {', '.join(online)}")
                
                time.sleep(30)
            except Exception as e:
                print(f"⚠️ Ошибка статуса: {e}")
                time.sleep(30)
    
    def _process_message(self, data: dict):
        """Обработка входящего сообщения"""
        try:
            msg_type = data.get('type')
            from_user = data.get('from')
            
            if not from_user:
                return
            
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
            # Проверяем реестр для получения IP
            if target_user in self.registry:
                ip = self.registry[target_user].get('ip')
                if ip:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(3)
                        s.connect((ip, self.port))
                        s.send(json.dumps(data).encode())
                        return True
            
            return False
        except Exception as e:
            print(f"⚠️ Ошибка отправки {target_user}: {e}")
            return False
    
    def find_user(self, username: str) -> Optional[dict]:
        """Поиск пользователя в реестре"""
        try:
            if username.startswith('@'):
                username = username[1:]
            
            # Проверяем локальный реестр пользователей
            from src.core.user_manager import UserManager
            um = UserManager()
            if not um.user_exists(username):
                print(f"❌ {username} НЕ СУЩЕСТВУЕТ")
                return None
            
            # Проверяем реестр сети
            if username in self.registry:
                ip = self.registry[username].get('ip')
                online = self.registry[username].get('online', False)
                print(f"✅ Найден {username} в сети: IP={ip}, online={online}")
                return {
                    'username': username,
                    'exists': True,
                    'ip': ip,
                    'online': online
                }
            
            # Если пользователь есть в системе, но не в реестре
            print(f"⚠️ {username} существует, но не в сети")
            return {'username': username, 'exists': True, 'online': False}
            
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
        
        if not user_info.get('online'):
            print(f"❌ {target} НЕ В СЕТИ (офлайн)")
            return False
        
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
            print(f"⚠️ Не удалось отправить заявку {target}")
            return False
    
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
    
    def stop(self):
        self.is_running = False
        self._unregister_me()
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print("🛑 P2P сеть остановлена")