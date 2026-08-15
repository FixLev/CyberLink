# src/theme/styles.py
# Общие стили для интерфейса

import flet as ft
from src.theme.colors import COLORS


def get_global_theme() -> ft.Theme:
    """Глобальная тема приложения"""
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=COLORS['accent_primary'],
            on_primary=ft.colors.WHITE,
            secondary=COLORS['accent_secondary'],
            background=COLORS['bg_primary'],
            surface=COLORS['bg_card'],
            on_surface=COLORS['text_primary'],
            on_background=COLORS['text_secondary'],
        ),
        visual_density=ft.VisualDensity.COMPACT,
        font_family="Interphases",
    )


def get_button_style() -> ft.ButtonStyle:
    """Стиль кнопок"""
    return ft.ButtonStyle(
        bgcolor=COLORS['accent_primary'],
        color=ft.colors.WHITE,
        padding=ft.padding.symmetric(horizontal=20, vertical=12),
        shape=ft.RoundedRectangleBorder(radius=10),
        text_style=ft.TextStyle(
            font_family="InterphasesBold",
            size=14,
        ),
    )


def get_text_field_style() -> dict:
    """Стиль полей ввода"""
    return {
        "border_color": COLORS['glass_border'],
        "focused_border_color": COLORS['accent_primary'],
        "text_style": ft.TextStyle(
            color=COLORS['text_primary'],
            font_family="Interphases",
        ),
        "label_style": ft.TextStyle(
            color=COLORS['text_secondary'],
            font_family="Interphases",
        ),
        "hint_style": ft.TextStyle(
            color=COLORS['text_dim'],
            font_family="Interphases",
        ),
    }


def get_glass_panel_style() -> dict:
    """Стиль стеклянной панели"""
    return {
        "bgcolor": COLORS['glass_bg'],
        "border": ft.border.all(1, COLORS['glass_border']),
        "border_radius": ft.border_radius.all(16),
    }


def get_chat_item_style(is_unread: bool = False) -> dict:
    """Стиль элемента списка чатов"""
    return {
        "padding": ft.padding.all(10),
        "border_radius": ft.border_radius.all(10),
        "bgcolor": COLORS['bg_hover'] if is_unread else ft.colors.TRANSPARENT,
    }


def get_message_style(is_my: bool = True) -> dict:
    """Стиль облачка сообщения"""
    return {
        "padding": ft.padding.all(12),
        "bgcolor": COLORS['glass_bg'] if is_my else COLORS['bg_card'],
        "border_radius": ft.border_radius.only(
            top_left=15,
            top_right=15,
            bottom_left=5 if is_my else 15,
            bottom_right=15 if is_my else 5,
        ),
        "border": ft.border.all(1, COLORS['glass_border']),
    }