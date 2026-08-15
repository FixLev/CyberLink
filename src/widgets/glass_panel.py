# src/widgets/glass_panel.py
# Стеклянная панель с эффектом размытия

import flet as ft
from src.theme.colors import COLORS


class GlassPanel(ft.Container):
    """Стеклянная панель с эффектом Glassmorphism"""
    
    def __init__(
        self,
        content: ft.Control = None,
        padding: ft.PaddingValue = None,
        margin: ft.MarginValue = None,
        width: int = None,
        height: int = None,
        expand: bool = False,
        border_radius: int = 16,
        **kwargs
    ):
        super().__init__(
            content=content,
            padding=padding or ft.padding.all(15),
            margin=margin or ft.margin.all(0),
            width=width,
            height=height,
            expand=expand,
            border_radius=ft.border_radius.all(border_radius),
            bgcolor=COLORS['glass_bg'],
            border=ft.border.all(1, COLORS['glass_border']),
            **kwargs
        )
        
        # Добавляем эффект размытия (доступно в Flet)
        # Примечание: backdrop_filter поддерживается не во всех версиях
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=20,
            color=ft.colors.with_opacity(0.2, ft.colors.BLACK),
        )