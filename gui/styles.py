# gui/styles.py
# CyberLink - Стили киберпанк (исправленная версия)

import sys

# ============================================
# БАЗОВЫЕ НАСТРОЙКИ
# ============================================

# Список шрифтов для проверки (без QFontDatabase)
FONT_FAMILIES = ['Segoe UI', 'Inter', 'Roboto', 'San Francisco', 'Arial', 'sans-serif']
MONO_FONT_FAMILIES = ['Consolas', 'JetBrains Mono', 'Fira Code', 'Courier New', 'monospace']

# ============================================
# ОСНОВНЫЕ ЦВЕТА
# ============================================

COLORS = {
    'neon_pink': '#ff2d55',
    'neon_blue': '#00d4ff',
    'neon_purple': '#7b2ffc',
    'neon_green': '#00ff88',
    'neon_yellow': '#ffdd00',
    'dark_bg': '#0a0a1a',
    'dark_card': '#12122a',
    'dark_input': '#1a1a3a',
    'text_primary': '#e0e0ff',
    'text_secondary': '#8888aa',
    'text_dark': '#666688',
}

# ============================================
# БАННЕР
# ============================================

CYBERLINK_ASCII = r"""
   ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██╗     ██╗███╗   ██╗██╗  ██╗
  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██║     ██║████╗  ██║██║ ██╔╝
  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██║     ██║██╔██╗ ██║█████╔╝ 
  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██║     ██║██║╚██╗██║██╔═██╗ 
  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║███████╗██║██║ ╚████║██║  ██╗
   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
"""

# ============================================
# СТИЛЬ ДЛЯ КНОПОК (без transform, transition, box-shadow)
# ============================================

BUTTON_STYLE = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS['neon_pink']}, 
            stop:0.5 {COLORS['neon_purple']},
            stop:1 {COLORS['neon_blue']});
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        font-size: 13px;
        font-weight: bold;
        min-height: 34px;
        min-width: 80px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #ff4d7a, 
            stop:0.5 #8b4ffc,
            stop:1 #4dd4ff);
    }}
    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #cc1a44, 
            stop:0.5 #5a1fcc,
            stop:1 #0099cc);
    }}
    QPushButton:disabled {{
        background: #333355;
        color: #666688;
    }}
"""

# ============================================
# СТИЛЬ ДЛЯ ДИАЛОГОВ
# ============================================

DIALOG_STYLE = f"""
    QDialog {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #0a0a1a, 
            stop:0.5 #0a0a2a,
            stop:1 #0a0a1a);
    }}
    QDialog QLabel {{
        color: #e0e0ff;
        font-size: 13px;
    }}
    QDialog QLineEdit {{
        background-color: #1a1a3a;
        color: #e0e0ff;
        border: 2px solid #00d4ff;
        border-radius: 10px;
        padding: 10px 15px;
        font-size: 14px;
    }}
    QDialog QLineEdit:focus {{
        border-color: #ff2d55;
        background-color: #1a1a4a;
    }}
    {BUTTON_STYLE}
"""

# ============================================
# СТИЛЬ ДЛЯ MESSAGEBOX
# ============================================

MESSAGEBOX_STYLE = f"""
    QMessageBox {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #0a0a1a, 
            stop:0.5 #0a0a2a,
            stop:1 #0a0a1a);
    }}
    QMessageBox QLabel {{
        color: #e0e0ff;
        font-size: 13px;
    }}
    {BUTTON_STYLE}
"""

# ============================================
# СТИЛЬ ДЛЯ INPUTDIALOG
# ============================================

INPUTDIALOG_STYLE = f"""
    QInputDialog {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #0a0a1a, 
            stop:0.5 #0a0a2a,
            stop:1 #0a0a1a);
    }}
    QInputDialog QLabel {{
        color: #e0e0ff;
        font-size: 13px;
    }}
    QInputDialog QLineEdit {{
        background-color: #1a1a3a;
        color: #e0e0ff;
        border: 2px solid #00d4ff;
        border-radius: 10px;
        padding: 10px 15px;
        font-size: 14px;
    }}
    QInputDialog QLineEdit:focus {{
        border-color: #ff2d55;
        background-color: #1a1a4a;
    }}
    {BUTTON_STYLE}
