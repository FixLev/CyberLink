# src/core/network.py
"""
CyberLink P2P Network — BitTorrent DHT + прямой UDP

Установка:
    pip install libtorrent cryptography

Android (Termux):
    pkg install python libtorrent-rasterbar
    pip install cryptography
"""

import base64
import hashlib
import json
import os
import socket
import threading
import time
from typing import Dict, List, Optional

from PyQt5.QtCore import QObject, pyqtSignal

try:
    import libtorrent as lt
    _DHT_OK = True
except ImportError:
    _DHT_OK = False
    print("❌ libtorrent не найден. Установи: pip install libtorrent")

# ──────────────────────────────────────────────────────────────
# Настройки
# ──────────────────────────────────────────────────────────────
_APP_NS   = "cyberlink_v2"   # namespace в DHT — отличает нас от торрентов
_MSG_PORT = 13337            # UDP-порт для сообщений
_DHT_PORT = 13338            # UDP-порт для DHT

# Публичные bootstrap-узлы BitTorrent DHT.
# НЕ наши серверы — они только помогают войти в DHT-сеть.
# Не видят сообщений, не хранят данных.
_BOOTSTRAP = [
    ("router.bittorrent.com",  6881),
    ("router.utorrent.com",    6881),
    ("dht.transmissionbt.com", 6881),
    ("router.bitcomet.com",    6881),
]


