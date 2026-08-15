# src/core/profile_manager.py
# Управление профилем пользователя

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from PIL import Image

from PyQt5.QtGui import QPixmap, QImage


class ProfileManager:
    """Управление профилем пользователя"""
    
    def __init__(self, username):
        self.username = username
        self.data_dir = Path("data") / "users" / f"@{username}"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.profile_file = self.data_dir / "profile.json"
        self.avatar_file = self.data_dir / "avatar.jpg"
        self.contacts_file = self.data_dir / "contacts.json"
        self.groups_file = self.data_dir / "groups.json"
        self.settings_file = self.data_dir / "settings.json"
        self.privacy_file = self.data_dir / "privacy.json"
        
        if not self.profile_file.exists():
            self._create_default_profile()
        
        if not self.settings_file.exists():
            self._create_default_settings()
        
        if not self.privacy_file.exists():
            self._create_default_privacy()
        
        if not self.contacts_file.exists():
            self._create_default_contacts()
        
        if not self.groups_file.exists():
            self._create_default_groups()
    
    def _create_default_profile(self):
        profile = {
            "username": self.username,
            "display_name": self.username,
            "bio": "",
            "phone": "",
            "email": "",
            "birth_date": "",
            "city": "",
            "country": "",
            "occupation": "",
            "company": "",
            "gender": "Не указан",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
    
    def _create_default_settings(self):
        settings = {
            "theme": "dark",
            "language": "ru",
            "notifications": True,
            "sound": True,
            "font_size": 14,
            "auto_download_media": True,
        }
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    
    def _create_default_privacy(self):
        privacy = {
            "status": "online",
            "last_seen": {"level": "contacts", "selected": []},
            "profile_photo": {"level": "everyone", "selected": []},
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
        with open(self.privacy_file, 'w', encoding='utf-8') as f:
            json.dump(privacy, f, indent=2, ensure_ascii=False)
    
    def _create_default_contacts(self):
        contacts = {"contacts": [], "pending": [], "blocked": []}
        with open(self.contacts_file, 'w', encoding='utf-8') as f:
            json.dump(contacts, f, indent=2, ensure_ascii=False)
    
    def _create_default_groups(self):
        groups = {"groups": []}
        with open(self.groups_file, 'w', encoding='utf-8') as f:
            json.dump(groups, f, indent=2, ensure_ascii=False)
    
    # ============================================
    # РАБОТА С ПРОФИЛЕМ
    # ============================================
    
    def get_profile(self):
        with open(self.profile_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_profile(self, data):
        profile = self.get_profile()
        for key, value in data.items():
            if key in profile:
                profile[key] = value
        profile["updated_at"] = datetime.now().isoformat()
        
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        return True
    
    def get_avatar(self):
        if self.avatar_file.exists():
            pixmap = QPixmap(str(self.avatar_file))
            if not pixmap.isNull():
                return pixmap
        return None
    
    def set_avatar(self, image_path):
        try:
            img = Image.open(image_path)
            
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb = Image.new('RGB', img.size, (255, 255, 255))
                rgb.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb
            
            img.thumbnail((512, 512), Image.Resampling.LANCZOS)
            
            size = max(img.size)
            new_img = Image.new('RGB', (size, size), (0, 0, 0))
            new_img.paste(img, ((size - img.width) // 2, (size - img.height) // 2))
            
            new_img = new_img.resize((512, 512), Image.Resampling.LANCZOS)
            new_img.save(str(self.avatar_file), 'JPEG', quality=85, optimize=True)
            
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки аватарки: {e}")
            return False
    
    # ============================================
    # РАБОТА С ПРИВАТНОСТЬЮ
    # ============================================
    
    def get_privacy(self):
        with open(self.privacy_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_privacy(self, data):
        privacy = self.get_privacy()
        for key, value in data.items():
            if isinstance(value, dict) and key in privacy and isinstance(privacy[key], dict):
                privacy[key].update(value)
            else:
                privacy[key] = value
        
        with open(self.privacy_file, 'w', encoding='utf-8') as f:
            json.dump(privacy, f, indent=2, ensure_ascii=False)
        return True
    
    def set_status(self, status):
        privacy = self.get_privacy()
        privacy["status"] = status
        with open(self.privacy_file, 'w', encoding='utf-8') as f:
            json.dump(privacy, f, indent=2, ensure_ascii=False)
        return True
    
    def get_status(self):
        privacy = self.get_privacy()
        return privacy.get("status", "online")
    
    # ============================================
    # РАБОТА С КОНТАКТАМИ
    # ============================================
    
    def get_contacts(self):
        with open(self.contacts_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def add_contact(self, username):
        contacts = self.get_contacts()
        if username not in contacts["contacts"] and username not in contacts["pending"]:
            contacts["pending"].append(username)
            with open(self.contacts_file, 'w', encoding='utf-8') as f:
                json.dump(contacts, f, indent=2, ensure_ascii=False)
            return True
        return False
    
    def accept_contact(self, username):
        contacts = self.get_contacts()
        if username in contacts["pending"]:
            contacts["pending"].remove(username)
            if username not in contacts["contacts"]:
                contacts["contacts"].append(username)
            with open(self.contacts_file, 'w', encoding='utf-8') as f:
                json.dump(contacts, f, indent=2, ensure_ascii=False)
            return True
        return False
    
    def remove_contact(self, username):
        contacts = self.get_contacts()
        if username in contacts["contacts"]:
            contacts["contacts"].remove(username)
            with open(self.contacts_file, 'w', encoding='utf-8') as f:
                json.dump(contacts, f, indent=2, ensure_ascii=False)
            return True
        return False
    
    def block_user(self, username):
        contacts = self.get_contacts()
        if username not in contacts["blocked"]:
            contacts["blocked"].append(username)
            if username in contacts["contacts"]:
                contacts["contacts"].remove(username)
            with open(self.contacts_file, 'w', encoding='utf-8') as f:
                json.dump(contacts, f, indent=2, ensure_ascii=False)
            return True
        return False
    
    def unblock_user(self, username):
        contacts = self.get_contacts()
        if username in contacts["blocked"]:
            contacts["blocked"].remove(username)
            with open(self.contacts_file, 'w', encoding='utf-8') as f:
                json.dump(contacts, f, indent=2, ensure_ascii=False)
            return True
        return False