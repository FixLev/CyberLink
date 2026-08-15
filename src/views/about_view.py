# src/views/about_view.py
# О программе

import flet as ft
from src.theme.colors import COLORS


class AboutView:
    """Окно 'О программе'"""
    
    def __init__(self, on_close=None):
        self.on_close = on_close
    
    def build(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "ℹ️ О CyberLink",
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
                    ft.Text(
                        "✦ CYBERLINK",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                        letter_spacing=4,
                    ),
                    ft.Text(
                        "Версия 1.0.0",
                        size=14,
                        color=COLORS['text_secondary'],
                    ),
                    ft.Divider(color=COLORS['glass_border']),
                    ft.Text(
                        "Космический P2P мессенджер с полным шифрованием",
                        size=14,
                        color=COLORS['text_primary'],
                    ),
                    ft.Text(
                        "Все данные хранятся локально. Никаких серверов.",
                        size=12,
                        color=COLORS['text_secondary'],
                    ),
                    ft.Divider(color=COLORS['glass_border']),
                    ft.Column(
                        [
                            ft.Text(
                                "🚀 Разработчики:",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=COLORS['text_primary'],
                            ),
                            ft.Text(
                                "• Команда CyberLink",
                                size=13,
                                color=COLORS['text_secondary'],
                            ),
                            ft.Text(
                                "• Дизайнер: твой друг",
                                size=13,
                                color=COLORS['text_secondary'],
                            ),
                        ],
                        spacing=3,
                    ),
                    ft.Divider(color=COLORS['glass_border']),
                    ft.Row(
                        [
                            ft.TextButton(
                                "🐙 GitHub",
                                style=ft.ButtonStyle(color=COLORS['accent_primary']),
                                on_click=lambda e: self._open_link("https://github.com/FixLev/CyberLink"),
                            ),
                            ft.TextButton(
                                "📄 Лицензия",
                                style=ft.ButtonStyle(color=COLORS['accent_primary']),
                                on_click=lambda e: self._open_link("https://github.com/FixLev/CyberLink/blob/main/LICENSE"),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    ft.Text(
                        "© 2026 CyberLink Team",
                        size=11,
                        color=COLORS['text_dim'],
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=25,
            width=400,
            height=500,
            bgcolor=COLORS['bg_secondary'],
            border_radius=16,
            border=ft.border.all(1, COLORS['glass_border']),
        )
    
    def _open_link(self, url: str):
        import webbrowser
        webbrowser.open(url)
    
    def _close(self):
        if self.on_close:
            self.on_close()