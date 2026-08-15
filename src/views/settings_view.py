# src/views/settings_view.py
# Окно настроек

import flet as ft
from src.theme.colors import COLORS


class SettingsView:
    """Окно настроек CyberLink"""
    
    def __init__(self, on_close=None):
        self.on_close = on_close
    
    def build(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "⚙️ Настройки",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=COLORS['text_primary'],
                            ),
                            ft.IconButton(
                                "close",
                                icon_color=COLORS['text_secondary'],
                                on_click=lambda e: self._close(),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(color=COLORS['glass_border']),
                    ft.ListView(
                        [
                            self._build_setting_item(
                                "🎨 Внешний вид",
                                "Тема, обои, шрифты",
                                "palette",
                            ),
                            self._build_setting_item(
                                "🔒 Приватность",
                                "Кто видит профиль, кто может писать",
                                "privacy_tip",
                            ),
                            self._build_setting_item(
                                "🔔 Уведомления",
                                "Звук, вибро, всплывающие",
                                "notifications",
                            ),
                            self._build_setting_item(
                                "💾 Хранилище",
                                "Автозагрузка, кэш, бэкап",
                                "storage",
                            ),
                            self._build_setting_item(
                                "🛡️ Безопасность",
                                "Смена пароля, сессии, 2FA",
                                "security",
                            ),
                            self._build_setting_item(
                                "ℹ️ О программе",
                                "Версия, разработчики",
                                "info",
                            ),
                        ],
                        spacing=5,
                        expand=True,
                    ),
                ],
                spacing=10,
                expand=True,
            ),
            padding=20,
            width=500,
            height=500,
            bgcolor=COLORS['bg_secondary'],
            border_radius=16,
            border=ft.border.all(1, COLORS['glass_border']),
        )
    
    def _build_setting_item(self, title, description, icon):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, color=COLORS['accent_primary'], size=24),
                    ft.Column(
                        [
                            ft.Text(
                                title,
                                size=14,
                                weight=ft.FontWeight.W_500,
                                color=COLORS['text_primary'],
                            ),
                            ft.Text(
                                description,
                                size=12,
                                color=COLORS['text_secondary'],
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Icon("chevron_right", color=COLORS['text_dim']),
                ],
            ),
            padding=12,
            border_radius=10,
            bgcolor=COLORS['bg_hover'],
            on_click=lambda e: self._open_setting(title),
        )
    
    def _open_setting(self, title):
        print(f"📂 Открыта настройка: {title}")
    
    def _close(self):
        if self.on_close:
            self.on_close()