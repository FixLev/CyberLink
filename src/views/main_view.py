# src/views/main_view.py
# Главная страница CyberLink

import flet as ft
from src.theme.colors import COLORS


class MainView:
    """Главная страница CyberLink"""
    
    def build(self):
        """Построение главной страницы"""
        
        # === Верхний бар ===
        top_bar = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "✦ CYBERLINK",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Row(
                        [
                            ft.IconButton(ft.icons.SETTINGS, icon_color=ft.Colors.WHITE54),
                            ft.IconButton(ft.icons.REMOVE, icon_color=ft.Colors.WHITE54),
                            ft.IconButton(ft.icons.CROP_SQUARE, icon_color=ft.Colors.WHITE54),
                            ft.IconButton(ft.icons.CLOSE, icon_color=ft.Colors.WHITE54),
                        ]
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=15,
        )
        
        # === Навигация ===
        nav = ft.Container(
            content=ft.Row(
                [
                    self._nav_item("💬", "Чаты", True),
                    self._nav_item("📇", "Контакты", False),
                    self._nav_item("📁", "Файлы", False),
                    self._nav_item("📡", "Каналы", False),
                    self._nav_item("👤", "Профиль", False),
                ],
                spacing=5,
            ),
            padding=(15, 10, 15, 10),
        )
        
        # === Приветствие ===
        welcome = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "🌌 Добро пожаловать в CyberLink!",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS['text_primary'],
                    ),
                    ft.Text(
                        "Космический P2P мессенджер с полным шифрованием",
                        size=16,
                        color=COLORS['text_secondary'],
                    ),
                    ft.Text(
                        "🚀 Скоро здесь будет полный функционал",
                        size=14,
                        color=COLORS['text_dim'],
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
        
        # === Собираем всё вместе ===
        return ft.Column(
            controls=[top_bar, nav, welcome],
            spacing=0,
            expand=True,
        )
    
    def _nav_item(self, icon: str, label: str, is_active: bool = False):
        """Элемент навигации"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(icon, size=18),
                    ft.Text(
                        label,
                        size=13,
                        weight=ft.FontWeight.W_500,
                        color=COLORS['text_primary'] if is_active else COLORS['text_secondary'],
                    ),
                ],
                spacing=8,
            ),
            padding=(16, 8, 16, 8),
            border_radius=10,
            bgcolor=COLORS['accent_primary'] if is_active else ft.Colors.TRANSPARENT,
            opacity=1.0 if is_active else 0.7,
        )