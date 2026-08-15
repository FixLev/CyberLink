# src/theme/icons.py
# Менеджер иконок с возможностью быстрой замены на SVG

class Icons:
    """Централизованное хранилище иконок"""
    
    # Режим: 'emoji' или 'svg' (потом поменяем)
    _mode = 'emoji'
    
    @classmethod
    def set_mode(cls, mode: str):
        """Переключение режима иконок"""
        cls._mode = mode
    
    @classmethod
    def get(cls, emoji: str, svg_path: str = None) -> str:
        """Получение иконки в зависимости от режима"""
        if cls._mode == 'svg' and svg_path:
            return svg_path
        return emoji
    
    # ============================================
    # Основные действия
    # ============================================
    @classmethod
    def ATTACH(cls):
        return cls.get('📎', 'assets/icons/attach.svg')
    
    @classmethod
    def SEND(cls):
        return cls.get('📤', 'assets/icons/send.svg')
    
    @classmethod
    def CALL(cls):
        return cls.get('📞', 'assets/icons/call.svg')
    
    @classmethod
    def RECORD_CIRCLE(cls):
        return cls.get('🔄', 'assets/icons/record_circle.svg')
    
    @classmethod
    def RECORD_VOICE(cls):
        return cls.get('🎙️', 'assets/icons/record_voice.svg')
    
    @classmethod
    def EMOJI(cls):
        return cls.get('😊', 'assets/icons/emoji.svg')
    
    # ============================================
    # Навигация
    # ============================================
    @classmethod
    def BACK(cls):
        return cls.get('◀️', 'assets/icons/back.svg')
    
    @classmethod
    def SETTINGS(cls):
        return cls.get('⚙️', 'assets/icons/settings.svg')
    
    @classmethod
    def SEARCH(cls):
        return cls.get('🔍', 'assets/icons/search.svg')
    
    @classmethod
    def REFRESH(cls):
        return cls.get('🔄', 'assets/icons/refresh.svg')
    
    # ============================================
    # Управление сообщениями
    # ============================================
    @classmethod
    def DELETE(cls):
        return cls.get('🗑️', 'assets/icons/delete.svg')
    
    @classmethod
    def PIN(cls):
        return cls.get('📌', 'assets/icons/pin.svg')
    
    @classmethod
    def EDIT(cls):
        return cls.get('✏️', 'assets/icons/edit.svg')
    
    @classmethod
    def COPY(cls):
        return cls.get('📋', 'assets/icons/copy.svg')
    
    @classmethod
    def FORWARD(cls):
        return cls.get('➡️', 'assets/icons/forward.svg')
    
    @classmethod
    def REPLY(cls):
        return cls.get('↩️', 'assets/icons/reply.svg')
    
    # ============================================
    # Навигационные вкладки
    # ============================================
    @classmethod
    def CHATS(cls):
        return cls.get('💬', 'assets/icons/chats.svg')
    
    @classmethod
    def CONTACTS(cls):
        return cls.get('📇', 'assets/icons/contacts.svg')
    
    @classmethod
    def FILES(cls):
        return cls.get('📁', 'assets/icons/files.svg')
    
    @classmethod
    def CHANNELS(cls):
        return cls.get('📡', 'assets/icons/channels.svg')
    
    @classmethod
    def PROFILE(cls):
        return cls.get('👤', 'assets/icons/profile.svg')