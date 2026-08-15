# src/views/__init__.py
# Экспорт всех страниц

from .main_view import MainView
from .login_view import LoginView
from .chat_view import ChatView
from .profile_view import ProfileView
from .settings_view import SettingsView

__all__ = [
    'MainView',
    'LoginView',
    'ChatView',
    'ProfileView',
    'SettingsView',
]