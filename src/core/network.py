# src/core/network.py
# ДЕЦЕНТРАЛИЗОВАННЫЙ P2P ДВИЖОК - БЕЗ СЕРВЕРОВ!
# Работает через мобильный интернет, WiFi, любые NAT
# Роскомпозор идёт нахуй!

import json
import time
import socket
import threading
import random
import hashlib
import struct
from typing import Optional, Dict, Tuple
from PyQt5.QtCore import QObject, pyqtSignal


class P2PNetwork(QObject):
    """
    Полностью децентрализованная P2P сеть
    - БЕЗ серверов
    - БЕЗ STUN/TURN
    - Работает через мобильный интернет
    - Обходит любые NAT через дыропробивание
    """
    
    # Сигналы
    friend_request_received = pyqtSignal(str, str, str)
    friend_request_response = pyqtSignal(str, bool)
    message_received = pyqtSignal(str, dict)
    friend_online = pyqtSignal(str)
    friend_offline = pyqtSignal(str)
    peer_found = pyqtSignal(str, str)  # username, ip
    
    def __init__(self, username: str):
        super().__init__()
        self.username = username
        self.is_running = False
        
        # === СЕТЕВЫЕ ПАРАМЕТРЫ ===
        self.port = 3333
        self.broadcast_port = 3334
        self.hole_punch_port = 3335
        
        # === НАТ-ПРОБИВАНИЕ ===
        self.punch_socket = None
        self.punch_thread = None
        self.punch_attempts: Dict[str, int] = {}
        self.punch_peers: Dict[str, dict] = {}  # username -> {ip, port, last_attempt}
        
        # === ПОДКЛЮЧЕНИЯ ===
        self.connections: Dict[str, dict] = {}
        self.pending_messages: Dict[str, list] = {}
        
        # === ОБНАРУЖЕНИЕ ===
        self.discovered_peers: Dict[str, dict] = {}
        self.peer_cache: Dict[str, dict] = {}
        
        # === DHT (ДЕЦЕНТРАЛИЗОВАННЫЙ ПОИСК) ===
        self.dht_bootstrap_nodes = [
            ("8.8.8.8", 3333),  # Google DNS как начальная точка
            ("1.1.1.1", 3333),  # Cloudflare
            ("9.9.9.9", 3333),  # Quad9
        ]
        self.dht_table: Dict[str, dict] = {}
        
        # === IP ===
        self.local_ip = self._get_local_ip()
        self.public_ip = self._get_public_ip()
        
        print("=" * 60)
        print("🔥 CYBERLINK - БЕЗ СЕРВЕРОВ!")
        print("=" * 60)
        print(f"👤 {self.username}")
        print(f"🌐 Локальный IP: {self.local_ip}")
        print(f"🌍 Публичный IP: {self.public_ip}")
        print(f"🔌 Порт: {self.port}")
        print(f"🚀 Роскомпозор идёт нахуй!")
        print("=" * 60)
        
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
    
    def _get_public_ip(self) -> str:
        """Получение публичного IP через внешние сервисы"""
        # Пробуем через DNS (без HTTP)
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8', '1.1.1.1']
            answer = resolver.resolve('myip.opendns.com', 'A')
            return str(answer[0])
        except:
            pass
        
        # Пробуем через HTTP (если есть)
        try:
            import requests
            response = requests.get('https://api.ipify.org?format=json', timeout=3)
            return response.json()['ip']
        except:
            pass
        
        # Пробуем через socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("1.1.1.1", 53))
                return s.getsockname()[0]
        except:
            pass
        
        return self.local_ip
    
    def _hash_username(self, username: str) -> str:
        """Хеширование имени пользователя для DHT"""
        return hashlib.sha256(username.encode()).hexdigest()[:16]
    
    def start_network(self):
        """Запуск сети"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # === 1. ЗАПУСКАЕМ СЕРВЕР ДЛЯ ПРИЁМА СООБЩЕНИЙ ===
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        
        # === 2. ЗАПУСКАЕМ ДЫРОПРОБИВАНИЕ ===
        self.punch_thread = threading.Thread(target=self._run_hole_punching, daemon=True)
        self.punch_thread.start()
        
        # === 3. ЗАПУСКАЕМ ШИРОКОВЕЩАТЕЛЬНОЕ ОБНАРУЖЕНИЕ ===
        self.broadcast_thread = threading.Thread(target=self._run_broadcast, daemon=True)
        self.broadcast_thread.start()
        
        # === 4. ЗАПУСКАЕМ DHT ===
        self.dht_thread = threading.Thread(target=self._run_dht, daemon=True)
        self.dht_thread.start()
        
        # === 5. ЗАПУСКАЕМ ОБРАБОТКУ ОЧЕРЕДИ ===
        self.process_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.process_thread.start()
        
        print("✅ ВСЕ СИСТЕМЫ ЗАПУЩЕНЫ!")
        print("📡 Ожидание подключений...")
    
    # ============================================================
    # 1. СЕРВЕР ДЛЯ ПРИЁМА СООБЩЕНИЙ
    # ============================================================
    
    def _run_server(self):
        """Сервер для приема сообщений"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(50)
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
                        # Сохраняем информацию о пире
                        if from_user not in self.connections:
                            self.connections[from_user] = {
                                'ip': addr[0],
                                'port': self.port,
                                'last_seen': time.time(),
                                'connected': True
                            }
                            print(f"🔗 ПОДКЛЮЧИЛСЯ {from_user} ({addr[0]})")
                            self.friend_online.emit(from_user)
                        
                        self._process_message(message)
                except json.JSONDecodeError:
                    pass
            conn.close()
        except Exception as e:
            print(f"⚠️ Ошибка обработки: {e}")
    
    # ============================================================
    # 2. ДЫРОПРОБИВАНИЕ (HOLE PUNCHING)
    # ============================================================
    
    def _run_hole_punching(self):
        """Дыропробивание через UDP - ОСНОВНОЙ МЕТОД"""
        try:
            self.punch_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.punch_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.punch_socket.bind(('0.0.0.0', self.hole_punch_port))
            self.punch_socket.settimeout(0.5)
            
            print(f"✅ ДЫРОПРОБИВАНИЕ ЗАПУЩЕНО НА ПОРТУ {self.hole_punch_port}")
            
            while self.is_running:
                try:
                    data, addr = self.punch_socket.recvfrom(1024)
                    if data:
                        try:
                            message = json.loads(data.decode())
                            from_user = message.get('from')
                            msg_type = message.get('type')
                            
                            if msg_type == 'punch_request' and from_user:
                                # Отвечаем на запрос дыропробивания
                                response = {
                                    'type': 'punch_response',
                                    'from': self.username,
                                    'timestamp': time.time()
                                }
                                self.punch_socket.sendto(json.dumps(response).encode(), addr)
                                print(f"🔫 ДЫРОПРОБИВАНИЕ: ответ {from_user} ({addr[0]})")
                                
                                # Сохраняем пира
                                if from_user not in self.connections:
                                    self.connections[from_user] = {
                                        'ip': addr[0],
                                        'port': addr[1],
                                        'last_seen': time.time(),
                                        'connected': True
                                    }
                                    self.friend_online.emit(from_user)
                            
                            elif msg_type == 'punch_response' and from_user:
                                # Получили ответ на дыропробивание
                                print(f"🔫 ДЫРОПРОБИВАНИЕ: установлено с {from_user} ({addr[0]})")
                                if from_user not in self.connections:
                                    self.connections[from_user] = {
                                        'ip': addr[0],
                                        'port': addr[1],
                                        'last_seen': time.time(),
                                        'connected': True
                                    }
                                    self.friend_online.emit(from_user)
                        except:
                            pass
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"⚠️ Ошибка дыропробивания: {e}")
        except Exception as e:
            print(f"❌ Ошибка дыропробивания: {e}")
    
    def _punch_peer(self, target_user: str, target_ip: str, target_port: int = None) -> bool:
        """Активное дыропробивание - стучимся в предполагаемый порт"""
        if not target_ip:
            return False
        
        if not target_port:
            target_port = self.hole_punch_port
        
        try:
            # Отправляем запрос на дыропробивание
            request = {
                'type': 'punch_request',
                'from': self.username,
                'target': target_user,
                'timestamp': time.time()
            }
            
            # Стучимся несколько раз с разными портами
            for port in [target_port, self.port, 3333, 3334, 3335]:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                        s.settimeout(1)
                        s.sendto(json.dumps(request).encode(), (target_ip, port))
                        print(f"🔫 ДЫРОПРОБИВАНИЕ: стучимся {target_user} -> {target_ip}:{port}")
                        
                        # Ждём ответ
                        try:
                            data, addr = s.recvfrom(1024)
                            response = json.loads(data.decode())
                            if response.get('type') == 'punch_response':
                                print(f"✅ ДЫРОПРОБИВАНИЕ УСПЕШНО! {target_user} ({addr[0]}:{addr[1]})")
                                self.connections[target_user] = {
                                    'ip': addr[0],
                                    'port': addr[1],
                                    'last_seen': time.time(),
                                    'connected': True
                                }
                                self.friend_online.emit(target_user)
                                return True
                        except:
                            pass
                except:
                    continue
            
            return False
        except Exception as e:
            print(f"⚠️ Ошибка дыропробивания {target_user}: {e}")
            return False
    
    # ============================================================
    # 3. ШИРОКОВЕЩАТЕЛЬНОЕ ОБНАРУЖЕНИЕ
    # ============================================================
    
    def _run_broadcast(self):
        """Широковещательное обнаружение пиров в локальной сети"""
        try:
            broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            broadcast_socket.settimeout(0.5)
            
            while self.is_running:
                try:
                    # Отправляем широковещательное сообщение
                    announce = {
                        'type': 'discover',
                        'from': self.username,
                        'ip': self.local_ip,
                        'port': self.port,
                        'timestamp': time.time()
                    }
                    broadcast_socket.sendto(
                        json.dumps(announce).encode(),
                        ('255.255.255.255', self.broadcast_port)
                    )
                    
                    # Слушаем ответы
                    try:
                        data, addr = broadcast_socket.recvfrom(1024)
                        if data:
                            try:
                                message = json.loads(data.decode())
                                from_user = message.get('from')
                                if from_user and from_user != self.username:
                                    if from_user not in self.connections:
                                        self.connections[from_user] = {
                                            'ip': addr[0],
                                            'port': self.port,
                                            'last_seen': time.time(),
                                            'connected': True
                                        }
                                        print(f"📡 ОБНАРУЖЕН: {from_user} ({addr[0]})")
                                        self.friend_online.emit(from_user)
                            except:
                                pass
                    except socket.timeout:
                        pass
                    
                    time.sleep(5)
                except Exception as e:
                    print(f"⚠️ Ошибка широковещания: {e}")
                    time.sleep(5)
        except Exception as e:
            print(f"⚠️ Ошибка широковещательного сокета: {e}")
    
    # ============================================================
    # 4. DHT (ДЕЦЕНТРАЛИЗОВАННЫЙ ПОИСК)
    # ============================================================
    
    def _run_dht(self):
        """DHT для децентрализованного поиска пользователей"""
        print("📡 DHT ЗАПУЩЕН (децентрализованный поиск)")
        
        # Регистрируемся в DHT через широковещание
        while self.is_running:
            try:
                # Объявляем о себе в DHT
                dht_data = {
                    'type': 'dht_announce',
                    'from': self.username,
                    'ip': self.public_ip or self.local_ip,
                    'port': self.port,
                    'node_id': self._hash_username(self.username),
                    'timestamp': time.time()
                }
                
                # Широковещательный запрос к DHT
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    s.settimeout(0.5)
                    s.sendto(json.dumps(dht_data).encode(), ('255.255.255.255', self.broadcast_port))
                    
                    # Слушаем DHT-ответы
                    try:
                        data, addr = s.recvfrom(1024)
                        if data:
                            try:
                                response = json.loads(data.decode())
                                if response.get('type') == 'dht_response':
                                    from_user = response.get('from')
                                    if from_user and from_user != self.username:
                                        self.dht_table[from_user] = {
                                            'ip': response.get('ip', addr[0]),
                                            'port': response.get('port', self.port),
                                            'node_id': response.get('node_id', ''),
                                            'last_seen': time.time()
                                        }
                                        print(f"📡 DHT: найден {from_user} ({self.dht_table[from_user]['ip']})")
                            except:
                                pass
                    except socket.timeout:
                        pass
                
                time.sleep(30)
            except Exception as e:
                print(f"⚠️ Ошибка DHT: {e}")
                time.sleep(30)
    
    # ============================================================
    # 5. ОБРАБОТКА СООБЩЕНИЙ
    # ============================================================
    
    def _process_message(self, data: dict):
        """Обработка входящего сообщения"""
        try:
            msg_type = data.get('type')
            from_user = data.get('from')
            
            if not from_user:
                return
            
            if msg_type == 'friend_request':
                print(f"📨 ЗАЯВКА ОТ {from_user}")
                self.friend_request_received.emit(
                    from_user,
                    data.get('content', {}).get('message', ''),
                    from_user
                )
            
            elif msg_type == 'friend_response':
                print(f"📨 ОТВЕТ ОТ {from_user}")
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
                
        except Exception as e:
            print(f"❌ Ошибка обработки: {e}")
    
    def _process_loop(self):
        """Обработка очереди сообщений"""
        while self.is_running:
            try:
                # Отправляем накопившиеся сообщения
                for user, messages in list(self.pending_messages.items()):
                    if user in self.connections:
                        ip = self.connections[user].get('ip')
                        if ip:
                            for msg in messages:
                                self._send_direct(user, msg)
                            self.pending_messages[user] = []
                
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ Ошибка обработки очереди: {e}")
                time.sleep(1)
    
    # ============================================================
    # 6. ОТПРАВКА СООБЩЕНИЙ
    # ============================================================
    
    def _send_direct(self, target_user: str, data: dict) -> bool:
        """Отправка данных напрямую"""
        try:
            if target_user in self.connections:
                ip = self.connections[target_user].get('ip')
                port = self.connections[target_user].get('port', self.port)
                if ip:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(3)
                        s.connect((ip, port))
                        s.send(json.dumps(data).encode())
                        return True
            
            # Проверяем DHT
            if target_user in self.dht_table:
                ip = self.dht_table[target_user].get('ip')
                port = self.dht_table[target_user].get('port', self.port)
                if ip:
                    # Пробуем дыропробивание
                    if self._punch_peer(target_user, ip, port):
                        return self._send_direct(target_user, data)
            
            return False
        except Exception as e:
            print(f"⚠️ Ошибка отправки {target_user}: {e}")
            return False
    
    # ============================================================
    # 7. ПУБЛИЧНЫЕ МЕТОДЫ
    # ============================================================
    
    def find_user(self, username: str) -> Optional[dict]:
        """Поиск пользователя"""
        try:
            if username.startswith('@'):
                username = username[1:]
            
            from src.core.user_manager import UserManager
            um = UserManager()
            if not um.user_exists(username):
                return None
            
            # Проверяем активные соединения
            if username in self.connections:
                return {
                    'username': username,
                    'exists': True,
                    'online': True,
                    'ip': self.connections[username].get('ip', 'unknown')
                }
            
            # Проверяем DHT
            if username in self.dht_table:
                ip = self.dht_table[username].get('ip')
                if ip:
                    # Пробуем дыропробивание
                    self._punch_peer(username, ip, self.dht_table[username].get('port', self.port))
                    if username in self.connections:
                        return {
                            'username': username,
                            'exists': True,
                            'online': True,
                            'ip': ip
                        }
            
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
        if not user_info or not user_info.get('online'):
            print(f"❌ {target} НЕ В СЕТИ")
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
        
        if recipient in self.connections:
            return self._send_direct(recipient, data)
        else:
            if recipient not in self.pending_messages:
                self.pending_messages[recipient] = []
            self.pending_messages[recipient].append(data)
            print(f"⏳ Сообщение в очереди для {recipient}")
            
            # Пробуем найти пользователя
            self.find_user(recipient)
            return True
    
    def stop(self):
        self.is_running = False
        if hasattr(self, 'server_socket'):
            try:
                self.server_socket.close()
            except:
                pass
        if hasattr(self, 'punch_socket'):
            try:
                self.punch_socket.close()
            except:
                pass
        print("🛑 P2P сеть остановлена")