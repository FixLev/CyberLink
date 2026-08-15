# src/views/profile_view.py
# Страница профиля

import flet as ft
from src.theme.colors import COLORS


class ProfileView:
    """Страница профиля пользователя"""
    
    def __init__(self, username: str = "@Electric_Eye"):
        self.username = username
    
    def build(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Text("👤", size=80),
                        width=120,
                        height=120,
                        alignment=ft.alignment.center,
                        bgcolor=COLORS['bg_card'],
                        border_radius=60,
                        border=ft.border.all(2, COLORS['accent_primary']),
                    ),
                    ft.Text(
                        self.username,
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS['text_primary'],
                    ),
                    ft.Text(
                        "Кибер-энтузиаст | Тестировщик",
                        size=14,
                        color=COLORS['text_secondary'],
                    ),
                    ft.Row(
                        [
                            ft.Text("🟢 Онлайн", color=COLORS['online']),
                            ft.Text("•", color=COLORS['text_dim']),
                            ft.Text("📍 Москва", color=COLORS['text_dim']),
                        ],
                        spacing=5,
                    ),
                    ft.Divider(color=COLORS['glass_border']),
                    ft.Row(
                        [
                            self._build_stat_item("📊", "12", "Чатов"),
                            ft.VerticalDivider(width=1, color=COLORS['glass_border']),
                            self._build_stat_item("👥", "8", "Контактов"),
                            ft.VerticalDivider(width=1, color=COLORS['glass_border']),
                            self._build_stat_item("📁", "23", "Файлов"),
                        ],
                        spacing=20,
                    ),
                    ft.Divider(color=COLORS['glass_border']),
                    ft.Column(
                        [
                            self._build_info_row("📱 Телефон", "+7 (999) 123-45-67"),
                            self._build_info_row("📧 Email", "alex@example.com"),
                            self._build_info_row("📅 Дата рождения", "15.06.1995"),
                            self._build_info_row("🏙️ Город", "Москва, Россия"),
                            self._build_info_row("💼 Должность", "Software Developer"),
                            self._build_info_row("🏢 Компания", "CyberLink Inc."),
                        ],
                        spacing=5,
                    ),
                    ft.Divider(color=COLORS['glass_border']),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "✏️ Редактировать",
                                icon="edit",
                                style=ft.ButtonStyle(
                                    bgcolor=COLORS['accent_primary'],
                                    color=ft.Colors.WHITE,
                                    padding=(20, 10, 20, 10),
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                            ),
                            ft.OutlinedButton(
                                "📤 Экспорт данных",
                                icon="download",
                                style=ft.ButtonStyle(
                                    color=COLORS['text_secondary'],
                                    padding=(20, 10, 20, 10),
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                            ),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True,
            padding=20,
        )
    
    def _build_stat_item(self, icon, value, label):
        return ft.Column(
            [
                ft.Text(icon, size=24),
                ft.Text(
                    value,
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS['text_primary'],
                ),
                ft.Text(
                    label,
                    size=12,
                    color=COLORS['text_dim'],
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        )
    
    def _build_info_row(self, label, value):
        return ft.Row(
            [
                ft.Text(
                    label,
                    size=13,
                    color=COLORS['text_secondary'],
                    width=120,
                ),
                ft.Text(
                    value,
                    size=13,
                    color=COLORS['text_primary'],
                ),
            ],
            spacing=10,
        )