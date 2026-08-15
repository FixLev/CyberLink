# src/views/login_view.py
# Окно входа и регистрации

import flet as ft
from src.theme.colors import COLORS


class LoginView:
    """Окно входа в CyberLink"""
    
    def __init__(self, on_login=None):
        self.on_login = on_login
        self.is_login = True
    
    def build(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "✦ CYBERLINK",
                        size=36,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                        letter_spacing=6,
                    ),
                    ft.Text(
                        "Космический P2P мессенджер",
                        size=14,
                        color=COLORS['text_secondary'],
                    ),
                    ft.Divider(color=COLORS['glass_border'], height=20),
                    ft.Text(
                        "🔐 Вход в систему" if self.is_login else "📝 Регистрация",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS['text_primary'],
                    ),
                    ft.TextField(
                        label="Логин (@никнейм)",
                        hint_text="Введите логин",
                        prefix_icon="person",
                        border_color=COLORS['glass_border'],
                        focused_border_color=COLORS['accent_primary'],
                        text_style=ft.TextStyle(color=COLORS['text_primary']),
                        label_style=ft.TextStyle(color=COLORS['text_secondary']),
                    ),
                    ft.TextField(
                        label="Пароль",
                        hint_text="Введите пароль",
                        password=True,
                        can_reveal_password=True,
                        prefix_icon="lock",
                        border_color=COLORS['glass_border'],
                        focused_border_color=COLORS['accent_primary'],
                        text_style=ft.TextStyle(color=COLORS['text_primary']),
                        label_style=ft.TextStyle(color=COLORS['text_secondary']),
                    ),
                    ft.ElevatedButton(
                        "🚀 Войти" if self.is_login else "📝 Создать аккаунт",
                        style=ft.ButtonStyle(
                            bgcolor=COLORS['accent_primary'],
                            color=ft.Colors.WHITE,
                            padding=(40, 15, 40, 15),  # left, top, right, bottom
                            shape=ft.RoundedRectangleBorder(radius=12),
                            text_style=ft.TextStyle(size=14),
                        ),
                        on_click=self._handle_auth,
                        width=300,
                    ),
                    ft.Row(
                        [
                            ft.Text(
                                "Ещё нет аккаунта?" if self.is_login else "Уже есть аккаунт?",
                                color=COLORS['text_secondary'],
                            ),
                            ft.TextButton(
                                "Зарегистрироваться" if self.is_login else "Войти",
                                style=ft.ButtonStyle(color=COLORS['accent_primary']),
                                on_click=self._toggle_mode,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=5,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            ),
            alignment=ft.alignment.center,
            expand=True,
            bgcolor=ft.Colors.TRANSPARENT,
        )
    
    def _toggle_mode(self, e):
        self.is_login = not self.is_login
        e.page.update()
    
    def _handle_auth(self, e):
        if self.is_login:
            print("🔐 Выполняется вход...")
        else:
            print("📝 Выполняется регистрация...")