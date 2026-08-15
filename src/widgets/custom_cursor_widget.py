# src/widgets/custom_cursor_widget.py
# Кастомный курсор с прилипанием к элементам

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import math


class CustomCursorWidget(QWidget):
    """Кастомный курсор с прилипанием к элементам"""
    
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
        
        # Скорость вращения (градусов за кадр) - ОТРИЦАТЕЛЬНАЯ для вращения в другую сторону
        self.rotation_speed = -3.0
        
        # Начальные углы для каждого уголка (поворот вокруг своей оси)
        self.corner_start_angles = [180, -90, 0, 90]
        
        # ВСЕ УГЛЫ СВЕТЛО-ГОЛУБЫЕ
        light_blue = QColor(129, 212, 250)  # #81d4fa
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
        
        # Позиция курсора
        self.cursor_pos = QCursor.pos()
        
        # Таймер анимации (60 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)
        
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
        
        # Проверяем наведение
        self.check_hover()
        
        # Обновляем вращение
        if self.is_snapped:
            # При прилипании — плавно убираем вращение (к 0)
            self.target_angle = 0
            diff = self.target_angle - self.angle_offset
            self.angle_offset += diff * 0.15
        else:
            # Если не прилипли — вращаемся
            self.angle_offset += self.rotation_speed
        
        self.update()
    
    def check_hover(self):
        """Проверка наведения и прилипание"""
        widget = QApplication.widgetAt(self.cursor_pos)
        
        # Проверяем, является ли виджет целевым
        is_target = False
        
        if widget and widget != self:
            # 1. Проверяем специальные виджеты (поля ввода, кнопки, комбобоксы и т.д.)
            target_types = (
                QLineEdit,      # Поля ввода
                QTextEdit,      # Текстовые поля
                QPushButton,    # Кнопки
                QToolButton,    # Кнопки-инструменты
                QCommandLinkButton,  # Командные кнопки
                QDialogButtonBox,    # Блоки кнопок диалогов
                QCheckBox,      # Чекбоксы
                QRadioButton,   # Радиокнопки
                QComboBox,      # Выпадающие списки
                QSpinBox,       # Спинбоксы (числовые поля)
                QDoubleSpinBox, # Спинбоксы с плавающей точкой
                QSlider,        # Слайдеры
                QListWidget,    # Списки
                QListView,      # Списки (вид)
                QTreeView,      # Деревья
                QTableWidget,   # Таблицы
                QTabWidget,     # Вкладки
                QMenuBar,       # Меню
                QScrollBar,     # Скроллбары
                QDateEdit,      # Поля выбора даты
                QTimeEdit,      # Поля выбора времени
                QDateTimeEdit,  # Поля выбора даты и времени
                QTextBrowser,   # Браузер текста
                QPlainTextEdit, # Обычное текстовое поле
            )
            
            if isinstance(widget, target_types):
                is_target = True
            
            # 2. Проверяем QLabel с текстом "CYBERLINK"
            elif isinstance(widget, QLabel):
                text = widget.text()
                if "CYBERLINK" in text or "✦ CYBERLINK" in text:
                    is_target = True
                    print(f"🔍 Наведено на CYBERLINK: {text}")  # Для отладки
            
            # 3. Проверяем QGroupBox (группы с заголовками)
            elif isinstance(widget, QGroupBox):
                title = widget.title()
                if "CYBERLINK" in title:
                    is_target = True
            
            # 4. Проверяем QMenu (меню)
            elif isinstance(widget, QMenu):
                title = widget.title()
                if "CYBERLINK" in title:
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
            
            # Углы поворота для каждого уголка при прилипании
            self.snap_corner_angles = [
                0,   # левый-верхний (0°)
                90,  # правый-верхний (90°)
                -90, # левый-нижний (-90°)
                180, # правый-нижний (180°)
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
        
        # Радиус и размер углов
        if self.is_snapped:
            radius = self.radius + 6
            corner_size = self.corner_size + 4
            pen_width = 3
            dot_size = self.dot_size + 2
            glow_alpha = 60
        else:
            radius = self.radius
            corner_size = self.corner_size
            pen_width = 2
            dot_size = self.dot_size
            glow_alpha = 20
        
        # Сохраняем состояние и поворачиваем ВСЁ вокруг центра
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.angle_offset)
        painter.translate(-cx, -cy)
        
        # Свечение
        if self.is_snapped:
            glow_color = QColor(129, 212, 250, glow_alpha)
        else:
            glow_color = QColor(255, 255, 255, glow_alpha)
            
        gradient = QRadialGradient(cx, cy, 50)
        gradient.setColorAt(0, glow_color)
        gradient.setColorAt(1, Qt.transparent)
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - 50, cy - 50, 100, 100)
        
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
                
                # Обычный угол поворота
                rotate_angle = self.corner_start_angles[i]
            
            painter.save()
            painter.translate(center_x, center_y)
            painter.rotate(rotate_angle)
            
            color = self.corner_colors[i]
            
            if self.is_snapped:
                color = QColor(79, 195, 247)  # Ярко-голубой при прилипании
            
            painter.setPen(QPen(color, pen_width, Qt.SolidLine, Qt.RoundCap))
            painter.setBrush(Qt.NoBrush)
            
            half = corner_size // 2
            
            # Рисуем L-образный уголок
            painter.drawLine(-half, half, -half, -half)
            painter.drawLine(-half, -half, half, -half)
            
            # Свечение уголка
            if self.is_snapped:
                glow = QColor(79, 195, 247)
                glow.setAlpha(80)
            else:
                glow = QColor(color)
                glow.setAlpha(40)
                
            painter.setPen(QPen(glow, pen_width + 4, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(-half, half, -half, -half)
            painter.drawLine(-half, -half, half, -half)
            
            painter.restore()
        
        # Точка в центре
        if self.is_snapped:
            dot_color = QColor(79, 195, 247)
        else:
            dot_color = QColor(255, 255, 255)
        
        # Убираем свечение точки (оставляем только саму точку)
        painter.setBrush(dot_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - dot_size//2, cy - dot_size//2, dot_size, dot_size)
        
        # Маленький блик на точке
        painter.setBrush(QColor(255, 255, 255, 180))
        painter.drawEllipse(
            cx - dot_size//6,
            cy - dot_size//6,
            dot_size//3,
            dot_size//3
        )
        
        painter.restore()
    
    def stop(self):
        self.timer.stop()
        self.hide()
        self.deleteLater()