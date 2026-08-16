# src/utils/dialogs.py
# Диалоговые окна - исправленные стили для ComboBox

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


def get_dialog_style():
    """Возвращает стиль для диалоговых окон"""
    return """
        QDialog {
            background: #0d0d2b;
        }
        QLabel {
            color: #f5f5f5;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        }
        QPushButton {
            background: rgba(79, 195, 247, 0.12);
            color: #4fc3f7;
            border: none;
            border-radius: 6px;
            padding: 6px 16px;
            font-size: 13px;
            font-family: 'TT Mussels', 'Arial', sans-serif;
            font-weight: bold;
        }
        QPushButton:hover {
            background: rgba(79, 195, 247, 0.2);
        }
        QPushButton:default {
            background: rgba(79, 195, 247, 0.2);
        }
        QLineEdit {
            background: rgba(30, 30, 48, 0.6);
            color: #f5f5f5;
            border: 1px solid rgba(79, 195, 247, 0.15);
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        }
        QLineEdit:focus {
            border-color: rgba(79, 195, 247, 0.4);
        }
        QLineEdit::placeholder {
            color: rgba(255, 255, 255, 0.3);
        }
        QComboBox {
            background: rgba(30, 30, 48, 0.8);
            color: #f5f5f5;
            border: 1px solid rgba(79, 195, 247, 0.2);
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 14px;
            font-family: 'TT Mussels', 'Arial', sans-serif;
            min-width: 120px;
            min-height: 30px;
        }
        QComboBox:hover {
            border-color: rgba(79, 195, 247, 0.4);
        }
        QComboBox:focus {
            border-color: rgba(79, 195, 247, 0.5);
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
            background: transparent;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #8888aa;
            margin-right: 5px;
        }
        QComboBox QAbstractItemView {
            background: rgba(20, 20, 40, 0.95);
            color: #f5f5f5;
            border: 1px solid rgba(79, 195, 247, 0.2);
            border-radius: 8px;
            selection-background-color: rgba(79, 195, 247, 0.25);
            selection-color: #ffffff;
            outline: none;
            padding: 4px;
        }
        QComboBox QAbstractItemView::item {
            color: #f5f5f5;
            padding: 6px 12px;
            min-height: 25px;
            background: transparent;
        }
        QComboBox QAbstractItemView::item:hover {
            background: rgba(79, 195, 247, 0.15);
        }
        QComboBox QAbstractItemView::item:selected {
            background: rgba(79, 195, 247, 0.25);
            color: #ffffff;
        }
        QScrollArea {
            background: transparent;
            border: none;
        }
        QScrollBar:vertical {
            background: rgba(255, 255, 255, 0.03);
            width: 6px;
            border-radius: 3px;
        }
        QScrollBar::handle:vertical {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        QCheckBox {
            color: #f5f5f5;
            font-family: 'TT Mussels', 'Arial', sans-serif;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid rgba(79, 195, 247, 0.2);
            background: rgba(30, 30, 48, 0.4);
        }
        QCheckBox::indicator:checked {
            background: rgba(79, 195, 247, 0.3);
            border-color: rgba(79, 195, 247, 0.5);
        }
        QCheckBox::indicator:hover {
            border-color: rgba(79, 195, 247, 0.4);
        }
    """


def show_cyber_message(parent, title, message, icon=QMessageBox.Information):
    """Показать сообщение в стиле CyberLink"""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(icon)
    msg.setStyleSheet("""
        QMessageBox {
            background: #0d0d2b;
            color: #f5f5f5;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        }
        QMessageBox QLabel {
            color: #f5f5f5;
            font-size: 14px;
        }
        QMessageBox QPushButton {
            background: rgba(79, 195, 247, 0.12);
            color: #4fc3f7;
            border: none;
            border-radius: 6px;
            padding: 6px 16px;
            font-size: 13px;
            font-family: 'TT Mussels', 'Arial', sans-serif;
            font-weight: bold;
            min-width: 70px;
        }
        QMessageBox QPushButton:hover {
            background: rgba(79, 195, 247, 0.2);
        }
        QMessageBox QPushButton:default {
            background: rgba(79, 195, 247, 0.2);
        }
    """)
    return msg.exec_()


