# src/views/main_view.py
# Главное окно с навигацией, чатами, друзьями, профилем и настройками

import random
import math
import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.theme.colors import COLORS
from src.views.chat_view import ChatView
from src.views.friends_view import FriendsView
from src.views.profile_view import ProfileView
from src.views.settings_view import SettingsView


class SpaceWidget(QWidget):
    """Космический фон с анимированными звёздами и кометами"""
    
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
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
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


class MainView(QMainWindow):
    def __init__(self, username, password=None, network=None, friends_manager=None, storage=None):
        super().__init__()
        self.username = username
        self.password = password
        self.network = network
        self.friends_manager = friends_manager
        self.storage = storage
        self.current_mode = 'chats'
        self.drag_pos = None
        self.chat_padding = 30
        self.cursor_widget = None
        
        self.setWindowTitle(f"CyberLink - {username}")
        self.setGeometry(100, 100, 1300, 800)
        self.setMinimumSize(1000, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        self.init_ui()
    
    def set_cursor_widget(self, cursor):
        self.cursor_widget = cursor
    
    def init_ui(self):
        # Космический фон
        self.space_widget = SpaceWidget(self)
        self.setCentralWidget(self.space_widget)
        
        # Стеклянная панель
        glass = QFrame(self.space_widget)
        glass.setGeometry(10, 10, self.width() - 20, self.height() - 20)
        glass.setObjectName("glass_panel")
        glass.setStyleSheet("""
            QFrame#glass_panel {
                background-color: rgba(10, 10, 25, 0.12);
                border: 1px solid rgba(79, 195, 247, 0.05);
                border-radius: 16px;
            }
        """)
        
        # Основной layout для стеклянной панели
        main_layout = QVBoxLayout(glass)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # === 1. ВЕРХНЯЯ ПАНЕЛЬ ===
        top_bar = self._create_top_bar(glass)
        main_layout.addWidget(top_bar)
        
        # === 2. НАВИГАЦИЯ ===
        nav_bar = self._create_nav_bar()
        main_layout.addWidget(nav_bar)
        
        # === 3. ОСНОВНАЯ ОБЛАСТЬ ===
        content_split = QSplitter(Qt.Horizontal)
        content_split.setHandleWidth(0)
        content_split.setStyleSheet("QSplitter::handle { background: transparent; }")
        
        # Левая панель (список чатов)
        self.chat_panel = QFrame()
        self.chat_panel.setFixedWidth(400)
        self.chat_panel.setStyleSheet("border-right: 1px solid rgba(79, 195, 247, 0.06);")
        self.chat_panel_layout = QVBoxLayout(self.chat_panel)
        self.chat_panel_layout.setContentsMargins(12, 12, 12, 12)
        self.chat_panel_layout.setSpacing(10)
        
        # Поиск
        search = QLineEdit()
        search.setPlaceholderText("🔍 Поиск...")
        search.setStyleSheet("""
            QLineEdit {
                background: rgba(30, 30, 48, 0.5);
                color: #f5f5f5;
                border: 1px solid rgba(79, 195, 247, 0.08);
                border-radius: 12px;
                padding: 10px 14px;
                font-size: 14px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
            }
            QLineEdit:focus {
                border-color: rgba(79, 195, 247, 0.3);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.25);
            }
        """)
        self.chat_panel_layout.addWidget(search)
        
        # Список чатов
        self.chat_list = QListWidget()
        self.chat_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
                font-family: 'TT Mussels', 'Arial', sans-serif;
            }
            QListWidget::item {
                padding: 4px 8px;
                border-radius: 8px;
                margin: 1px 0;
                min-height: 30px;
            }
            QListWidget::item:hover {
                background: rgba(255, 255, 255, 0.04);
            }
            QListWidget::item:selected {
                background: rgba(79, 195, 247, 0.08);
            }
        """)
        self.chat_panel_layout.addWidget(self.chat_list)
        
        content_split.addWidget(self.chat_panel)
        
        # Правая панель (рабочая зона)
        self.work_area = QStackedWidget()
        content_split.addWidget(self.work_area)
        
        # === СОЗДАЁМ СТРАНИЦЫ ===
        
        # 1. Чаты
        self.chat_page = ChatView(self.username)
        if hasattr(self.chat_page, 'set_managers'):
            self.chat_page.set_managers(self.friends_manager, self.network)
        
        # 2. Друзья
        self.friends_page = FriendsView(
            self.username,
            self.friends_manager,
            self.network
        )
        
        # 3. Профиль - передаём пароль
        self.profile_page = ProfileView(
            self.username,
            self.friends_manager,
            self.network,
            self.password
        )
        
        # 4. Настройки - передаём пароль
        self.settings_page = SettingsView(
            self.username,
            self,
            self.friends_manager,
            self.network,
            self.password
        )
        
        # Добавляем страницы в рабочую область
        self.work_area.addWidget(self.chat_page)
        self.work_area.addWidget(self.friends_page)
        self.work_area.addWidget(self.profile_page)
        self.work_area.addWidget(self.settings_page)
        
        # По умолчанию показываем чаты
        self.work_area.setCurrentIndex(0)
        
        # Устанавливаем соотношение размеров
        content_split.setSizes([400, self.width() - 400])
        
        main_layout.addWidget(content_split, stretch=1)
        
        # === 4. НИЖНЯЯ ПАНЕЛЬ ===
        status_bar = self._create_status_bar()
        main_layout.addWidget(status_bar)
        
        self.glass_panel = glass
        self.content_split = content_split
        
        # Заполняем чаты
        self.update_chat_list()
    
    def update_chat_list(self):
        """Обновление списка чатов"""
        self.chat_list.clear()
        
        # Если есть friends_manager - показываем друзей
        if self.friends_manager:
            friends = self.friends_manager.get_friends_list()
            if friends:
                for friend in friends:
                    friend_id = friend.get('id')
                    display_name = friend.get('display_name', friend_id)
                    is_online = self.friends_manager.is_online(friend_id)
                    
                    item = QListWidgetItem()
                    widget = QWidget()
                    layout = QHBoxLayout(widget)
                    layout.setContentsMargins(8, 4, 8, 4)
                    
                    status = "🟢" if is_online else "⚪"
                    name = QLabel(f"{status} {display_name}")
                    name.setStyleSheet(f"""
                        color: {'#00ff88' if is_online else '#8888aa'};
                        font-size: 14px;
                        font-family: 'TT Mussels', 'Arial', sans-serif;
                    """)
                    layout.addWidget(name)
                    layout.addStretch()
                    
                    item.setSizeHint(widget.sizeHint())
                    item.setData(Qt.UserRole, friend_id)
                    self.chat_list.addItem(item)
                    self.chat_list.setItemWidget(item, widget)
                
                self.chat_list.itemClicked.connect(self.on_chat_selected)
                return
        
        # Если нет друзей - показываем пустое состояние
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        
        empty_icon = QLabel("💬")
        empty_icon.setStyleSheet("font-size: 48px; color: #8888aa;")
        empty_icon.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_icon)
        
        empty_text = QLabel("Нет активных чатов")
        empty_text.setStyleSheet("""
            color: #8888aa;
            font-size: 16px;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        """)
        empty_text.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_text)
        
        empty_sub = QLabel("Добавьте друзей, чтобы начать общение")
        empty_sub.setStyleSheet("""
            color: #666688;
            font-size: 13px;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        """)
        empty_sub.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_sub)
        
        item = QListWidgetItem()
        item.setSizeHint(empty_widget.sizeHint())
        self.chat_list.addItem(item)
        self.chat_list.setItemWidget(item, empty_widget)
    
    def on_chat_selected(self, item):
        """Обработка выбора чата"""
        friend_id = item.data(Qt.UserRole)
        if friend_id and hasattr(self, 'chat_page'):
            self.switch_mode('chats')
            self.chat_page.open_chat(friend_id)
    
    def _create_top_bar(self, parent):
        bar = QFrame(parent)
        bar.setFixedHeight(50)
        bar.setStyleSheet("border-bottom: 1px solid rgba(79, 195, 247, 0.06);")
        bar.mousePressEvent = self.mousePressEvent
        bar.mouseMoveEvent = self.mouseMoveEvent
        bar.mouseReleaseEvent = self.mouseReleaseEvent
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 12, 0)
        
        logo = QLabel("✦ CYBERLINK")
        logo.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #f5f5f5;
            font-family: 'Karvx', 'Arial', sans-serif;
        """)
        logo.setCursor(Qt.PointingHandCursor)
        logo.mousePressEvent = lambda e: None
        layout.addWidget(logo)
        
        layout.addStretch()
        
        # Кнопки управления
        buttons = [
            ("━", self.showMinimized),
            ("☐", self._toggle_maximize),
            ("✕", self.close),
        ]
        
        for text, callback in buttons:
            btn = QPushButton(text, bar)
            btn.setFixedSize(28, 28)
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
                    background: rgba(255, 255, 255, 0.08);
                }
            """)
            if text == "✕":
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        color: #8888aa;
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
        
        return bar
    
    def _create_nav_bar(self):
        nav = QFrame()
        nav.setFixedHeight(40)
        nav.setStyleSheet("border-bottom: 1px solid rgba(79, 195, 247, 0.06);")
        
        layout = QHBoxLayout(nav)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(4)
        
        nav_items = [
            {"icon": "💬", "label": "Чаты", "key": "chats"},
            {"icon": "🤝", "label": "Друзья", "key": "friends"},
            {"icon": "👤", "label": "Профиль", "key": "profile"},
            {"icon": "⚙️", "label": "Настройки", "key": "settings"},
        ]
        
        self.nav_buttons = []
        
        for item in nav_items:
            btn = QPushButton(f"{item['icon']} {item['label']}")
            btn.setFixedHeight(30)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("key", item["key"])
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #b0b0c0;
                    border: none;
                    border-radius: 8px;
                    padding: 4px 14px;
                    font-size: 13px;
                    font-family: 'TT Mussels', 'Arial', sans-serif;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.05);
                }
            """)
            btn.clicked.connect(lambda checked, k=item["key"]: self.switch_mode(k))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        if self.nav_buttons:
            self.nav_buttons[0].setStyleSheet("""
                QPushButton {
                    background: rgba(79, 195, 247, 0.12);
                    color: #f5f5f5;
                    border: none;
                    border-radius: 8px;
                    padding: 4px 14px;
                    font-size: 13px;
                    font-family: 'TT Mussels', 'Arial', sans-serif;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgba(79, 195, 247, 0.18);
                }
            """)
        
        layout.addStretch()
        return nav
    
    def _create_status_bar(self):
        bar = QFrame()
        bar.setFixedHeight(30)
        bar.setStyleSheet("border-top: 1px solid rgba(79, 195, 247, 0.06);")
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 12, 0)
        
        self.status_label = QLabel("🟢 Онлайн")
        self.status_label.setStyleSheet("color: #4fc3f7; font-size: 12px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        user = QLabel(f"🌟 {self.username}")
        user.setStyleSheet("color: #b0b0c0; font-size: 12px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        layout.addWidget(user)
        
        layout.addStretch()
        
        unread = QLabel("0 💫 непрочитанных")
        unread.setStyleSheet("color: #8888aa; font-size: 12px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        layout.addWidget(unread)
        
        layout.addStretch()
        
        p2p = QLabel("🌐 P2P")
        p2p.setStyleSheet("color: #4fc3f7; font-size: 12px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        layout.addWidget(p2p)
        
        return bar
    
    def switch_mode(self, mode):
        """Переключение между режимами"""
        self.current_mode = mode
        
        for btn in self.nav_buttons:
            key = btn.property("key")
            if key == mode:
                btn.setStyleSheet("""
                    QPushButton {
                        background: rgba(79, 195, 247, 0.12);
                        color: #f5f5f5;
                        border: none;
                        border-radius: 8px;
                        padding: 4px 14px;
                        font-size: 13px;
                        font-family: 'TT Mussels', 'Arial', sans-serif;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background: rgba(79, 195, 247, 0.18);
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        color: #b0b0c0;
                        border: none;
                        border-radius: 8px;
                        padding: 4px 14px;
                        font-size: 13px;
                        font-family: 'TT Mussels', 'Arial', sans-serif;
                    }
                    QPushButton:hover {
                        background: rgba(255, 255, 255, 0.05);
                    }
                """)
        
        if mode == "chats":
            self.work_area.setCurrentIndex(0)
        elif mode == "friends":
            self.work_area.setCurrentIndex(1)
        elif mode == "profile":
            self.work_area.setCurrentIndex(2)
        elif mode == "settings":
            self.work_area.setCurrentIndex(3)
    
    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def mousePressEvent(self, event):
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
            self.glass_panel.setGeometry(10, 10, self.width() - 20, self.height() - 20)
        super().resizeEvent(event)