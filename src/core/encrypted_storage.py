# src/core/encrypted_storage.py
# Шифрованное хранилище (БЕЗ @)

import os
import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding


class EncryptedStorage:
    """Шифрованное хранилище (БЕЗ @)"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.key = self._derive_key(password)
        
        # Папка пользователя - БЕЗ @
        self.data_dir = os.path.join("data", "users", username)
        os.makedirs(self.data_dir, exist_ok=True)
        
        print(f"🔐 Хранилище для {username} (папка: {self.data_dir})")
    
    def _derive_key(self, password: str) -> bytes:
        salt = b'cyberlink_storage_salt'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())
    
    def _encrypt(self, data: bytes) -> bytes:
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return iv + encrypted
    
    def _decrypt(self, encrypted_data: bytes) -> bytes:
        try:
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted = decryptor.update(ciphertext) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            return unpadder.update(decrypted) + unpadder.finalize()
        except Exception as e:
            print(f"⚠️ Ошибка расшифровки: {e}")
            return b''
    
    # ===== МЕТОДЫ ДЛЯ JSON ДАННЫХ =====
    
    def save(self, filename: str, data: dict) -> bool:
        """Сохранение зашифрованного JSON файла"""
        try:
            json_data = json.dumps(data, indent=2, ensure_ascii=False)
            encrypted = self._encrypt(json_data.encode('utf-8'))
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(base64.b64encode(encrypted).decode('ascii'))
            print(f"💾 Сохранён зашифрованный файл: {filename}")
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения {filename}: {e}")
            return False
    
    def load(self, filename: str) -> dict:
        """Загрузка зашифрованного JSON файла"""
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            print(f"📄 Файл {filename} не найден, создаём новый")
            return {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                encrypted_b64 = f.read().strip()
            if not encrypted_b64:
                print(f"📄 Файл {filename} пуст, создаём новый")
                return {}
            encrypted = base64.b64decode(encrypted_b64)
            decrypted = self._decrypt(encrypted)
            if not decrypted:
                print(f"⚠️ Не удалось расшифровать {filename}")
                return {}
            return json.loads(decrypted.decode('utf-8'))
        except json.JSONDecodeError as e:
            print(f"⚠️ Ошибка JSON в {filename}: {e}")
            return {}
        except Exception as e:
            print(f"⚠️ Ошибка загрузки {filename}: {e}")
            return {}
    
    # ===== МЕТОДЫ ДЛЯ АВАТАРОК (БИНАРНЫЕ ДАННЫЕ) =====
    
    def encrypt_data(self, data: bytes) -> bytes:
        """Шифрование бинарных данных (для аватарок)"""
        return self._encrypt(data)
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Расшифровка бинарных данных (для аватарок)"""
        return self._decrypt(encrypted_data)
    
    def save_raw(self, filename: str, data: bytes) -> bool:
        """Сохранение зашифрованных бинарных данных"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(data)
            print(f"💾 Сохранён зашифрованный файл: {filename}")
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения {filename}: {e}")
            return False
    
    def load_raw(self, filename: str) -> bytes:
        """Загрузка зашифрованных бинарных данных"""
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️ Ошибка загрузки {filename}: {e}")
            return None
    
    # ===== ОБЩИЕ МЕТОДЫ =====
    
    def delete(self, filename: str):
        """Удаление файла"""
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"🗑️ Удалён файл: {filename}")
    
    def exists(self, filename: str) -> bool:
        """Проверка существования файла"""
        return os.path.exists(os.path.join(self.data_dir, filename))