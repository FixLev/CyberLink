# src/theme/styles.py
# Космические стили для PyQt5

from src.theme.colors import COLORS

SPACE_STYLE = f"""
    QMainWindow {{
        background: transparent;
    }}
    
    QFrame#glass_panel {{
        background-color: {COLORS['glass_bg']};
        border: 1px solid {COLORS['glass_border']};
        border-radius: 20px;
    }}
    
    QPushButton {{
        background: transparent;
        color: {COLORS['text_secondary']};
        border: none;
        border-radius: 10px;
        padding: 8px 16px;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background: rgba(255, 255, 255, 0.05);
    }}
"""