# src/widgets/star_field.py
# Космический фон с мерцающими звёздами

import random
import math
import time
import flet as ft
from src.theme.colors import COLORS


class StarField(ft.BaseControl):
    """Анимированное звездное поле"""
    
    def __init__(self, star_count: int = 100):
        super().__init__()
        self.star_count = star_count
        self.stars = []
        self._animation_running = True
        self._controls = []
    
    def did_mount(self):
        """Запуск анимации при монтировании"""
        self.update_stars()
        self.start_animation()
    
    def will_unmount(self):
        """Остановка анимации при размонтировании"""
        self._animation_running = False
    
    def start_animation(self):
        """Запуск анимации мерцания"""
        if not self._animation_running:
            return
        self.page.after(50, self._animate)
    
    def _animate(self):
        """Обновление состояния звёзд"""
        if not self._animation_running:
            return
        
        for star in self.stars:
            star['opacity'] = 0.3 + 0.7 * abs(math.sin(time.time() * star['speed'] + star['phase']))
        
        self.update()
        self.page.after(100, self._animate)
    
    def update_stars(self):
        """Генерация звёзд"""
        self.stars = []
        for _ in range(self.star_count):
            self.stars.append({
                'x': random.uniform(0, 1),
                'y': random.uniform(0, 1),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.3, 1.5),
                'phase': random.uniform(0, 2 * math.pi),
                'opacity': random.uniform(0.3, 1.0),
            })
    
    def build(self):
        """Построение виджета"""
        return ft.Stack(
            controls=self._build_stars(),
            expand=True,
        )
    
    def _build_stars(self):
        """Создание виджетов звёзд"""
        self._controls = []
        for star in self.stars:
            self._controls.append(
                ft.Container(
                    width=star['size'],
                    height=star['size'],
                    bgcolor=ft.colors.WHITE,
                    border_radius=ft.border_radius.all(star['size'] // 2),
                    opacity=star['opacity'],
                    left=star['x'] * 100 - star['size'] / 2,
                    top=star['y'] * 100 - star['size'] / 2,
                )
            )
        return self._controls