class P2PNetwork(QObject):
    """
    Полностью децентрализованный P2P-мессенджер.

    Обнаружение пиров : BitTorrent DHT (20M+ нод, нельзя заблокировать)
    Передача данных  : прямой UDP + UDP hole punching
    Шифрование       : X25519 (ECDH) + ChaCha20-Poly1305
    """

    # ── Qt-сигналы (совместимы с остальным кодом проекта) ──
    friend_request_received = pyqtSignal(str, str, str)
    friend_request_response = pyqtSignal(str, bool)
    message_received        = pyqtSignal(str, dict)
    friend_online           = pyqtSignal(str)
    friend_offline          = pyqtSignal(str)

    # ══════════════════════════════════════════════════════════
    # Инициализация
    # ══════════════════════════════════════════════════════════

    def __init__(self, username: str):
        super().__init__()
        self.username   = username
        self.is_running = False

        os.makedirs("data", exist_ok=True)

        # Ключи E2E
        self._privkey, self.pubkey_bytes = self._load_or_create_keys()
        self._peer_keys: Dict[str, bytes] = {}   # username → pubkey bytes

        # Пиры: username → {ip, port, ts}
        self.peers: Dict[str, dict] = {}

        # Очередь для оффлайн-пиров
        self._queue:    Dict[str, List[dict]] = {}
        self._seen_ids: set = set()

        # Сокет и DHT-сессия
        self._sock: Optional[socket.socket] = None
        self._dht:  Optional[object]        = None

        # Маппинг info_hash (bytes) → username для DHT-ответов
        self._hash_to_user: Dict[bytes, str] = {}

        self._start()

    # ══════════════════════════════════════════════════════════
    # Ключи и шифрование
    # ══════════════════════════════════════════════════════════

    def _load_or_create_keys(self):
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
        from cryptography.hazmat.primitives.serialization import (
            Encoding, PublicFormat, PrivateFormat, NoEncryption,
        )
        path = os.path.join("data", f"{self.username}.key")
        if os.path.exists(path):
            with open(path, "rb") as f:
                priv = X25519PrivateKey.from_private_bytes(f.read())
        else:
            priv = X25519PrivateKey.generate()
            with open(path, "wb") as f:
                f.write(priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption()))
        pub = priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        return priv, pub

    def _shared_key(self, peer_pub: bytes) -> bytes:
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        from cryptography.hazmat.primitives import hashes
        shared = self._privkey.exchange(X25519PublicKey.from_public_bytes(peer_pub))
        return HKDF(
            algorithm=hashes.SHA256(), length=32,
            salt=None, info=b"cyberlink-e2e-v2",
        ).derive(shared)

    def _encrypt(self, peer: str, data: dict) -> Optional[bytes]:
        if peer not in self._peer_keys:
            return None
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
        key   = self._shared_key(self._peer_keys[peer])
        nonce = os.urandom(12)
        ct    = ChaCha20Poly1305(key).encrypt(nonce, json.dumps(data).encode(), None)
        return nonce + ct

    def _decrypt(self, peer: str, raw: bytes) -> Optional[dict]:
        if peer not in self._peer_keys or len(raw) < 12:
            return None
        try:
            from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
            key = self._shared_key(self._peer_keys[peer])
            pt  = ChaCha20Poly1305(key).decrypt(raw[:12], raw[12:], None)
            return json.loads(pt)
        except Exception:
            return None

    # ══════════════════════════════════════════════════════════
    # BitTorrent DHT
    # ══════════════════════════════════════════════════════════

    def _username_to_hash(self, username: str) -> bytes:
        """username → 20-байтный SHA1 → DHT key"""
        return hashlib.sha1(
            f"{_APP_NS}:{username.lower().strip()}".encode()
        ).digest()

    def _init_dht(self) -> bool:
        if not _DHT_OK:
            print("⚠️  DHT недоступен (нет libtorrent)")
            return False
        try:
            sp = lt.settings_pack()
            sp[lt.settings_pack.listen_interfaces] = f"0.0.0.0:{_DHT_PORT}"
            sp[lt.settings_pack.enable_dht]        = True
            sp[lt.settings_pack.enable_lsd]        = True    # LAN-обнаружение
            sp[lt.settings_pack.enable_upnp]       = True    # UPnP (пробивка NAT)
            sp[lt.settings_pack.enable_natpmp]     = True    # NAT-PMP
            sp[lt.settings_pack.alert_mask]        = (
                lt.alert.category_t.dht_notification |
                lt.alert.category_t.error_notification
            )
            self._dht = lt.session(sp)

            for host, port in _BOOTSTRAP:
                self._dht.add_dht_router(host, port)

            # Восстанавливаем DHT-таблицу (быстрее стартует)
            state_path = os.path.join("data", "dht.state")
            if os.path.exists(state_path):
                with open(state_path, "rb") as f:
                    self._dht.load_state(lt.bdecode(f.read()))

            print("📡 BitTorrent DHT запущен (~20M нод)")
            return True
        except Exception as e:
            print(f"❌ DHT init: {e}")
            return False

    def _dht_announce(self):
        """Сообщаем DHT: «я здесь, на этом порту»"""
        if not self._dht:
            return
        try:
            port  = self._sock.getsockname()[1]
            ih    = lt.sha1_hash(self._username_to_hash(self.username))
            self._dht.dht_announce(ih, port)
        except Exception as e:
            print(f"⚠️  DHT announce: {e}")

    def _dht_find(self, username: str):
        """Запрашиваем у DHT IP:port пользователя"""
        if not self._dht:
            return
        try:
            h = self._username_to_hash(username)
            self._hash_to_user[h] = username           # запоминаем для ответа
            self._dht.dht_get_peers(lt.sha1_hash(h))
            print(f"🔍 DHT: ищем {username}…")
        except Exception as e:
            print(f"⚠️  DHT find '{username}': {e}")

    def _dht_alert_loop(self):
        """Читаем ответы от DHT — там лежат IP найденных пиров"""
        while self.is_running:
            if self._dht:
                for alert in self._dht.pop_alerts():
                    # Имя класса — безопасный способ проверки без привязки к версии
                    if type(alert).__name__ == "dht_get_peers_reply_alert":
                        self._on_dht_reply(alert)
            time.sleep(0.2)

    def _on_dht_reply(self, alert):
        try:
            ih_bytes = bytes(alert.info_hash)
        except Exception:
            return

        username = self._hash_to_user.get(ih_bytes)
        if not username or username == self.username:
            return

        for ep in alert.peers():
            ip   = str(ep.address())
            port = ep.port()
            if ip and not ip.startswith("0.") and port > 0:
                print(f"📡 DHT нашёл {username} → {ip}:{port}")
                threading.Thread(
                    target=self._handshake, args=(username, ip, port),
                    daemon=True,
                ).start()

    def _dht_heartbeat(self):
        """Периодически анонсируем себя и ищем все контакты"""
        time.sleep(15)          # ждём пока DHT поднимется
        while self.is_running:
            self._dht_announce()
            for u in self._load_contacts():
                if u != self.username and u not in self.peers:
                    self._dht_find(u)
            time.sleep(300)     # каждые 5 минут

    # ══════════════════════════════════════════════════════════
    # UDP-транспорт
    # ══════════════════════════════════════════════════════════

    def _init_sock(self) -> bool:
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self._sock.bind(("0.0.0.0", _MSG_PORT))
            except OSError:
                self._sock.bind(("0.0.0.0", 0))         # занят — берём любой
            print(f"🔌 UDP порт: {self._sock.getsockname()[1]}")
            return True
        except Exception as e:
            print(f"❌ Socket: {e}")
            return False

    def _raw_send(self, ip: str, port: int, pkt: dict) -> bool:
        try:
            self._sock.sendto(json.dumps(pkt, separators=(",", ":")).encode(), (ip, port))
            return True
        except Exception:
            return False

    def _handshake(self, username: str, ip: str, port: int):
        """
        UDP hole punch + обмен публичными ключами.
        Отправляем несколько раз — это пробивает большинство NAT.
        """
        pkt = {"t": "hs", "f": self.username, "k": self.pubkey_bytes.hex()}
        for _ in range(4):
            self._raw_send(ip, port, pkt)
            time.sleep(0.05)

    # ── Приём ──────────────────────────────────────────────────

    def _recv_loop(self):
        self._sock.settimeout(1.0)
        while self.is_running:
            try:
                data, addr = self._sock.recvfrom(65535)
                threading.Thread(
                    target=self._on_packet, args=(data, addr),
                    daemon=True,
                ).start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:
                    print(f"⚠️  recv: {e}")

    def _on_packet(self, data: bytes, addr):
        ip, port = addr
        try:
            pkt = json.loads(data)
        except Exception:
            return

        pkt_type  = pkt.get("t")
        from_user = pkt.get("f")
        if not from_user:
            return

        # Дедупликация
        pid = pkt.get("i")
        if pid:
            if pid in self._seen_ids:
                return
            self._seen_ids.add(pid)
            if len(self._seen_ids) > 100_000:
                self._seen_ids = set(list(self._seen_ids)[-50_000:])

        # Регистрируем/обновляем пира
        is_new = from_user not in self.peers
        self.peers[from_user] = {"ip": ip, "port": port, "ts": time.time()}
        if is_new:
            print(f"✅ Пир онлайн: {from_user} ({ip}:{port})")
            self.friend_online.emit(from_user)
            self._flush_queue(from_user)

        # ── Handshake ──
        if pkt_type == "hs":
            k = pkt.get("k")
            if k:
                self._peer_keys[from_user] = bytes.fromhex(k)
            # Отвечаем своим handshake (если это была первая сторона)
            if is_new:
                self._handshake(from_user, ip, port)

        # ── Зашифрованное сообщение ──
        elif pkt_type == "enc":
            raw = base64.b64decode(pkt.get("b", ""))
            payload = self._decrypt(from_user, raw)
            if payload:
                self._on_payload(from_user, payload)
            else:
                # Нет ключа — просим handshake
                self._handshake(from_user, ip, port)

        # ── Незашифрованное (только до обмена ключами) ──
        elif pkt_type == "plain":
            self._on_payload(from_user, pkt.get("b") or {})

    def _on_payload(self, from_user: str, payload: dict):
        """Обработка прикладного сообщения"""
        app_type = payload.get("type")

        if app_type == "friend_request":
            pk = payload.get("pubkey")
            if pk:
                self._peer_keys[from_user] = bytes.fromhex(pk)
            self.friend_request_received.emit(
                from_user,
                payload.get("message", ""),
                from_user,
            )

        elif app_type == "friend_response":
            self.friend_request_response.emit(
                from_user,
                payload.get("accepted", False),
            )

        elif app_type == "message":
            self.message_received.emit(
                payload.get("chat_id"),
                payload.get("message") or {},
            )

    # ── Отправка ───────────────────────────────────────────────

    def _send(self, target: str, payload: dict) -> bool:
        info = self.peers.get(target)
        if not info:
            return False

        pid = f"{int(time.time() * 1000)}_{self.username}"
        enc = self._encrypt(target, payload)

        if enc:
            pkt = {
                "t": "enc",
                "f": self.username,
                "i": pid,
                "b": base64.b64encode(enc).decode(),
            }
        else:
            # Ключа ещё нет (до первого handshake)
            pkt = {"t": "plain", "f": self.username, "i": pid, "b": payload}

        return self._raw_send(info["ip"], info["port"], pkt)

    def _send_or_queue(self, target: str, payload: dict):
        """Отправить, или поставить в очередь и начать поиск через DHT"""
        if self._send(target, payload):
            return
        self._queue.setdefault(target, []).append(payload)
        count = len(self._queue[target])
        print(f"📥 Очередь [{target}]: {count} сообщ.")
        self._dht_find(target)

    def _flush_queue(self, target: str):
        msgs = self._queue.pop(target, [])
        for m in msgs:
            self._send(target, m)
        if msgs:
            print(f"📤 Доставлено [{target}]: {len(msgs)} сообщ.")

    def _retry_loop(self):
        """Каждые 30 сек — пробуем доставить из очереди"""
        while self.is_running:
            time.sleep(30)
            for u in list(self._queue.keys()):
                if u in self.peers:
                    self._flush_queue(u)
                else:
                    self._dht_find(u)

    # ══════════════════════════════════════════════════════════
    # Запуск
    # ══════════════════════════════════════════════════════════

    def _start(self):
        self.is_running = True
        if not self._init_sock():
            return
        self._init_dht()

        for name, target in [
            ("recv",      self._recv_loop),
            ("dht-alert", self._dht_alert_loop),
            ("dht-hb",    self._dht_heartbeat),
            ("retry",     self._retry_loop),
        ]:
            threading.Thread(target=target, daemon=True, name=name).start()

        print("=" * 55)
        print(f"🚀 CyberLink P2P | {self.username}")
        print(f"🔑 PubKey : {self.pubkey_bytes.hex()[:24]}…")
        print(f"📡 Режим  : BitTorrent DHT + прямой UDP")
        print("=" * 55)

    # ══════════════════════════════════════════════════════════
    # Вспомогательное
    # ══════════════════════════════════════════════════════════

    def _load_contacts(self) -> List[str]:
        """Читает список контактов из data/contacts.json (любой формат)"""
        path = os.path.join("data", "contacts.json")
        if not os.path.exists(path):
            return []
        try:
            with open(path) as f:
                d = json.load(f)
            if isinstance(d, list):
                return d
            if isinstance(d, dict):
                return list(d.keys())
        except Exception:
            pass
        return []

    # ══════════════════════════════════════════════════════════
    # Публичный API (совместим с остальным кодом проекта)
    # ══════════════════════════════════════════════════════════

    def send_friend_request(self, target: str, message: str = "") -> bool:
        if target.startswith("@"):
            target = target[1:]

        # 1. Если он уже онлайн — отправляем мгновенно
        if target in self.peers:
            return self._send(target, {
                "type": "friend_request",
                "message": message,
                "pubkey": self.pubkey_bytes.hex(),
            })

        # 2. Если не онлайн — пробуем найти его в DHT прямо сейчас
        print(f"🔍 Проверка существования {target} в DHT...")
        self._dht_find(target)

        # Ждем короткое время (1-2 сек), чтобы DHT успел ответить
        # В реальном P2P это может занять больше времени, но для UI это компромисс
        start_wait = time.time()
        while time.time() - start_wait < 2.0:
            if target in self.peers:
                # Нашли! Теперь отправляем
                return self._send(target, {
                    "type": "friend_request",
                    "message": message,
                    "pubkey": self.pubkey_bytes.hex(),
                })
            time.sleep(0.2)

        # 3. Если за 2 секунды никто не ответил — пользователь либо оффлайн, либо не существует
        print(f"❌ Пользователь {target} не найден в сети.")
        return False

    def respond_friend_request(self, target: str, accepted: bool) -> bool:
        if target.startswith("@"):
            target = target[1:]
        self._send_or_queue(target, {"type": "friend_response", "accepted": accepted})
        return True

    def send_message(self, chat_id: str, message: dict) -> bool:
        parts     = chat_id.split("_")
        recipient = parts[0] if len(parts) > 1 and parts[1] == self.username else parts[1]
        self._send_or_queue(recipient, {
            "type": "message", "chat_id": chat_id, "message": message,
        })
        return True

    def find_user(self, username: str) -> Optional[dict]:
        if username.startswith("@"):
            username = username[1:]
        if username in self.peers:
            return {"username": username, "exists": True, "online": True}
        self._dht_find(username)
        return {"username": username, "exists": True, "online": False}

    def add_peer_manual(self, username: str, ip: str, port: int = _MSG_PORT):
        """Добавить пира вручную — по IP, QR-коду или ссылке"""
        self.peers[username] = {"ip": ip, "port": port, "ts": time.time()}
        threading.Thread(
            target=self._handshake, args=(username, ip, port), daemon=True,
        ).start()
        self.friend_online.emit(username)

    def get_my_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "unknown"

    def stop(self):
        self.is_running = False
        if self._dht:
            try:
                state = self._dht.save_state()
                with open(os.path.join("data", "dht.state"), "wb") as f:
                    f.write(lt.bencode(state))
            except Exception:
                pass
        if self._sock:
            self._sock.close()
        print("🛑 P2P остановлен")