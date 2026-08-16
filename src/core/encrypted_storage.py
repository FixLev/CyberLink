# src/core/encrypted_storage.py
# Шифрованное хранилище - ИСПРАВЛЕННОЕ

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
    
    def save(self, filename: str, data: dict) -> bool:
        """Сохранение зашифрованного файла"""
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
        """Загрузка зашифрованного файла"""
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
                # СОЗДАЁМ НОВЫЙ ФАЙЛ ВМЕСТО ОШИБКИ
                new_data = {}
                self.save(filename, new_data)
                return new_data
            return json.loads(decrypted.decode('utf-8'))
        except json.JSONDecodeError as e:
            print(f"⚠️ Ошибка JSON в {filename}: {e}")
            # СОЗДАЁМ НОВЫЙ ФАЙЛ
            new_data = {}
            self.save(filename, new_data)
            return new_data
        except Exception as e:
            print(f"⚠️ Ошибка загрузки {filename}: {e}")
            return {}
    
    # ===== МЕТОДЫ ДЛЯ АВАТАРОК =====
    
    def encrypt_data(self, data: bytes) -> bytes:
        return self._encrypt(data)
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        return self._decrypt(encrypted_data)
    
    def save_raw(self, filename: str, data: bytes) -> bool:
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
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️ Ошибка загрузки {filename}: {e}")
            return None
    
    def delete(self, filename: str):
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"🗑️ Удалён файл: {filename}")
    
    def exists(self, filename: str) -> bool:
        return os.path.exists(os.path.join(self.data_dir, filename))