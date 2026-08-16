# src/core/profile_manager.py
# Управление профилем пользователя (БЕЗ @, С ШИФРОВАНИЕМ АВАТАРОК)

import json
import os
import base64
from pathlib import Path
from datetime import datetime
from PIL import Image
import io

from PyQt5.QtGui import QPixmap, QImage

from src.core.encrypted_storage import EncryptedStorage


class ProfileManager:
    """Управление профилем пользователя (без @, с шифрованием)"""
    
    def __init__(self, username: str, password: str = None):
        self.username = username
        self.password = password
        
        # Папка пользователя - БЕЗ @
        self.data_dir = Path("data") / "users" / username
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаём зашифрованное хранилище
        if password:
            self.storage = EncryptedStorage(username, password)
        else:
            self.storage = None
        
        # Аватарка хранится в зашифрованном виде
        self.avatar_key = "avatar.jpg.encrypted"
    
    def _get_storage(self) -> EncryptedStorage:
        """Получение хранилища"""
        if not self.storage:
            if self.password:
                self.storage = EncryptedStorage(self.username, self.password)
            else:
                self.storage = EncryptedStorage(self.username, "temp_password")
        return self.storage
    
    # ============================================
    # РАБОТА С ПРОФИЛЕМ (ЗАШИФРОВАНО)
    # ============================================
    
    def get_profile(self) -> dict:
        """Получение профиля (зашифровано)"""
        try:
            storage = self._get_storage()
            profile = storage.load('profile.json')
            if not profile:
                profile = self._default_profile()
                storage.save('profile.json', profile)
            return profile
        except Exception as e:
            print(f"⚠️ Ошибка загрузки профиля: {e}")
            return self._default_profile()
    
    def save_profile(self, profile: dict):
        """Сохранение профиля (зашифровано)"""
        try:
            storage = self._get_storage()
            storage.save('profile.json', profile)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения профиля: {e}")
    
    def update_profile(self, data: dict) -> bool:
        """Обновление профиля (зашифровано)"""
        try:
            profile = self.get_profile()
            for key, value in data.items():
                if key in profile:
                    profile[key] = value
            profile["updated_at"] = datetime.now().isoformat()
            self.save_profile(profile)
            return True
        except Exception as e:
            print(f"⚠️ Ошибка обновления профиля: {e}")
            return False
    
    def _default_profile(self) -> dict:
        """Профиль по умолчанию"""
        return {
            "username": self.username,
            "display_name": self.username,
            "status": "В сети",
            "bio": "",
            "phone": "",
            "email": "",
            "birth_date": "",
            "city": "",
            "country": "",
            "occupation": "",
            "company": "",
            "gender": "Не указан",
            "has_avatar": False,  # Флаг наличия аватарки
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
    
    # ============================================
    # РАБОТА С АВАТАРКОЙ (ЗАШИФРОВАНО)
    # ============================================
    
    def get_avatar(self):
        """Получение аватарки (расшифровка)"""
        try:
            storage = self._get_storage()
            
            # Проверяем, есть ли зашифрованная аватарка
            if not storage.exists(self.avatar_key):
                return None
            
            # Загружаем зашифрованные данные
            encrypted_data = storage.load_raw(self.avatar_key)
            if not encrypted_data:
                return None
            
            # Расшифровываем
            avatar_bytes = storage.decrypt_data(encrypted_data)
            if not avatar_bytes:
                return None
            
            # Конвертируем в QPixmap
            image = QImage.fromData(avatar_bytes)
            if image.isNull():
                return None
            
            return QPixmap.fromImage(image)
            
        except Exception as e:
            print(f"⚠️ Ошибка загрузки аватарки: {e}")
            return None
    
    def set_avatar(self, image_path: str) -> bool:
        """Установка аватарки (шифрование)"""
        try:
            # Открываем изображение
            img = Image.open(image_path)
            
            # Конвертируем в RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb = Image.new('RGB', img.size, (255, 255, 255))
                rgb.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb
            
            # Ресайзим
            img.thumbnail((512, 512), Image.Resampling.LANCZOS)
            
            # Делаем квадратным
            size = max(img.size)
            new_img = Image.new('RGB', (size, size), (0, 0, 0))
            new_img.paste(img, ((size - img.width) // 2, (size - img.height) // 2))
            new_img = new_img.resize((512, 512), Image.Resampling.LANCZOS)
            
            # Конвертируем в байты JPEG
            buffer = io.BytesIO()
            new_img.save(buffer, format='JPEG', quality=85, optimize=True)
            image_bytes = buffer.getvalue()
            
            # Шифруем и сохраняем
            storage = self._get_storage()
            encrypted = storage.encrypt_data(image_bytes)
            storage.save_raw(self.avatar_key, encrypted)
            
            # Обновляем профиль
            profile = self.get_profile()
            profile["has_avatar"] = True
            self.save_profile(profile)
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка сохранения аватарки: {e}")
            return False
    
    def remove_avatar(self) -> bool:
        """Удаление аватарки"""
        try:
            storage = self._get_storage()
            storage.delete(self.avatar_key)
            
            profile = self.get_profile()
            profile["has_avatar"] = False
            self.save_profile(profile)
            
            return True
        except Exception as e:
            print(f"❌ Ошибка удаления аватарки: {e}")
            return False
    
    # ============================================
    # РАБОТА С КОНТАКТАМИ (ЗАШИФРОВАНО)
    # ============================================
    
    def get_contacts(self) -> dict:
        """Получение контактов (зашифровано)"""
        try:
            storage = self._get_storage()
            contacts = storage.load('contacts.json')
            if not contacts:
                contacts = {"contacts": [], "pending": [], "blocked": []}
                storage.save('contacts.json', contacts)
            return contacts
        except:
            return {"contacts": [], "pending": [], "blocked": []}
    
    def save_contacts(self, contacts: dict):
        """Сохранение контактов (зашифровано)"""
        try:
            storage = self._get_storage()
            storage.save('contacts.json', contacts)
        except:
            pass
    
    def add_contact(self, username: str) -> bool:
        """Добавление контакта"""
        contacts = self.get_contacts()
        if username not in contacts["contacts"] and username not in contacts["pending"]:
            contacts["pending"].append(username)
            self.save_contacts(contacts)
            return True
        return False
    
    def accept_contact(self, username: str) -> bool:
        """Принятие контакта"""
        contacts = self.get_contacts()
        if username in contacts["pending"]:
            contacts["pending"].remove(username)
            if username not in contacts["contacts"]:
                contacts["contacts"].append(username)
            self.save_contacts(contacts)
            return True
        return False
    
    def remove_contact(self, username: str) -> bool:
        """Удаление контакта"""
        contacts = self.get_contacts()
        if username in contacts["contacts"]:
            contacts["contacts"].remove(username)
            self.save_contacts(contacts)
            return True
        return False
    
    # ============================================
    # РАБОТА С НАСТРОЙКАМИ (ЗАШИФРОВАНО)
    # ============================================
    
    def get_settings(self) -> dict:
        """Получение настроек (зашифровано)"""
        try:
            storage = self._get_storage()
            settings = storage.load('settings.json')
            if not settings:
                settings = self._default_settings()
                storage.save('settings.json', settings)
            return settings
        except:
            return self._default_settings()
    
    def save_settings(self, settings: dict):
        """Сохранение настроек (зашифровано)"""
        try:
            storage = self._get_storage()
            storage.save('settings.json', settings)
        except:
            pass
    
    def _default_settings(self) -> dict:
        return {
            "theme": "dark",
            "language": "ru",
            "notifications": True,
            "sound": True,
            "font_size": 14,
        }
    
    # ============================================
    # РАБОТА С ПРИВАТНОСТЬЮ (ЗАШИФРОВАНО)
    # ============================================
    
    def get_privacy(self) -> dict:
        """Получение настроек приватности (зашифровано)"""
        try:
            storage = self._get_storage()
            privacy = storage.load('privacy.json')
            if not privacy:
                privacy = self._default_privacy()
                storage.save('privacy.json', privacy)
            return privacy
        except:
            return self._default_privacy()
    
    def save_privacy(self, privacy: dict):
        """Сохранение настроек приватности (зашифровано)"""
        try:
            storage = self._get_storage()
            storage.save('privacy.json', privacy)
        except:
            pass
    
    def update_privacy(self, data: dict) -> bool:
        """Обновление настроек приватности"""
        try:
            privacy = self.get_privacy()
            for key, value in data.items():
                if isinstance(value, dict) and key in privacy and isinstance(privacy[key], dict):
                    privacy[key].update(value)
                else:
                    privacy[key] = value
            self.save_privacy(privacy)
            return True
        except:
            return False
    
    def _default_privacy(self) -> dict:
        return {
            "status": "online",
            "last_seen": {"level": "contacts", "selected": []},
            "phone": {"level": "contacts", "selected": []},
            "email": {"level": "contacts", "selected": []},
            "gender": {"level": "contacts", "selected": []},
            "birth_date": {"level": "contacts", "selected": []},
            "city": {"level": "contacts", "selected": []},
            "country": {"level": "contacts", "selected": []},
            "occupation": {"level": "contacts", "selected": []},
            "company": {"level": "contacts", "selected": []},
            "bio": {"level": "everyone", "selected": []},
            "read_receipts": True,
            "who_can_add_me": "everyone",
            "who_can_message_me": "everyone",
            "who_can_call_me": "contacts",
        }
    
    def set_status(self, status: str) -> bool:
        """Установка статуса"""
        privacy = self.get_privacy()
        privacy["status"] = status
        self.save_privacy(privacy)
        return True
    
    def get_status(self) -> str:
        """Получение статуса"""
        privacy = self.get_privacy()
        return privacy.get("status", "online")