# src/views/profile_view.py
# Страница профиля с редактированием

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.theme.colors import COLORS
from src.core.profile_manager import ProfileManager
from src.utils.dialogs import show_cyber_message  # ДОБАВЛЯЕМ ИМПОРТ


class ProfileView(QWidget):
    def __init__(self, username, friends_manager=None, network=None, password=None):
        super().__init__()
        self.username = username
        self.friends_manager = friends_manager
        self.network = network
        self.password = password
        
        # Создаём ProfileManager с паролем
        self.profile_manager = ProfileManager(username, password)
        self.is_editing = False
        
        self.init_ui()
        self.load_profile()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Заголовок
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("border-bottom: 1px solid rgba(79, 195, 247, 0.06);")
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("👤 Профиль")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #f5f5f5;
            font-family: 'TT Mussels', 'Arial', sans-serif;
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Кнопка редактирования
        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background: rgba(79, 195, 247, 0.12);
                color: #4fc3f7;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 14px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(79, 195, 247, 0.2);
            }
        """)
        self.edit_btn.clicked.connect(self.toggle_edit)
        header_layout.addWidget(self.edit_btn)
        
        # Кнопка сохранения (скрыта по умолчанию)
        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: rgba(79, 195, 247, 0.15);
                color: #4fc3f7;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 14px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(79, 195, 247, 0.25);
            }
        """)
        self.save_btn.clicked.connect(self.save_profile)
        self.save_btn.hide()
        header_layout.addWidget(self.save_btn)
        
        layout.addWidget(header)
        
        # Контент
        self.content = QScrollArea()
        self.content.setWidgetResizable(True)
        self.content.setStyleSheet("""
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
        """)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(40, 30, 40, 30)
        self.content_layout.setSpacing(15)
        self.content_layout.setAlignment(Qt.AlignTop)
        
        # Аватар
        self.avatar_container = QFrame()
        self.avatar_container.setFixedHeight(150)
        avatar_layout = QHBoxLayout(self.avatar_container)
        avatar_layout.setAlignment(Qt.AlignCenter)
        
        self.avatar_label = QLabel("👤")
        self.avatar_label.setStyleSheet("font-size: 80px;")
        self.avatar_label.setAlignment(Qt.AlignCenter)
        avatar_layout.addWidget(self.avatar_label)
        
        self.content_layout.addWidget(self.avatar_container)
        
        # Кнопка изменения аватарки
        self.avatar_btn = QPushButton("📷 Сменить аватар")
        self.avatar_btn.setCursor(Qt.PointingHandCursor)
        self.avatar_btn.setStyleSheet("""
            QPushButton {
                background: rgba(79, 195, 247, 0.08);
                color: #4fc3f7;
                border: 1px solid rgba(79, 195, 247, 0.15);
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 12px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
            }
            QPushButton:hover {
                background: rgba(79, 195, 247, 0.15);
            }
        """)
        self.avatar_btn.clicked.connect(self.change_avatar)
        self.avatar_btn.hide()
        self.content_layout.addWidget(self.avatar_btn, alignment=Qt.AlignCenter)
        
        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background: rgba(79, 195, 247, 0.06); max-height: 1px;")
        self.content_layout.addWidget(line)
        
        # === ОТОБРАЖАЕМОЕ ИМЯ ===
        name_row = QHBoxLayout()
        name_label = QLabel("👤 Имя:")
        name_label.setStyleSheet("color: #8888aa; font-size: 14px; font-family: 'TT Mussels', 'Arial', sans-serif; min-width: 150px;")
        name_row.addWidget(name_label)
        
        self.name_display = QLabel("")
        self.name_display.setStyleSheet("color: #f5f5f5; font-size: 14px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        name_row.addWidget(self.name_display, stretch=1)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите отображаемое имя")
        self.name_input.setStyleSheet("""
            QLineEdit {
                background: rgba(30, 30, 48, 0.6);
                color: #f5f5f5;
                border: 1px solid rgba(79, 195, 247, 0.15);
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 14px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
            }
            QLineEdit:focus {
                border-color: rgba(79, 195, 247, 0.4);
            }
        """)
        self.name_input.hide()
        name_row.addWidget(self.name_input, stretch=1)
        
        self.content_layout.addLayout(name_row)
        
        # === ПОЛ ===
        gender_row = QHBoxLayout()
        gender_label = QLabel("⚧️ Пол:")
        gender_label.setStyleSheet("color: #8888aa; font-size: 14px; font-family: 'TT Mussels', 'Arial', sans-serif; min-width: 150px;")
        gender_row.addWidget(gender_label)
        
        self.gender_display = QLabel("Не указан")
        self.gender_display.setStyleSheet("color: #f5f5f5; font-size: 14px; font-family: 'TT Mussels', 'Arial', sans-serif;")
        gender_row.addWidget(self.gender_display, stretch=1)
        
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Не указан", "Мужской", "Женский"])
        self.gender_combo.setStyleSheet("""
            QComboBox {
                background: rgba(30, 30, 48, 0.6);
                color: #f5f5f5;
                border: 1px solid rgba(79, 195, 247, 0.15);
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 14px;
                font-family: 'TT Mussels', 'Arial', sans-serif;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #8888aa;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background: rgba(30, 30, 48, 0.9);
                color: #f5f5f5;
                border: 1px solid rgba(79, 195, 247, 0.15);
                border-radius: 8px;
                selection-background-color: rgba(79, 195, 247, 0.2);
            }
        """)
        self.gender_combo.hide()
        gender_row.addWidget(self.gender_combo)
        
        self.content_layout.addLayout(gender_row)
        
        # === ОСТАЛЬНЫЕ ПОЛЯ ===
        self.info_layout = QGridLayout()
        self.info_layout.setSpacing(15)
        
        info_items = [
            ("📱 Телефон", "phone", "+7 (999) 123-45-67"),
            ("📧 Email", "email", "user@example.com"),
            ("📅 Дата рождения", "birth_date", "15.06.1995"),
            ("🏙️ Город", "city", "Москва, Россия"),
            ("💼 Должность", "occupation", "Software Developer"),
            ("🏢 Компания", "company", "CyberLink Inc."),
        ]
        
        self.info_widgets = {}
        
        for i, (label, key, default) in enumerate(info_items):
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #8888aa; font-size: 14px; font-family: 'TT Mussels', 'Arial', sans-serif;")
            self.info_layout.addWidget(label_widget, i, 0)
            
            display_label = QLabel(default)
            display_label.setStyleSheet("color: #f5f5f5; font-size: 14px; font-family: 'TT Mussels', 'Arial', sans-serif;")
            display_label.setObjectName(f"{key}_label")
            self.info_layout.addWidget(display_label, i, 1)
            
            edit_input = QLineEdit()
            edit_input.setPlaceholderText(default)
            edit_input.setStyleSheet("""
                QLineEdit {
                    background: rgba(30, 30, 48, 0.6);
                    color: #f5f5f5;
                    border: 1px solid rgba(79, 195, 247, 0.15);
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-size: 14px;
                    font-family: 'TT Mussels', 'Arial', sans-serif;
                }
                QLineEdit:focus {
                    border-color: rgba(79, 195, 247, 0.4);
                }
            """)
            edit_input.setObjectName(f"{key}_input")
            edit_input.hide()
            self.info_layout.addWidget(edit_input, i, 1)
            
            self.info_widgets[key] = {
                'label': display_label,
                'input': edit_input,
                'default': default
            }
        
        self.content_layout.addLayout(self.info_layout)
        self.content_layout.addStretch()
        
        self.content.setWidget(self.content_widget)
        layout.addWidget(self.content)
    
    def load_profile(self):
        """Загрузка профиля"""
        profile = self.profile_manager.get_profile()
        
        # Отображаемое имя
        display_name = profile.get("display_name", self.username)
        self.name_display.setText(display_name)
        self.name_input.setText(display_name)
        
        # Пол
        gender = profile.get("gender", "Не указан")
        self.gender_display.setText(gender)
        index = self.gender_combo.findText(gender)
        if index >= 0:
            self.gender_combo.setCurrentIndex(index)
        else:
            self.gender_combo.setCurrentIndex(0)
        
        # Остальные поля
        for key, widget_data in self.info_widgets.items():
            value = profile.get(key, widget_data['default'])
            widget_data['label'].setText(str(value) if value else "—")
            widget_data['input'].setText(str(value) if value else "")
        
        # Аватар
        avatar = self.profile_manager.get_avatar()
        if avatar:
            self.avatar_label.setPixmap(avatar.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.avatar_label.setText("")
        else:
            self.avatar_label.setText("👤")
            self.avatar_label.setStyleSheet("font-size: 80px;")
    
    def toggle_edit(self):
        self.is_editing = not self.is_editing
        
        if self.is_editing:
            self.edit_btn.setText("❌ Отменить")
            self.edit_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 45, 85, 0.12);
                    color: #ff2d55;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 18px;
                    font-size: 14px;
                    font-family: 'TT Mussels', 'Arial', sans-serif;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgba(255, 45, 85, 0.2);
                }
            """)
            self.save_btn.show()
            self.avatar_btn.show()
            
            self.name_display.hide()
            self.name_input.show()
            self.gender_display.hide()
            self.gender_combo.show()
            
            for widget_data in self.info_widgets.values():
                widget_data['label'].hide()
                widget_data['input'].show()
        else:
            self.edit_btn.setText("✏️ Редактировать")
            self.edit_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(79, 195, 247, 0.12);
                    color: #4fc3f7;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 18px;
                    font-size: 14px;
                    font-family: 'TT Mussels', 'Arial', sans-serif;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgba(79, 195, 247, 0.2);
                }
            """)
            self.save_btn.hide()
            self.avatar_btn.hide()
            
            self.name_display.show()
            self.name_input.hide()
            self.gender_display.show()
            self.gender_combo.hide()
            
            for widget_data in self.info_widgets.values():
                widget_data['label'].show()
                widget_data['input'].hide()
            
            self.load_profile()
    
    def save_profile(self):
        profile_data = {}
        
        display_name = self.name_input.text().strip()
        if display_name:
            profile_data["display_name"] = display_name
        
        gender = self.gender_combo.currentText()
        if gender:
            profile_data["gender"] = gender
        
        for key, widget_data in self.info_widgets.items():
            value = widget_data['input'].text().strip()
            if value:
                profile_data[key] = value
        
        if profile_data:
            success = self.profile_manager.update_profile(profile_data)
            if success:
                self.toggle_edit()
                show_cyber_message(self, "Успех", "✅ Профиль сохранён!", QMessageBox.Information)
            else:
                show_cyber_message(self, "Ошибка", "❌ Не удалось сохранить профиль", QMessageBox.Critical)
        else:
            self.toggle_edit()
    
    def change_avatar(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Выберите аватар",
            "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            if self.profile_manager.set_avatar(file_path):
                avatar = self.profile_manager.get_avatar()
                if avatar:
                    self.avatar_label.setPixmap(avatar.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    self.avatar_label.setText("")
                else:
                    self.avatar_label.setText("👤")
                    self.avatar_label.setStyleSheet("font-size: 80px;")
                
                show_cyber_message(self, "Успех", "✅ Аватар обновлён!", QMessageBox.Information)