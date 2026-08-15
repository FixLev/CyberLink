# src/views/__init__.py
# Экспорт всех страниц

from .main_view import MainView
from .login_view import LoginView
from .settings_view import SettingsView
from .profile_view import ProfileView
from .about_view import AboutView

__all__ = [
    'MainView',
    'LoginView',
    'SettingsView',
    'ProfileView',
    'AboutView',
]