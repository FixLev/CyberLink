# src/core/network.py
# P2P сеть - С ГИГАНТСКИМ ЛОГИРОВАНИЕМ И АКТИВНЫМ ПОИСКОМ

import json
import time
import socket
import threading
import os
import hashlib
import random
from typing import Optional, Dict
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime


class P2PNetwork(QObject):
    """P2P сеть - С ГИГАНТСКИМ ЛОГИРОВАНИЕМ"""
    
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
        
        # НАХОДИМ СВОБОДНЫЙ ПОРТ С ЛОГАМИ
        self.port = self._find_free_port_with_logs()
        
        # Ключи (упрощенные для демо)
        self.public_key = hashlib.sha256(username.encode()).digest()[:16]
        
        # Кэш найденных пользователей
        self.discovered_users: Dict[str, dict] = {}
        
        # Список известных портов для сканирования
        self.known_ports = list(range(6881, 6910))  # 6881-6909
        
        # ГИГАНТСКИЙ ЛОГ
        self.log_file = open(f"network_log_{username}_{int(time.time())}.txt", 'w', encoding='utf-8')
        self._log("=" * 80)
        self._log(f"🚀 ЗАПУСК P2P СЕТИ ДЛЯ {username}")
        self._log(f"🕐 ВРЕМЯ: {datetime.now().isoformat()}")
        self._log("=" * 80)
        
        self.start_network()
    
    def _log(self, message: str):
        """Запись в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        if hasattr(self, 'log_file'):
            self.log_file.write(log_line + "\n")
            self.log_file.flush()
    
    def _get_local_ip(self) -> str:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                self._log(f"🌐 Локальный IP: {ip}")
                return ip
        except Exception as e:
            self._log(f"❌ Ошибка получения IP: {e}")
            return "127.0.0.1"
    
    def _find_free_port_with_logs(self) -> int:
        """Поиск свободного порта С ЛОГАМИ"""
        self._log("🔍 НАЧАЛО ПОИСКА СВОБОДНОГО ПОРТА")
        
        # ПРОВЕРЯЕМ ВСЕ ПОРТЫ 6881-6910
        for port in range(6881, 6910):
            self._log(f"   Проверка порта {port}...")
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    s.bind(('', port))
                    self._log(f"   ✅ ПОРТ {port} СВОБОДЕН! ВЫБИРАЕМ ЕГО.")
                    return port
            except OSError as e:
                self._log(f"   ❌ Порт {port} занят: {e}")
                continue
        
        # Если все заняты - случайный порт
        self._log("⚠️ ВСЕ ПОРТЫ 6881-6909 ЗАНЯТЫ! ИЩЕМ СЛУЧАЙНЫЙ...")
        for attempt in range(20):
            port = random.randint(10000, 60000)
            self._log(f"   Попытка {attempt+1}: порт {port}...")
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    s.bind(('', port))
                    self._log(f"   ✅ СЛУЧАЙНЫЙ ПОРТ {port} СВОБОДЕН!")
                    return port
            except:
                continue
        
        self._log("❌ НЕ УДАЛОСЬ НАЙТИ СВОБОДНЫЙ ПОРТ! ИСПОЛЬЗУЮ 6881 (РИСКОВАННО)")
        return 6881
    
    def start_network(self):
        """Запуск сети С ЛОГАМИ"""
        self._log("=" * 80)
        self._log("🚀 ЗАПУСК СЕТИ")
        self._log(f"   👤 Пользователь: {self.username}")
        self._log(f"   🌐 IP: {self.local_ip}")
        self._log(f"   🔌 Порт: {self.port}")
        self._log("=" * 80)
        
        if self.is_running:
            self._log("⚠️ СЕТЬ УЖЕ ЗАПУЩЕНА")
            return
        
        self.is_running = True
        
        # Запускаем сервер для приема сообщений
        self._log("📡 ЗАПУСК СЕРВЕРА...")
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        self._log("✅ СЕРВЕР ЗАПУЩЕН В ПОТОКЕ")
        
        # Запускаем обработку очереди
        self._log("📡 ЗАПУСК ОБРАБОТЧИКА ОЧЕРЕДИ...")
        self.process_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.process_thread.start()
        self._log("✅ ОБРАБОТЧИК ЗАПУЩЕН В ПОТОКЕ")
        
        # Запускаем сканирование сети
        self._log("📡 ЗАПУСК СКАНИРОВАНИЯ СЕТИ...")
        self.scan_thread = threading.Thread(target=self._scan_network, daemon=True)
        self.scan_thread.start()
        self._log("✅ СКАНИРОВАНИЕ ЗАПУЩЕНО В ПОТОКЕ")
        
        self._log("=" * 80)
        self._log(f"🚀 P2P СЕТЬ ЗАПУЩЕНА ДЛЯ {self.username} НА ПОРТУ {self.port}")
        self._log(f"   🌐 IP: {self.local_ip}")
        self._log("=" * 80)
    
    def _run_server(self):
        """Сервер для приема сообщений С ЛОГАМИ"""
        self._log(f"🔄 СЕРВЕР: ЗАПУСК НА ПОРТУ {self.port}")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', self.port))
                s.listen(5)
                s.settimeout(1)
                self._log(f"✅ СЕРВЕР: УСПЕШНО ЗАПУЩЕН НА ПОРТУ {self.port}")
                
                while self.is_running:
                    try:
                        conn, addr = s.accept()
                        self._log(f"📥 СЕРВЕР: ПРИНЯТО СОЕДИНЕНИЕ ОТ {addr[0]}:{addr[1]}")
                        threading.Thread(target=self._handle_connection, args=(conn, addr), daemon=True).start()
                    except socket.timeout:
                        continue
                    except Exception as e:
                        self._log(f"⚠️ СЕРВЕР: ОШИБКА - {e}")
                        break
        except Exception as e:
            self._log(f"❌ СЕРВЕР: НЕ УДАЛОСЬ ЗАПУСТИТЬ - {e}")
    
    def _handle_connection(self, conn, addr):
        """Обработка входящего соединения С ЛОГАМИ"""
        try:
            data = conn.recv(65536)
            if data:
                self._log(f"📥 ПОЛУЧЕНЫ ДАННЫЕ ОТ {addr[0]}:{addr[1]} ({len(data)} байт)")
                message = json.loads(data.decode())
                self._log(f"📥 СООБЩЕНИЕ: {message.get('type', 'unknown')} от {message.get('from', 'unknown')}")
                self._process_incoming_message(message, addr[0])
            conn.close()
        except Exception as e:
            self._log(f"⚠️ ОШИБКА ОБРАБОТКИ СОЕДИНЕНИЯ: {e}")
    
    def _process_loop(self):
        """Обработка очереди сообщений С ЛОГАМИ"""
        self._log("🔄 ОБРАБОТЧИК: ЗАПУЩЕН")
        while self.is_running:
            try:
                # Отправляем накопившиеся сообщения
                for peer_id, messages in list(self.pending_messages.items()):
                    if messages:
                        self._log(f"📤 ОБРАБОТЧИК: {len(messages)} сообщений для {peer_id}")
                    if peer_id in self.active_connections:
                        for msg in messages:
                            self._log(f"📤 ОБРАБОТЧИК: ОТПРАВКА {msg.get('type', 'unknown')} -> {peer_id}")
                            self._send_direct(peer_id, msg)
                        self.pending_messages[peer_id] = []
                
                # Проверяем активные соединения (пинг)
                for peer_id in list(self.active_connections.keys()):
                    if time.time() - self.active_connections[peer_id].get('last_ping', 0) > 30:
                        self._log(f"🔄 ПИНГ: ПРОВЕРКА {peer_id} (прошло >30 сек)")
                        if not self._ping_peer(peer_id):
                            self._log(f"❌ ПИНГ: {peer_id} НЕ ОТВЕЧАЕТ, УДАЛЯЕМ")
                            del self.active_connections[peer_id]
                            self.friend_offline.emit(peer_id)
                
                time.sleep(2)
            except Exception as e:
                self._log(f"⚠️ ОБРАБОТЧИК: ОШИБКА - {e}")
                time.sleep(2)
    
    def _scan_network(self):
        """Сканирование сети для поиска пользователей С ЛОГАМИ"""
        self._log("🔄 СКАНИРОВАНИЕ: ЗАПУЩЕНО")
        scan_count = 0
        
        while self.is_running:
            try:
                scan_count += 1
                self._log("=" * 60)
                self._log(f"🔍 СКАНИРОВАНИЕ #{scan_count}")
                
                ip_parts = self.local_ip.split('.')
                base_ip = '.'.join(ip_parts[:3])
                self._log(f"   🌐 Сканируем подсеть: {base_ip}.x")
                self._log(f"   🔌 Проверяем порты: {self.known_ports}")
                
                found = 0
                checked_ips = 0
                checked_ports = 0
                
                for i in range(1, 255):
                    if not self.is_running:
                        break
                    
                    ip = f"{base_ip}.{i}"
                    if ip == self.local_ip:
                        continue
                    
                    for port in self.known_ports:
                        if not self.is_running:
                            break
                        checked_ports += 1
                        
                        try:
                            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                                s.settimeout(0.2)
                                s.connect((ip, port))
                                self._log(f"   ✅ {ip}:{port} - ДОСТУПЕН")
                                
                                # Отправляем запрос на идентификацию
                                ping_data = {
                                    'type': 'discover',
                                    'from': self.username,
                                    'timestamp': time.time()
                                }
                                s.send(json.dumps(ping_data).encode())
                                self._log(f"   📤 {ip}:{port} - ОТПРАВЛЕН DISCOVER")
                                
                                # Ждём ответ
                                response = s.recv(1024)
                                if response:
                                    data = json.loads(response.decode())
                                    self._log(f"   📥 {ip}:{port} - ПОЛУЧЕН ОТВЕТ: {data}")
                                    
                                    if data.get('type') == 'discover_response':
                                        user = data.get('from')
                                        if user and user != self.username:
                                            self._log(f"   🎯 {ip}:{port} - НАЙДЕН ПОЛЬЗОВАТЕЛЬ {user}")
                                            
                                            if user not in self.discovered_users:
                                                self.discovered_users[user] = {
                                                    'username': user,
                                                    'ip': ip,
                                                    'port': port,
                                                    'last_seen': time.time()
                                                }
                                                found += 1
                                                self._log(f"   ✅ НОВЫЙ ПОЛЬЗОВАТЕЛЬ {user} ДОБАВЛЕН В КЭШ")
                                            
                                            if user not in self.active_connections:
                                                self.active_connections[user] = {
                                                    'ip': ip,
                                                    'port': port,
                                                    'last_ping': time.time()
                                                }
                                                self._log(f"   🔗 АКТИВНОЕ СОЕДИНЕНИЕ С {user} УСТАНОВЛЕНО")
                                                self.friend_online.emit(user)
                        except socket.timeout:
                            continue
                        except ConnectionRefusedError:
                            continue
                        except Exception as e:
                            continue
                        finally:
                            checked_ips += 1
                
                self._log(f"📊 ИТОГИ СКАНИРОВАНИЯ #{scan_count}:")
                self._log(f"   🔍 Проверено IP: {checked_ips}")
                self._log(f"   🔌 Проверено портов: {checked_ports}")
                self._log(f"   🎯 Найдено новых пользователей: {found}")
                self._log(f"   📋 Всего в кэше: {len(self.discovered_users)}")
                self._log(f"   🔗 Активных соединений: {len(self.active_connections)}")
                self._log("=" * 60)
                
                # Спим между сканированиями
                self._log(f"💤 СКАНИРОВАНИЕ: ЖДЁМ 30 СЕКУНД ДО СЛЕДУЮЩЕГО ПРОХОДА...")
                time.sleep(30)
                
            except Exception as e:
                self._log(f"❌ СКАНИРОВАНИЕ: ОШИБКА - {e}")
                import traceback
                self._log(traceback.format_exc())
                time.sleep(30)
    
    def _process_incoming_message(self, data: dict, from_ip: str = None):
        """Обработка входящего сообщения С ЛОГАМИ"""
        try:
            msg_type = data.get('type')
            from_id = data.get('from')
            
            self._log(f"📥 ОБРАБОТКА СООБЩЕНИЯ: тип={msg_type}, от={from_id}, IP={from_ip}")
            
            if not from_id:
                self._log("⚠️ НЕТ from_id В СООБЩЕНИИ")
                return
            
            # Обновляем активное соединение
            if from_id not in self.active_connections:
                self._log(f"🔗 НОВОЕ СОЕДИНЕНИЕ ОТ {from_id} ({from_ip})")
                self.active_connections[from_id] = {
                    'ip': from_ip or data.get('ip', ''),
                    'last_ping': time.time()
                }
                self.friend_online.emit(from_id)
            else:
                self.active_connections[from_id]['last_ping'] = time.time()
                self._log(f"🔄 ОБНОВЛЁН ПИНГ ДЛЯ {from_id}")
            
            # Обрабатываем who_is_here
            if msg_type == 'who_is_here':
                target = data.get('target')
                self._log(f"📡 who_is_here ОТ {from_id} ИЩЕТ {target}")
                
                # Если ищут нас - отвечаем
                if target == self.username:
                    response = {
                        'type': 'who_is_here_response',
                        'from': self.username,
                        'to': from_id,
                        'username': self.username,
                        'timestamp': time.time()
                    }
                    self._log(f"📤 ОТВЕЧАЕМ who_is_here ДЛЯ {from_id}")
                    self._send_direct(from_id, response, from_ip)
                return
            
            if msg_type == 'who_is_here_response':
                found_user = data.get('username')
                self._log(f"📡 who_is_here_response ОТ {from_id}: {found_user}")
                if found_user and found_user not in self.discovered_users:
                    self.discovered_users[found_user] = {
                        'username': found_user,
                        'ip': from_ip,
                        'last_seen': time.time()
                    }
                    self._log(f"✅ ПОЛЬЗОВАТЕЛЬ {found_user} ДОБАВЛЕН В КЭШ")
                    self.friend_online.emit(found_user)
                return
            
            # Обрабатываем discover
            if msg_type == 'discover':
                self._log(f"📡 DISCOVER ОТ {from_id}")
                response = {
                    'type': 'discover_response',
                    'from': self.username,
                    'timestamp': time.time()
                }
                self._log(f"📤 ОТВЕТ DISCOVER ДЛЯ {from_id}")
                self._send_direct(from_id, response, from_ip)
                return
            
            if msg_type == 'discover_response':
                self._log(f"📡 DISCOVER_RESPONSE ОТ {from_id}")
                if from_id not in self.discovered_users:
                    self.discovered_users[from_id] = {
                        'username': from_id,
                        'ip': from_ip,
                        'last_seen': time.time()
                    }
                    self._log(f"✅ ПОЛЬЗОВАТЕЛЬ {from_id} ДОБАВЛЕН В КЭШ")
                    self.friend_online.emit(from_id)
                return
            
            if msg_type == 'friend_request':
                self._log(f"📨 FRIEND_REQUEST ОТ {from_id}")
                self.friend_request_received.emit(
                    from_id,
                    data.get('content', {}).get('message', ''),
                    from_id
                )
            
            elif msg_type == 'friend_response':
                self._log(f"📨 FRIEND_RESPONSE ОТ {from_id}: {data.get('content', {}).get('accepted', False)}")
                self.friend_request_response.emit(
                    from_id,
                    data.get('content', {}).get('accepted', False)
                )
            
            elif msg_type == 'message':
                self._log(f"💬 MESSAGE ОТ {from_id}")
                self.message_received.emit(
                    data.get('content', {}).get('chat_id'),
                    data.get('content', {}).get('message', {})
                )
            
            elif msg_type == 'history_request':
                self._log(f"📜 HISTORY_REQUEST ОТ {from_id}")
                self.history_requested.emit(from_id)
            
            elif msg_type == 'history_response':
                history = data.get('content', {}).get('history', [])
                self._log(f"📜 HISTORY_RESPONSE ОТ {from_id}: {len(history)} сообщений")
                self.history_received.emit(from_id, history)
            
            elif msg_type == 'ping':
                self._log(f"🏓 PING ОТ {from_id}")
                response = {'type': 'pong', 'from': self.username, 'to': from_id}
                self._send_direct(from_id, response, from_ip)
            
            elif msg_type == 'pong':
                self._log(f"🏓 PONG ОТ {from_id}")
                self.friend_online.emit(from_id)
            
            else:
                self._log(f"⚠️ НЕИЗВЕСТНЫЙ ТИП СООБЩЕНИЯ: {msg_type}")
                
        except Exception as e:
            self._log(f"❌ ОШИБКА ОБРАБОТКИ СООБЩЕНИЯ: {e}")
            import traceback
            self._log(traceback.format_exc())
    
    def _send_direct(self, peer_id: str, data: dict, target_ip: str = None) -> bool:
        """Отправка данных напрямую С ЛОГАМИ"""
        try:
            self._log(f"📤 ОТПРАВКА {data.get('type', 'unknown')} -> {peer_id}")
            
            # Если знаем IP из активного соединения
            if peer_id in self.active_connections:
                ip = self.active_connections[peer_id].get('ip')
                port = self.active_connections[peer_id].get('port', self.port)
                if ip:
                    self._log(f"   📤 {peer_id} -> {ip}:{port} (из активного соединения)")
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(3)
                        s.connect((ip, port))
                        s.send(json.dumps(data).encode())
                        self._log(f"   ✅ ОТПРАВЛЕНО {peer_id} через {ip}:{port}")
                        return True
            
            # Если передали IP
            if target_ip:
                self._log(f"   📤 {peer_id} -> {target_ip} (из target_ip)")
                for port in self.known_ports:
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(1)
                            s.connect((target_ip, port))
                            s.send(json.dumps(data).encode())
                            self._log(f"   ✅ ОТПРАВЛЕНО {peer_id} через {target_ip}:{port}")
                            self.active_connections[peer_id] = {
                                'ip': target_ip,
                                'port': port,
                                'last_ping': time.time()
                            }
                            return True
                    except:
                        continue
            
            # Если есть в discovered_users
            if peer_id in self.discovered_users:
                ip = self.discovered_users[peer_id].get('ip')
                port = self.discovered_users[peer_id].get('port', self.port)
                if ip:
                    self._log(f"   📤 {peer_id} -> {ip}:{port} (из кэша)")
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(1)
                        s.connect((ip, port))
                        s.send(json.dumps(data).encode())
                        self._log(f"   ✅ ОТПРАВЛЕНО {peer_id} через {ip}:{port}")
                        self.active_connections[peer_id] = {
                            'ip': ip,
                            'port': port,
                            'last_ping': time.time()
                        }
                        return True
            
            # Сохраняем в очередь
            self._log(f"   ⏳ {peer_id} НЕ ДОСТУПЕН, СОХРАНЯЕМ В ОЧЕРЕДЬ")
            if peer_id not in self.pending_messages:
                self.pending_messages[peer_id] = []
            self.pending_messages[peer_id].append(data)
            return False
            
        except Exception as e:
            self._log(f"❌ ОШИБКА ОТПРАВКИ {peer_id}: {e}")
            if peer_id not in self.pending_messages:
                self.pending_messages[peer_id] = []
            self.pending_messages[peer_id].append(data)
            return False
    
    def _ping_peer(self, peer_id: str) -> bool:
        """Пинг пира С ЛОГАМИ"""
        self._log(f"🏓 ПИНГ {peer_id}...")
        try:
            data = {'type': 'ping', 'from': self.username}
            result = self._send_direct(peer_id, data)
            if result:
                self._log(f"   ✅ ПИНГ {peer_id} УСПЕШЕН")
            else:
                self._log(f"   ❌ ПИНГ {peer_id} НЕУДАЧЕН")
            return result
        except Exception as e:
            self._log(f"   ❌ ПИНГ {peer_id} ОШИБКА: {e}")
            return False
    
    def find_user(self, username: str) -> Optional[dict]:
        """Поиск пользователя в сети С ЛОГАМИ - АКТИВНОЕ СКАНИРОВАНИЕ"""
        try:
            if username.startswith('@'):
                username = username[1:]
            
            self._log("=" * 60)
            self._log(f"🔍 ПОИСК ПОЛЬЗОВАТЕЛЯ {username}")
            self._log(f"   📋 КЭШ: {list(self.discovered_users.keys())}")
            self._log(f"   🔗 АКТИВНЫЕ: {list(self.active_connections.keys())}")
            
            # Проверяем кэш
            if username in self.discovered_users:
                self._log(f"   ✅ {username} НАЙДЕН В КЭШЕ")
                return self.discovered_users[username]
            
            # Проверяем активные соединения
            if username in self.active_connections:
                self._log(f"   ✅ {username} В АКТИВНЫХ СОЕДИНЕНИЯХ")
                return {'username': username, 'exists': True, 'active': True}
            
            # Проверяем локальный реестр
            from src.core.user_manager import UserManager
            um = UserManager()
            if not um.user_exists(username):
                self._log(f"   ❌ {username} НЕ СУЩЕСТВУЕТ (локально)")
                return None
            
            self._log(f"   🔍 {username} СУЩЕСТВУЕТ ЛОКАЛЬНО, НО НЕ В КЭШЕ. АКТИВНОЕ СКАНИРОВАНИЕ СЕТИ...")
            
            # АКТИВНО СКАНИРУЕМ СЕТЬ
            ip_parts = self.local_ip.split('.')
            base_ip = '.'.join(ip_parts[:3])
            self._log(f"   🌐 СКАНИРУЕМ ПОДСЕТЬ {base_ip}.x ПОРТЫ {self.known_ports[:5]}...")
            
            found = False
            
            # Проверяем все IP в подсети
            for i in range(1, 255):
                ip = f"{base_ip}.{i}"
                if ip == self.local_ip:
                    continue
                
                for port in self.known_ports:
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(0.3)
                            s.connect((ip, port))
                            
                            # Отправляем запрос "кто здесь?"
                            ping_data = {
                                'type': 'who_is_here',
                                'from': self.username,
                                'target': username,
                                'timestamp': time.time()
                            }
                            s.send(json.dumps(ping_data).encode())
                            
                            # Ждём ответ
                            response = s.recv(1024)
                            if response:
                                data = json.loads(response.decode())
                                self._log(f"   📥 ОТВЕТ ОТ {ip}:{port}: {data}")
                                
                                if data.get('type') == 'who_is_here_response':
                                    found_user = data.get('username')
                                    if found_user == username:
                                        self._log(f"   🎯 НАЙДЕН {username} на {ip}:{port}")
                                        self.discovered_users[username] = {
                                            'username': username,
                                            'ip': ip,
                                            'port': port,
                                            'last_seen': time.time()
                                        }
                                        self.active_connections[username] = {
                                            'ip': ip,
                                            'port': port,
                                            'last_ping': time.time()
                                        }
                                        self.friend_online.emit(username)
                                        return self.discovered_users[username]
                    except:
                        continue
            
            self._log(f"   ❌ {username} НЕ НАЙДЕН В СЕТИ")
            return None
            
        except Exception as e:
            self._log(f"❌ ОШИБКА ПОИСКА {username}: {e}")
            import traceback
            self._log(traceback.format_exc())
            return None
    
    def connect_to_peer(self, peer_id: str, ip: str, port: int = None):
        """Установка соединения с пиром С ЛОГАМИ"""
        self._log(f"🔗 УСТАНОВКА СОЕДИНЕНИЯ С {peer_id} ({ip}:{port or self.port})")
        self.active_connections[peer_id] = {
            'ip': ip,
            'port': port or self.port,
            'last_ping': time.time()
        }
        self.friend_online.emit(peer_id)
        self._ping_peer(peer_id)
    
    def send_friend_request(self, target: str, message: str = "") -> bool:
        """Отправка заявки С ЛОГАМИ"""
        if target.startswith('@'):
            target = target[1:]
        
        self._log("=" * 60)
        self._log(f"📨 ОТПРАВКА ЗАЯВКИ {target}")
        self._log(f"   📝 СООБЩЕНИЕ: {message[:50]}...")
        
        user_info = self.find_user(target)
        if not user_info:
            self._log(f"   ❌ {target} НЕ НАЙДЕН В СЕТИ")
            return False
        
        self._log(f"   ✅ {target} НАЙДЕН: {user_info}")
        self._log(f"   📤 ОТПРАВЛЯЕМ ЗАЯВКУ...")
        
        data = {
            'type': 'friend_request',
            'from': self.username,
            'to': target,
            'content': {'message': message}
        }
        result = self._send_direct(target, data)
        if result:
            self._log(f"   ✅ ЗАЯВКА ОТПРАВЛЕНА {target}")
        else:
            self._log(f"   ⏳ ЗАЯВКА В ОЧЕРЕДИ ДЛЯ {target}")
        return result
    
    def respond_friend_request(self, target: str, accepted: bool) -> bool:
        """Ответ на заявку С ЛОГАМИ"""
        if target.startswith('@'):
            target = target[1:]
        
        self._log(f"📨 ОТВЕТ НА ЗАЯВКУ {target}: {accepted}")
        
        data = {
            'type': 'friend_response',
            'from': self.username,
            'to': target,
            'content': {'accepted': accepted}
        }
        return self._send_direct(target, data)
    
    def send_message(self, chat_id: str, message: dict) -> bool:
        """Отправка сообщения С ЛОГАМИ"""
        users = chat_id.split('_')
        recipient = users[0] if users[1] == self.username else users[1]
        
        self._log(f"💬 ОТПРАВКА СООБЩЕНИЯ В ЧАТ {chat_id} -> {recipient}")
        
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
        """Запрос истории С ЛОГАМИ"""
        self._log(f"📜 ЗАПРОС ИСТОРИИ У {friend_id}")
        data = {
            'type': 'history_request',
            'from': self.username,
            'to': friend_id,
            'timestamp': time.time()
        }
        return self._send_direct(friend_id, data)
    
    def send_chat_history(self, friend_id: str, history: list) -> bool:
        """Отправка истории С ЛОГАМИ"""
        self._log(f"📜 ОТПРАВКА ИСТОРИИ {friend_id} ({len(history)} сообщений)")
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
        if peer_id in self.discovered_users:
            return self.discovered_users[peer_id].get('ip')
        return None
    
    def stop(self):
        """Остановка сети С ЛОГАМИ"""
        self._log("🛑 ОСТАНОВКА СЕТИ")
        self.is_running = False
        if hasattr(self, 'log_file'):
            self.log_file.close()
        print("🛑 P2P сеть остановлена")