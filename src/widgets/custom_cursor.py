# src/widgets/custom_cursor_widget.py
# Кастомный курсор — квадрат из 4 углов с разными начальными углами

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import math


class CustomCursorWidget(QWidget):
    """Кастомный курсор — квадрат из 4 углов"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        
        # Размеры курсора
        self.dot_size = 8
        self.corner_size = 14
        self.radius = 22
        self.angle_offset = 0
        self.axis_angle_offset = 0
        
        # Скорость вращения (градусов за кадр)
        self.rotation_speed = 0.5
        
        # Начальные углы для каждого уголка (поворот вокруг своей оси)
        # Красный: 180°, Жёлтый: -90°, Зелёный: 0°, Синий: 90°
        self.corner_start_angles = [180, -90, 0, 90]
        
        # Цвета углов
        self.corner_colors = [
            QColor(255, 45, 85),    # Красный - верхний-левый (индекс 0)
            QColor(255, 220, 45),   # Жёлтый - верхний-правый (индекс 1)
            QColor(0, 255, 136),    # Зелёный - нижний-левый (индекс 2)
            QColor(79, 195, 247),   # Синий - нижний-правый (индекс 3)
        ]
        
        # Базовые углы для позиции (45, 135, 225, 315)
        self.base_angles = [45, 135, 225, 315]
        
        # Позиция
        self.cursor_pos = QCursor.pos()
        
        # Состояние наведения
        self.is_hovering = False
        
        # Таймер анимации (60 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)
        
        # Размер окна
        self.resize(200, 200)
        self.move(self.cursor_pos.x() - 100, self.cursor_pos.y() - 100)
        self.show()
        
        self.setCursor(Qt.BlankCursor)
        QApplication.setOverrideCursor(Qt.BlankCursor)
    
    def set_rotation_speed(self, speed):
        """Установка скорости вращения"""
        self.rotation_speed = speed
    
    def animate(self):
        """Анимация курсора (60 FPS)"""
        current_pos = QCursor.pos()
        
        # Плавное следование за мышью
        dx = current_pos.x() - self.cursor_pos.x()
        dy = current_pos.y() - self.cursor_pos.y()
        self.cursor_pos.setX(int(self.cursor_pos.x() + dx * 0.5))
        self.cursor_pos.setY(int(self.cursor_pos.y() + dy * 0.5))
        
        # Вращение
        self.angle_offset += self.rotation_speed
        self.axis_angle_offset += self.rotation_speed  # Синхронно!
        
        # Перемещаем виджет
        x = self.cursor_pos.x() - self.width() // 2
        y = self.cursor_pos.y() - self.height() // 2
        self.move(x, y)
        
        self.check_hover()
        self.update()
    
    def check_hover(self):
        """Проверка наведения"""
        widget = QApplication.widgetAt(self.cursor_pos)
        if widget and widget != self:
            interactive_types = (QPushButton, QLineEdit, QTextEdit, QListWidget,
                                QComboBox, QCheckBox, QRadioButton, QSpinBox,
                                QSlider, QTabWidget, QToolButton, QMenuBar,
                                QScrollBar, QListView, QTreeView, QTableWidget,
                                QDialog, QMainWindow)
            self.is_hovering = isinstance(widget, interactive_types)
        else:
            self.is_hovering = False
    
    def paintEvent(self, event):
        """Рисование курсора"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        cx = self.width() // 2
        cy = self.height() // 2
        
        # Радиус и размер углов
        if self.is_hovering:
            radius = self.radius + 4
            corner_size = self.corner_size + 2
            pen_width = 3
        else:
            radius = self.radius
            corner_size = self.corner_size
            pen_width = 2
        
        # Свечение
        glow_color = QColor(255, 255, 255, 20)
        gradient = QRadialGradient(cx, cy, 50)
        gradient.setColorAt(0, glow_color)
        gradient.setColorAt(1, Qt.transparent)
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - 50, cy - 50, 100, 100)
        
        # 4 угла квадрата
        # Углы квадрата: 45°, 135°, 225°, 315° от центра
        angles = [45, 135, 225, 315]
        angle_step = self.angle_offset
        
        for i, angle in enumerate(angles):
            # Позиция уголка на квадрате (вращается вокруг центра)
            rad = math.radians(angle + angle_step)
            
            # Координаты центра уголка
            center_x = cx + radius * math.cos(rad)
            center_y = cy + radius * math.sin(rad)
            
            painter.save()
            
            # Перемещаемся в центр уголка
            painter.translate(center_x, center_y)
            
            # Вращаем уголок вокруг своей оси
            # Начальный угол + синхронное вращение
            rotation = self.corner_start_angles[i] + angle_step
            painter.rotate(math.degrees(rotation))
            
            color = self.corner_colors[i]
            painter.setPen(QPen(color, pen_width, Qt.SolidLine, Qt.RoundCap))
            painter.setBrush(Qt.NoBrush)
            
            half = corner_size // 2
            
            # Рисуем L-образный уголок относительно его центра
            painter.drawLine(-half, half, -half, -half)
            painter.drawLine(-half, -half, half, -half)
            
            # Свечение уголка
            glow = QColor(color)
            glow.setAlpha(30)
            painter.setPen(QPen(glow, pen_width + 4, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(-half, half, -half, -half)
            painter.drawLine(-half, -half, half, -half)
            
            painter.restore()
        
        # Точка в центре
        dot_size = self.dot_size + (2 if self.is_hovering else 0)
        
        dot_glow = QRadialGradient(cx, cy, dot_size * 4)
        dot_glow.setColorAt(0, QColor(255, 255, 255, 50))
        dot_glow.setColorAt(1, Qt.transparent)
        painter.setBrush(dot_glow)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - dot_size * 4, cy - dot_size * 4, dot_size * 8, dot_size * 8)
        
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(cx - dot_size//2, cy - dot_size//2, dot_size, dot_size)
        
        painter.setBrush(QColor(255, 255, 255, 180))
        painter.drawEllipse(
            cx - dot_size//6,
            cy - dot_size//6,
            dot_size//3,
            dot_size//3
        )
    
    def stop(self):
        self.timer.stop()
        self.hide()
        self.deleteLater()