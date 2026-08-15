import asyncio
import json
import hashlib
from kademlia.network import Server
from kademlia.storage import ForgetfulStorage
import socket
import random
from datetime import datetime

class P2PNetwork:
    def __init__(self, username, port=None):
        self.username = username
        self.port = port or random.randint(10000, 20000)
        self.server = Server(storage=ForgetfulStorage())
        self.peers = {}  # {username: (ip, port)}
        self.is_running = False
        self.message_callback = None
        
    async def start(self):
        """Запуск P2P сети"""
        self.is_running = True
        
        # Запускаем сервер
        await self.server.listen(self.port)
        
        # Получаем внешний IP
        external_ip = self.get_external_ip()
        
        # Регистрируемся в DHT
        # В реальной сети нужно подключиться к bootstrap узлам
        # Для демонстрации используем локальный bootstrap
        bootstrap_node = ('127.0.0.1', 9999)  # Заглушка
        try:
            await self.server.bootstrap([bootstrap_node])
        except:
            print("⚠️ Не удалось подключиться к DHT, работаем в локальном режиме")
        
        # Сохраняем свои данные в DHT
        key = hashlib.sha256(self.username.encode()).hexdigest()
        value = json.dumps({
            'username': self.username,
            'ip': external_ip,
            'port': self.port,
            'online': True,
            'last_seen': datetime.now().isoformat()
        })
        await self.server.set(key, value)
        
        # Запускаем фоновые процессы
        asyncio.create_task(self.update_presence())
        asyncio.create_task(self.listen_for_messages())
        
        print(f"✅ P2P сеть запущена на порту {self.port}")
        print(f"👤 Ваш логин: @{self.username}")
        print(f"🌐 Внешний IP: {external_ip}")
        return True
    
    def get_external_ip(self):
        """Получение внешнего IP"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    async def update_presence(self):
        """Обновление присутствия в сети"""
        while self.is_running:
            await asyncio.sleep(30)  # Обновляем каждые 30 секунд
            key = hashlib.sha256(self.username.encode()).hexdigest()
            value = json.dumps({
                'username': self.username,
                'ip': self.get_external_ip(),
                'port': self.port,
                'online': True,
                'last_seen': datetime.now().isoformat()
            })
            await self.server.set(key, value)
    
    async def find_user(self, username):
        """Поиск пользователя в сети"""
        key = hashlib.sha256(username.encode()).hexdigest()
        try:
            result = await self.server.get(key)
            if result:
                data = json.loads(result)
                return data
        except:
            pass
        return None
    
    async def send_message(self, to_username, content, sync_hash=None):
        """Отправка сообщения"""
        # Находим получателя
        user_info = await self.find_user(to_username)
        
        if not user_info:
            raise Exception(f"Пользователь @{to_username} не найден в сети")
        
        # Формируем сообщение
        message = {
            'type': 'message',
            'from': self.username,
            'to': to_username,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'sync_hash': sync_hash
        }
        
        # В реальном P2P здесь было бы прямое соединение
        # Для демонстрации имитируем отправку
        print(f"📤 Отправлено сообщение для @{to_username}: {content[:30]}...")
        
        # Если есть callback, вызываем его (для имитации получения)
        if self.message_callback:
            # Имитация получения сообщения другой стороной
            await asyncio.sleep(0.5)
            await self.message_callback(message)
        
        return True
    
    async def listen_for_messages(self):
        """Прослушивание входящих сообщений"""
        while self.is_running:
            await asyncio.sleep(1)
            # В реальной реализации здесь был бы обработчик входящих соединений
    
    def set_message_callback(self, callback):
        """Установка callback для получения сообщений"""
        self.message_callback = callback
    
    async def stop(self):
        """Остановка сети"""
        self.is_running = False
        await self.server.stop()