"""

# ============================================
# СТИЛЬ ДЛЯ ГЛАВНОГО ОКНА
# ============================================

MAIN_STYLE = f"""
    QMainWindow {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {COLORS['dark_bg']}, 
            stop:0.5 #0a0a2a,
            stop:1 {COLORS['dark_bg']});
    }}
    
    QMenuBar {{
        background-color: {COLORS['dark_bg']};
        color: {COLORS['text_primary']};
        border-bottom: 2px solid {COLORS['neon_blue']};
        padding: 5px 10px;
    }}
    QMenuBar::item {{
        padding: 8px 15px;
        border-radius: 8px;
        font-size: 13px;
    }}
    QMenuBar::item:selected {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS['neon_pink']}, 
            stop:1 {COLORS['neon_purple']});
        color: white;
    }}
    
    QMenu {{
        background-color: {COLORS['dark_card']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['neon_blue']};
        border-radius: 10px;
        padding: 8px;
    }}
    QMenu::item {{
        padding: 8px 30px;
        border-radius: 6px;
        font-size: 13px;
    }}
    QMenu::item:selected {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS['neon_pink']}, 
            stop:1 {COLORS['neon_purple']});
        color: white;
    }}
    
    QStatusBar {{
        background-color: {COLORS['dark_bg']};
        color: {COLORS['neon_green']};
        border-top: 1px solid {COLORS['neon_blue']};
        padding: 5px;
        font-size: 12px;
    }}
    
    QListWidget {{
        background-color: {COLORS['dark_card']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['neon_blue']};
        border-radius: 12px;
        padding: 8px;
        outline: none;
    }}
    QListWidget::item {{
        padding: 12px 16px;
        border-radius: 8px;
        margin: 2px 0;
    }}
    QListWidget::item:hover {{
        background-color: #1a1a4a;
    }}
    QListWidget::item:selected {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS['neon_pink']}, 
            stop:1 {COLORS['neon_purple']});
        color: white;
    }}
    
    QTextEdit {{
        background-color: {COLORS['dark_card']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['neon_blue']};
        border-radius: 12px;
        padding: 15px;
        font-size: 14px;
    }}
    QTextEdit:focus {{
        border-color: {COLORS['neon_pink']};
    }}
    
    QLineEdit {{
        background-color: {COLORS['dark_input']};
        color: {COLORS['text_primary']};
        border: 2px solid {COLORS['neon_blue']};
        border-radius: 12px;
        padding: 12px 18px;
        font-size: 14px;
    }}
    QLineEdit:focus {{
        border-color: {COLORS['neon_pink']};
        background-color: #1a1a4a;
    }}
    
    QScrollBar:vertical {{
        background: {COLORS['dark_bg']};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {COLORS['neon_blue']}, 
            stop:1 {COLORS['neon_purple']});
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {COLORS['neon_pink']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
    }}
"""

# ============================================
# СТИЛЬ ДЛЯ ОКНА ВХОДА
# ============================================

LOGIN_STYLE = f"""
    QWidget {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {COLORS['dark_bg']}, 
            stop:0.5 #0a0a2a,
            stop:1 {COLORS['dark_bg']});
    }}
    
    QLineEdit {{
        background-color: {COLORS['dark_input']};
        color: {COLORS['text_primary']};
        border: 2px solid {COLORS['neon_blue']};
        border-radius: 12px;
        padding: 12px 18px;
        font-size: 14px;
    }}
    QLineEdit:focus {{
        border-color: {COLORS['neon_pink']};
        background-color: #1a1a4a;
    }}
    
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS['neon_pink']}, 
            stop:0.5 {COLORS['neon_purple']},
            stop:1 {COLORS['neon_blue']});
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 25px;
        font-size: 15px;
        font-weight: bold;
        min-height: 40px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #ff4d7a, 
            stop:0.5 #8b4ffc,
            stop:1 #4dd4ff);
    }}
    QPushButton:disabled {{
        background: #333355;
        color: #666688;
    }}
"""


FONT_FAMILY = 'Segoe UI'
MONO_FONT = 'Consolas'

# Обновляем экспорт
__all__ = [
    'CYBERLINK_ASCII',
    'COLORS',
    'BUTTON_STYLE',
    'DIALOG_STYLE',
    'MESSAGEBOX_STYLE',
    'INPUTDIALOG_STYLE',
    'MAIN_STYLE',
    'LOGIN_STYLE',
    'FONT_FAMILY',    # Добавить
    'MONO_FONT'       # Добавить
]