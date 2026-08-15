# src/views/main_view.py
# Главное окно CyberLink с космосом и кометой

import random
import math
import time
from pathlib import Path

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.theme.colors import COLORS


# ============================================
# КОСМИЧЕСКИЙ ФОН
# ============================================

class SpaceWidget(QWidget):
    """Анимированный космический фон"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        
        self.stars = []
        for _ in range(250):
            self.stars.append({
                'x': random.randint(0, 10000),
                'y': random.randint(0, 10000),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.3, 0.8),
                'phase': random.uniform(0, 6.28),
                'opacity': random.uniform(0.2, 1.0),
                'brightness': random.uniform(150, 255),
            })
        
        self.comets = []
        self.comet_tails = []
        self.next_comet_time = time.time() + 3.0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)
    
    def _create_comet(self):
        side = random.choice(['left', 'right', 'top', 'bottom'])
        
        angle = random.uniform(20, 60) * (1 if random.choice([True, False]) else -1)
        speed = random.uniform(150, 250)
        
        if side == 'left':
            x = random.randint(-200, 0)
            y = random.randint(0, 10000)
            dx = speed * math.cos(math.radians(angle))
            dy = speed * math.sin(math.radians(angle))
        elif side == 'right':
            x = random.randint(10000, 10200)
            y = random.randint(0, 10000)
            dx = -speed * math.cos(math.radians(angle))
            dy = speed * math.sin(math.radians(angle))
        elif side == 'top':
            x = random.randint(0, 10000)
            y = random.randint(-200, 0)
            dx = speed * math.sin(math.radians(angle))
            dy = speed * math.cos(math.radians(angle))
        else:
            x = random.randint(0, 10000)
            y = random.randint(10000, 10200)
            dx = speed * math.sin(math.radians(angle))
            dy = -speed * math.cos(math.radians(angle))
        
        return {
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy,
            'size': random.randint(5, 8),
            'life': 0,
            'max_life': random.uniform(3, 5),
            'history': [],
            'is_alive': True,
        }
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        gradient = QLinearGradient(0, 0, w, h)
        gradient.setColorAt(0, QColor(5, 5, 15))
        gradient.setColorAt(0.3, QColor(8, 8, 30))
        gradient.setColorAt(0.7, QColor(12, 12, 45))
        gradient.setColorAt(1, QColor(5, 5, 15))
        painter.fillRect(0, 0, w, h, gradient)
        
        for star in self.stars:
            x = int(star['x'] * w / 10000)
            y = int(star['y'] * h / 10000)
            size = max(1, int(star['size'] * w / 2000))
            opacity = int(star['opacity'] * star['brightness'])
            
            color = QColor(255, 255, 255, opacity)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x - size//2, y - size//2, size, size)
        
        for tail in self.comet_tails:
            self._draw_tail(painter, tail, w, h)
        
        for comet in self.comets:
            if len(comet['history']) > 1:
                self._draw_comet_tail(painter, comet, w, h)
            self._draw_comet_head(painter, comet, w, h)
    
    def _draw_tail(self, painter, tail, w, h):
        if len(tail['points']) < 2:
            return
        
        life_factor = min(1.0, tail['life'] / tail['max_life'])
        if life_factor >= 1.0:
            return
        
        points = []
        for hx, hy in tail['points']:
            px = int(hx * w / 10000)
            py = int(hy * h / 10000)
            points.append((px, py))
        
        max_alpha = int(200 * (1 - life_factor * 0.5))
        
        for i in range(len(points) - 1, 0, -1):
            progress = 1.0 - (i / len(points))
            progress = min(1.0, progress * 1.5)
            
            alpha = int(max_alpha * (1 - progress) * (1 - life_factor * 0.8))
            if alpha < 3:
                continue
            
            width = int(tail['size'] * (1 - progress * 0.85))
            if width < 1:
                continue
            
            x1, y1 = points[i - 1]
            x2, y2 = points[i]
            
            pen = QPen(QColor(150, 200, 255, alpha))
            pen.setWidth(max(1, width))
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(x1, y1, x2, y2)
    
    def _draw_comet_tail(self, painter, comet, w, h):
        points = []
        for hx, hy in comet['history']:
            px = int(hx * w / 10000)
            py = int(hy * h / 10000)
            points.append((px, py))
        
        life_factor = min(1.0, comet['life'] / comet['max_life'])
        max_alpha = int(200 * life_factor)
        
        for i in range(len(points) - 1, 0, -1):
            progress = 1.0 - (i / len(points))
            progress = min(1.0, progress * 1.5)
            
            alpha = int(max_alpha * (1 - progress))
            if alpha < 5:
                continue
            
            width = int(comet['size'] * (1 - progress * 0.85))
            if width < 1:
                continue
            
            x1, y1 = points[i - 1]
            x2, y2 = points[i]
            
            pen = QPen(QColor(150, 200, 255, alpha))
            pen.setWidth(max(1, width))
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(x1, y1, x2, y2)
    
    def _draw_comet_head(self, painter, comet, w, h):
        if not comet['is_alive'] or comet['life'] <= 0:
            return
        
        head_x = int(comet['x'] * w / 10000)
        head_y = int(comet['y'] * h / 10000)
        
        life_factor = min(1.0, comet['life'] / comet['max_life'])
        
        glow_alpha = int(120 * life_factor)
        glow = QColor(200, 230, 255, glow_alpha)
        painter.setBrush(glow)
        painter.setPen(Qt.NoPen)
        glow_size = comet['size'] * 4
        painter.drawEllipse(head_x - glow_size//2, head_y - glow_size//2, glow_size, glow_size)
        
        core_alpha = int(220 * life_factor)
        core = QColor(255, 255, 255, core_alpha)
        painter.setBrush(core)
        core_size = comet['size']
        painter.drawEllipse(head_x - core_size//2, head_y - core_size//2, core_size, core_size)
    
    def animate(self):
        w = self.width()
        h = self.height()
        if w == 0 or h == 0:
            return
        
        current_time = time.time()
        
        for star in self.stars:
            star['opacity'] = 0.3 + 0.7 * abs(
                math.sin(current_time * star['speed'] + star['phase'])
            )
        
        if not self.comets and current_time >= self.next_comet_time:
            self.comets.append(self._create_comet())
            self.next_comet_time = current_time + random.uniform(2.0, 3.0)
        
        for comet in self.comets[:]:
            comet['history'].append((comet['x'], comet['y']))
            
            if len(comet['history']) > 40:
                comet['history'].pop(0)
            
            comet['x'] += comet['dx']
            comet['y'] += comet['dy']
            comet['life'] += 0.1
            
            margin = 500
            if (comet['x'] > 10000 + margin or comet['x'] < -margin or
                comet['y'] > 10000 + margin or comet['y'] < -margin):
                
                if len(comet['history']) > 2:
                    tail = {
                        'points': list(comet['history']),
                        'size': comet['size'],
                        'life': 0,
                        'max_life': 2.0,
                    }
                    self.comet_tails.append(tail)
                
                self.comets.remove(comet)
        
        for tail in self.comet_tails[:]:
            tail['life'] += 0.05
            if tail['life'] >= tail['max_life']:
                self.comet_tails.remove(tail)
        
        self.update()


# ============================================
# ГЛАВНОЕ ОКНО
# ============================================

class MainView(QMainWindow):
    def __init__(self, username, network, database):
        super().__init__()
        self.username = username
        self.network = network
        self.database = database
        
        self.setWindowTitle(f"CyberLink - @{username}")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        self.drag_pos = None
        
        self.init_ui()
        self.load_contacts()
    
    def init_ui(self):
        self.space_widget = SpaceWidget(self)
        self.setCentralWidget(self.space_widget)
        
        glass = QFrame(self.space_widget)
        glass.setGeometry(15, 15, self.width() - 30, self.height() - 30)
        glass.setObjectName("glass_panel")
        glass.setStyleSheet(f"""
            QFrame#glass_panel {{
                background-color: rgba(10, 10, 25, 0.12);
                border: 1px solid rgba(79, 195, 247, 0.05);
                border-radius: 20px;
            }}
        """)
        
        layout = QVBoxLayout(glass)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        header = self._create_header(glass)
        layout.addWidget(header)
        
        nav = self._create_navigation()
        layout.addWidget(nav)
        
        content = self._create_content()
        layout.addWidget(content, stretch=1)
        
        self.glass_panel = glass
        self._add_control_buttons(glass)
    
    def _add_control_buttons(self, parent):
        btn_container = QFrame(parent)
        btn_container.setGeometry(parent.width() - 120, 10, 110, 35)
        btn_container.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(btn_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        buttons = [
            ("━", self.showMinimized),
            ("☐", self._toggle_maximize),
            ("✕", self.close),
        ]
        
        for text, callback in buttons:
            btn = QPushButton(text, btn_container)
            btn.setFixedSize(30, 30)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #8888aa;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.1);
                }
            """)
            if text == "✕":
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        color: #ff2d55;
                        border: none;
                        border-radius: 5px;
                        font-size: 16px;
                    }
                    QPushButton:hover {
                        background: #ff2d55;
                        color: white;
                    }
                """)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        self.btn_container = btn_container
    
    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def _create_header(self, parent):
        header = QFrame(parent)
        header.setFixedHeight(50)
        header.setStyleSheet("border-bottom: 1px solid rgba(79, 195, 247, 0.06);")
        header.setCursor(Qt.ArrowCursor)
        
        # ВСЯ область заголовка — для перетаскивания
        header.mousePressEvent = self.mousePressEvent
        header.mouseMoveEvent = self.mouseMoveEvent
        header.mouseReleaseEvent = self.mouseReleaseEvent
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 0, 10, 0)
        
        # Логотип — Karvx
        logo = QLabel("✦ CYBERLINK")
        logo.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #f5f5f5;
            font-family: 'Karvx', 'Arial', sans-serif;
        """)
        logo.setCursor(Qt.PointingHandCursor)
        # Логотип НЕ перетаскивает окно
        logo.mousePressEvent = lambda e: None
        logo.mouseMoveEvent = lambda e: None
        logo.mouseReleaseEvent = lambda e: None
        layout.addWidget(logo)
        
        layout.addStretch()
        
        return header
    
    def _create_navigation(self):
        nav = QFrame()
        nav.setFixedHeight(50)
        
        layout = QHBoxLayout(nav)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        nav_items = ["Чаты", "Профиль"]
        self.nav_buttons = []
        
        for i, name in enumerate(nav_items):
            btn = QPushButton(name)
            btn.setFixedHeight(36)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS['accent_primary'] if i == 0 else 'transparent'};
                    color: {'white' if i == 0 else COLORS['text_secondary']};
                    border: none;
                    border-radius: 10px;
                    padding: 8px 20px;
                    font-weight: {'bold' if i == 0 else 'normal'};
                    font-size: 14px;
                    font-family: 'TT Mussels', 'Arial', sans-serif;
                }}
                QPushButton:hover {{
                    background: {COLORS['accent_primary'] if i == 0 else 'rgba(255,255,255,0.05)'};
                }}
            """)
            btn.clicked.connect(lambda checked, idx=i: self.switch_page(idx))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        layout.addStretch()
        return nav
    
    def _create_content(self):
        content = QFrame()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 30, 20, 30)
        
        welcome = QLabel("🌌 Добро пожаловать в CyberLink!")
        welcome.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #f5f5f5;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        """)
        welcome.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome)
        
        subtitle = QLabel("Космический P2P мессенджер с полным шифрованием")
        subtitle.setStyleSheet("""
            font-size: 16px;
            color: #b0b0c0;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        info = QLabel("🚀 Скоро здесь будет полный функционал")
        info.setStyleSheet("""
            font-size: 14px;
            color: #6a6a7a;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        """)
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        layout.addStretch()
        return content
    
    def switch_page(self, index):
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {COLORS['accent_primary']};
                        color: white;
                        border: none;
                        border-radius: 10px;
                        padding: 8px 20px;
                        font-weight: bold;
                        font-size: 14px;
                        font-family: 'TT Mussels', 'Arial', sans-serif;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {COLORS['text_secondary']};
                        border: none;
                        border-radius: 10px;
                        padding: 8px 20px;
                        font-weight: normal;
                        font-size: 14px;
                        font-family: 'TT Mussels', 'Arial', sans-serif;
                    }}
                    QPushButton:hover {{
                        background: rgba(255,255,255,0.05);
                    }}
                """)
    
    def load_contacts(self):
        pass
    
    def mousePressEvent(self, event):
        # Разрешаем перетаскивание только если кликнули в верхние 80 пикселей
        if event.button() == Qt.LeftButton and event.y() <= 80:
            self.drag_pos = event.globalPos()
        else:
            self.drag_pos = None
    
    def mouseMoveEvent(self, event):
        if self.drag_pos is not None:
            delta = event.globalPos() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = event.globalPos()
    
    def mouseReleaseEvent(self, event):
        self.drag_pos = None
    
    def resizeEvent(self, event):
        if hasattr(self, 'glass_panel'):
            w = self.width() - 30
            h = self.height() - 30
            self.glass_panel.setGeometry(15, 15, w, h)
            
            if hasattr(self, 'btn_container'):
                self.btn_container.setGeometry(w - 120, 10, 110, 35)
        
        super().resizeEvent(event)