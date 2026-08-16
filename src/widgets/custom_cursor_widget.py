# src/widgets/custom_cursor_widget.py
# Кастомный курсор с прилипанием и анимацией при наведении

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import math


class CustomCursorWidget(QWidget):
    """Кастомный курсор с прилипанием и анимацией при наведении"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        
        # Делаем виджет на весь экран
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        self.setGeometry(screen_rect)
        
        # Размеры курсора
        self.dot_size = 8
        self.corner_size = 14
        self.radius = 22
        self.angle_offset = 0
        self.target_angle_offset = 0
        
        # Скорость вращения (градусов за кадр)
        self.rotation_speed = 3.0
        
        # Начальные углы для каждого уголка (поворот вокруг своей оси)
        self.corner_start_angles = [180, -90, 0, 90]
        
        # ТЕКУЩИЕ углы уголков (для анимации наведения)
        self.current_corner_angles = [180, -90, 0, 90]
        self.target_corner_angles = [180, -90, 0, 90]
        
        # ВСЕ УГЛЫ СВЕТЛО-ГОЛУБЫЕ
        light_blue = QColor(129, 212, 250)
        self.corner_colors = [
            light_blue, light_blue, light_blue, light_blue
        ]
        
        # Базовые углы для позиции (45, 135, 225, 315) — это квадрат!
        self.base_angles = [45, 135, 225, 315]
        
        # Состояние прилипания
        self.is_snapped = False
        self.snap_target = None
        self.snap_rect = None
        self.snap_positions = None
        self.target_angle = 0
        self.snap_corner_angles = [0, 0, 0, 0]
        
        # Состояние наведения (для анимации)
        self.is_hovering = False
        self.hover_progress = 0.0  # 0.0 - 1.0
        
        # Позиция курсора
        self.cursor_pos = QCursor.pos()
        
        # Таймер анимации (60 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)
        
        self.show()
        
        self.setCursor(Qt.BlankCursor)
        QApplication.setOverrideCursor(Qt.BlankCursor)
    
    def normalize_angle(self, angle):
        """Нормализация угла в диапазон 0-90 градусов"""
        angle = angle % 90
        if angle < 0:
            angle += 90
        return angle
    
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
        
        # Проверяем наведение НА ИНТЕРАКТИВНЫЕ ЭЛЕМЕНТЫ
        self.check_hover()
        
        # Обновляем прогресс анимации наведения
        if self.is_hovering and not self.is_snapped:
            self.hover_progress = min(1.0, self.hover_progress + 0.04)
        else:
            self.hover_progress = max(0.0, self.hover_progress - 0.04)
        
        # Обновляем целевые углы для уголков (поворот на 180° при наведении)
        for i in range(4):
            if self.hover_progress > 0:
                self.target_corner_angles[i] = self.corner_start_angles[i] + 180
            else:
                self.target_corner_angles[i] = self.corner_start_angles[i]
        
        # Плавно поворачиваем уголки
        for i in range(4):
            ca = self.current_corner_angles[i]
            ta = self.target_corner_angles[i]
            diff = ta - ca
            if diff > 180:
                diff -= 360
            elif diff < -180:
                diff += 360
            self.current_corner_angles[i] += diff * 0.15
        
        # Проверяем прилипание
        self.check_snap()
        
        # Обновляем вращение
        if self.is_snapped:
            # При прилипании — плавно убираем вращение (к 0)
            self.target_angle = 0
            diff = self.target_angle - self.angle_offset
            self.angle_offset += diff * 0.15
        else:
            # Если не прилипли — вращаемся
            self.angle_offset += self.rotation_speed
        
        # НОРМАЛИЗУЕМ УГОЛ В ДИАПАЗОНЕ 0-90
        self.angle_offset = self.normalize_angle(self.angle_offset)
        
        self.update()
    
    def check_hover(self):
        """Проверка наведения на интерактивные элементы (для анимации)"""
        widget = QApplication.widgetAt(self.cursor_pos)
        
        is_interactive = False
        if widget and widget != self:
            # Интерактивные типы виджетов
            interactive_types = (
                QPushButton, QToolButton, QCommandLinkButton,
                QLineEdit, QTextEdit, QPlainTextEdit,
                QComboBox, QSpinBox, QDoubleSpinBox,
                QCheckBox, QRadioButton,
                QListWidget, QListView, QTreeView, QTableWidget,
                QTabWidget, QSlider, QScrollBar,
                QDateEdit, QTimeEdit, QDateTimeEdit,
                QMenu, QMenuBar, QDialogButtonBox
            )
            is_interactive = isinstance(widget, interactive_types)
            
            # Проверяем также QLabel с CYBERLINK
            if not is_interactive and isinstance(widget, QLabel):
                if "CYBERLINK" in widget.text() or "✦ CYBERLINK" in widget.text():
                    is_interactive = True
        
        self.is_hovering = is_interactive
    
    def check_snap(self):
        """Проверка прилипания к целевым элементам"""
        widget = QApplication.widgetAt(self.cursor_pos)
        
        # Проверяем, является ли виджет целевым для прилипания
        is_target = False
        if widget and widget != self:
            # Целевые типы: поля ввода (QLineEdit, QTextEdit) и QLabel с текстом "CYBERLINK"
            target_types = (QLineEdit, QTextEdit)
            
            if isinstance(widget, target_types):
                is_target = True
            elif isinstance(widget, QLabel):
                if widget.text() == "✦ CYBERLINK" or "CYBERLINK" in widget.text():
                    is_target = True
        
        if is_target and widget != self.snap_target:
            # Новый элемент для прилипания
            self.snap_target = widget
            self.snap_rect = widget.geometry()
            self.is_snapped = True
            
            # Вычисляем позиции уголков на элементе (глобальные координаты)
            global_pos = widget.mapToGlobal(QPoint(0, 0))
            rect = widget.geometry()
            
            self.snap_positions = [
                (global_pos.x(), global_pos.y()),  # левый-верхний
                (global_pos.x() + rect.width(), global_pos.y()),  # правый-верхний
                (global_pos.x(), global_pos.y() + rect.height()),  # левый-нижний
                (global_pos.x() + rect.width(), global_pos.y() + rect.height()),  # правый-нижний
            ]
            
            # Углы поворота при прилипании
            self.snap_corner_angles = [
                0,   # левый-верхний
                90,  # правый-верхний
                -90, # левый-нижний
                180, # правый-нижний
            ]
            
        elif not is_target and self.is_snapped:
            # Уходим с элемента — возвращаемся в обычный режим
            self.is_snapped = False
            self.snap_target = None
            self.snap_rect = None
            self.snap_positions = None
    
    def paintEvent(self, event):
        """Рисование курсора"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Центр экрана (где курсор)
        cx = self.cursor_pos.x()
        cy = self.cursor_pos.y()
        
        # Используем ease-in-out для плавности
        progress = self.hover_progress * self.hover_progress * (3.0 - 2.0 * self.hover_progress)
        
        # Радиус и размер углов (уменьшаются при наведении)
        if self.is_snapped:
            radius = self.radius + 6
            corner_size = self.corner_size + 4
            pen_width = 3
            dot_size = self.dot_size + 2
            glow_alpha = 60
        else:
            # При наведении радиус уменьшается
            radius = self.radius - progress * 8
            radius = max(radius, 8)
            corner_size = self.corner_size + 4 * progress
            pen_width = 2 + progress
            dot_size = self.dot_size + 2 * progress
            glow_alpha = 20 + 40 * progress
        
        # Сохраняем состояние и поворачиваем ВСЁ вокруг центра
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.angle_offset)
        painter.translate(-cx, -cy)
        
        # Свечение
        glow_color = QColor(255, 255, 255, int(glow_alpha))
        glow_size = 50 + 20 * progress
        gradient = QRadialGradient(cx, cy, glow_size)
        gradient.setColorAt(0, glow_color)
        gradient.setColorAt(1, Qt.transparent)
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(cx - glow_size), int(cy - glow_size), int(glow_size * 2), int(glow_size * 2))
        
        # 4 угла
        for i in range(4):
            # Если прилипли — позиции уголков совпадают с углами элемента
            if self.is_snapped and self.snap_positions:
                # Координаты угла элемента
                center_x = self.snap_positions[i][0]
                center_y = self.snap_positions[i][1]
                
                # Угол поворота для прилипания
                rotate_angle = self.snap_corner_angles[i]
            else:
                # Обычная позиция на окружности
                rad = math.radians(self.base_angles[i])
                center_x = cx + radius * math.cos(rad)
                center_y = cy + radius * math.sin(rad)
                
                # Используем ТЕКУЩИЙ угол поворота (с анимацией наведения)
                rotate_angle = self.current_corner_angles[i]
            
            painter.save()
            painter.translate(center_x, center_y)
            painter.rotate(rotate_angle)
            
            color = self.corner_colors[i]
            
            if self.is_snapped:
                # При прилипании делаем ярче
                color = color.lighter(150)
            elif self.hover_progress > 0:
                # При наведении делаем ярче
                r = min(255, int(color.red() + 50 * progress))
                g = min(255, int(color.green() + 50 * progress))
                b = min(255, int(color.blue() + 50 * progress))
                color = QColor(r, g, b)
            
            painter.setPen(QPen(color, int(pen_width), Qt.SolidLine, Qt.RoundCap))
            painter.setBrush(Qt.NoBrush)
            
            half = int(corner_size // 2)
            
            # Рисуем L-образный уголок
            painter.drawLine(-half, half, -half, -half)
            painter.drawLine(-half, -half, half, -half)
            
            # Свечение уголка
            glow = QColor(color)
            glow_alpha_glow = int(40 + 40 * progress)
            glow.setAlpha(glow_alpha_glow)
            painter.setPen(QPen(glow, int(pen_width + 4), Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(-half, half, -half, -half)
            painter.drawLine(-half, -half, half, -half)
            
            painter.restore()
        
        # Точка в центре
        if self.is_snapped:
            dot_color = QColor(79, 195, 247)
        elif self.hover_progress > 0:
            dot_color = QColor(79, 195, 247)
        else:
            dot_color = QColor(255, 255, 255)
        
        dot_size_int = int(dot_size)
        
        # Убираем свечение точки
        painter.setBrush(dot_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - dot_size_int//2, cy - dot_size_int//2, dot_size_int, dot_size_int)
        
        # Блик на точке
        painter.setBrush(QColor(255, 255, 255, 180))
        painter.drawEllipse(
            cx - dot_size_int//6,
            cy - dot_size_int//6,
            dot_size_int//3,
            dot_size_int//3
        )
        
        painter.restore()
    
    def stop(self):
        self.timer.stop()
        self.hide()
        self.deleteLater()