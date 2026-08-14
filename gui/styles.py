# CyberLink - Стили киберпанк

CYBERLINK_ASCII = r"""
   ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██╗     ██╗███╗   ██╗██╗  ██╗
  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██║     ██║████╗  ██║██║ ██╔╝
  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██║     ██║██╔██╗ ██║█████╔╝ 
  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██║     ██║██║╚██╗██║██╔═██╗ 
  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║███████╗██║██║ ╚████║██║  ██╗
   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
"""

# Основные цвета
COLORS = {
    'neon_pink': '#ff2d55',
    'neon_blue': '#00d4ff',
    'neon_purple': '#7b2ffc',
    'dark_bg': '#0a0a1a',
    'dark_card': '#12122a',
    'dark_input': '#1a1a3a',
    'text_primary': '#e0e0ff',
    'text_secondary': '#8888aa',
    'neon_green': '#00ff88',
    'neon_yellow': '#ffdd00',
}

# Стиль для главного окна
MAIN_STYLE = f"""
    QMainWindow {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {COLORS['dark_bg']}, stop:1 #0a0a2a);
    }}
    QListWidget {{
        background-color: {COLORS['dark_card']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['neon_blue']};
        border-radius: 8px;
        padding: 5px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 13px;
    }}
    QListWidget::item {{
        padding: 12px;
        border-bottom: 1px solid #1a1a3a;
        border-radius: 4px;
    }}
    QListWidget::item:hover {{
        background-color: #1a1a4a;
        border-left: 3px solid {COLORS['neon_blue']};
    }}
    QListWidget::item:selected {{
        background-color: #1a1a5a;
        border-left: 3px solid {COLORS['neon_pink']};
        color: white;
    }}
    QTextEdit {{
        background-color: {COLORS['dark_card']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['neon_blue']};
        border-radius: 8px;
        padding: 15px;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
    }}
    QLineEdit {{
        background-color: {COLORS['dark_input']};
        color: {COLORS['text_primary']};
        border: 2px solid {COLORS['neon_blue']};
        border-radius: 20px;
        padding: 12px 20px;
        font-size: 14px;
        font-family: 'Consolas', monospace;
    }}
    QLineEdit:focus {{
        border-color: {COLORS['neon_pink']};
        background-color: #1a1a4a;
    }}
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS['neon_pink']}, stop:1 {COLORS['neon_purple']});
        color: white;
        border: none;
        border-radius: 20px;
        padding: 12px 25px;
        font-size: 14px;
        font-weight: bold;
        font-family: 'Segoe UI', Arial, sans-serif;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #ff3d6a, stop:1 #8b3ffc);
        box-shadow: 0 0 20px rgba(255, 45, 85, 0.3);
    }}
    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #cc1a44, stop:1 #6a1fcc);
    }}
    QLabel {{
        color: {COLORS['text_primary']};
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
    QScrollBar:vertical {{
        background: {COLORS['dark_bg']};
        width: 12px;
        border-radius: 6px;
    }}
    QScrollBar::handle:vertical {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS['neon_blue']}, stop:1 {COLORS['neon_purple']});
        border-radius: 6px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {COLORS['neon_pink']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
    }}
    QMenuBar {{
        background-color: {COLORS['dark_bg']};
        color: {COLORS['text_primary']};
        border-bottom: 1px solid {COLORS['neon_blue']};
    }}
    QMenuBar::item:selected {{
        background-color: {COLORS['neon_pink']};
    }}
    QStatusBar {{
        background-color: {COLORS['dark_bg']};
        color: {COLORS['neon_green']};
        border-top: 1px solid {COLORS['neon_blue']};
        font-family: 'Consolas', monospace;
    }}
"""

# Стиль для окна входа
LOGIN_STYLE = f"""
    QWidget {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {COLORS['dark_bg']}, stop:1 #0a0a2a);
    }}
    QLineEdit {{
        background-color: {COLORS['dark_input']};
        color: {COLORS['text_primary']};
        border: 2px solid {COLORS['neon_blue']};
        border-radius: 10px;
        padding: 12px 15px;
        font-size: 14px;
        font-family: 'Consolas', monospace;
    }}
    QLineEdit:focus {{
        border-color: {COLORS['neon_pink']};
        background-color: #1a1a4a;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.1);
    }}
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS['neon_pink']}, stop:1 {COLORS['neon_purple']});
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px;
        font-size: 14px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #ff3d6a, stop:1 #8b3ffc);
        box-shadow: 0 0 30px rgba(255, 45, 85, 0.2);
    }}
    QPushButton:disabled {{
        background: #333355;
        color: #666688;
    }}
    QLabel {{
        color: {COLORS['text_primary']};
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
"""