class CyberDialog(QDialog):
    """Диалог в стиле CyberLink - центр экрана + перетаскивание"""
    
    def __init__(self, parent, title, width=420, height=320, content_widget=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(width, height)
        
        # Для перетаскивания
        self.drag_pos = None
        
        self._content_widget = content_widget
        self._init_ui()
        self._center_on_screen()
    
    def _center_on_screen(self):
        """Центрирование диалога на экране"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        bg = QFrame()
        bg.setStyleSheet("""
            QFrame {
                background: #0d0d2b;
                border: 1px solid rgba(79, 195, 247, 0.06);
                border-radius: 12px;
            }
        """)
        bg_layout = QVBoxLayout(bg)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(0)
        
        # Заголовок (для перетаскивания)
        header = QFrame()
        header.setFixedHeight(40)
        header.setStyleSheet("border-bottom: 1px solid rgba(79, 195, 247, 0.06);")
        header.mousePressEvent = self.header_mouse_press
        header.mouseMoveEvent = self.header_mouse_move
        header.mouseReleaseEvent = self.header_mouse_release
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        title_label = QLabel(self.windowTitle())
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #f5f5f5;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #666688;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(255, 45, 85, 0.15);
                color: #ff2d55;
            }
        """)
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)
        
        bg_layout.addWidget(header)
        
        # Содержимое
        self.content_container = QWidget()
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(20, 20, 20, 10)
        content_layout.setSpacing(15)
        
        if self._content_widget:
            content_layout.addWidget(self._content_widget)
        else:
            content_layout.addStretch()
        
        bg_layout.addWidget(self.content_container)
        
        # Кнопки
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(15, 5, 15, 10)
        buttons_layout.setSpacing(10)
        
        buttons_layout.addStretch()
        
        ok_btn = QPushButton("✅ OK")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setStyleSheet("""
            QPushButton {
                background: rgba(79, 195, 247, 0.12);
                color: #4fc3f7;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 13px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(79, 195, 247, 0.2);
            }
        """)
        ok_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #8888aa;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 13px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.05);
                color: #f5f5f5;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        bg_layout.addWidget(buttons_widget)
        
        main_layout.addWidget(bg)
    
    def header_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos()
    
    def header_mouse_move(self, event):
        if self.drag_pos is not None:
            delta = event.globalPos() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = event.globalPos()
    
    def header_mouse_release(self, event):
        self.drag_pos = None
    
    def set_content(self, widget):
        """Установка содержимого диалога и ПРИМЕНЕНИЕ СТИЛЯ к ComboBox"""
        if hasattr(self, 'content_container'):
            old_layout = self.content_container.layout()
            if old_layout:
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        widget_to_delete = item.widget()
                        # Удаляем старый виджет
                        widget_to_delete.setParent(None)
                        widget_to_delete.deleteLater()
            else:
                old_layout = QVBoxLayout(self.content_container)
                old_layout.setContentsMargins(20, 20, 20, 10)
                old_layout.setSpacing(15)
            
            # Применяем стиль ко всем ComboBox внутри widget
            self._apply_combo_style(widget)
            
            old_layout.addWidget(widget)
            self._content_widget = widget
    
    def _apply_combo_style(self, widget):
        """Рекурсивно применяет стиль ко всем QComboBox внутри виджета"""
        # Если это QComboBox - применяем стиль напрямую
        if isinstance(widget, QComboBox):
            widget.setStyleSheet("""
                QComboBox {
                    background: rgba(30, 30, 48, 0.8);
                    color: #f5f5f5;
                    border: 1px solid rgba(79, 195, 247, 0.2);
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-size: 14px;
                    font-family: 'TT Mussels', 'Arial', sans-serif;
                    min-width: 120px;
                    min-height: 30px;
                }
                QComboBox:hover {
                    border-color: rgba(79, 195, 247, 0.4);
                }
                QComboBox:focus {
                    border-color: rgba(79, 195, 247, 0.5);
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                    background: transparent;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid #8888aa;
                    margin-right: 5px;
                }
                QComboBox QAbstractItemView {
                    background: rgba(20, 20, 40, 0.95);
                    color: #f5f5f5;
                    border: 1px solid rgba(79, 195, 247, 0.2);
                    border-radius: 8px;
                    selection-background-color: rgba(79, 195, 247, 0.25);
                    selection-color: #ffffff;
                    outline: none;
                    padding: 4px;
                }
                QComboBox QAbstractItemView::item {
                    color: #f5f5f5;
                    padding: 6px 12px;
                    min-height: 25px;
                    background: transparent;
                }
                QComboBox QAbstractItemView::item:hover {
                    background: rgba(79, 195, 247, 0.15);
                }
                QComboBox QAbstractItemView::item:selected {
                    background: rgba(79, 195, 247, 0.25);
                    color: #ffffff;
                }
            """)
            return
        
        # Если это контейнер - проходим по всем дочерним виджетам
        if isinstance(widget, QWidget):
            for child in widget.findChildren(QWidget):
                self._apply_combo_style(child)