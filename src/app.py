# src/app.py
# Главное приложение CyberLink

import flet as ft
from src.theme.colors import COLORS
from src.theme.icons import Icons
from src.widgets.glass_panel import GlassPanel
from src.widgets.star_field import StarField


class CyberLinkApp:
    """Главное приложение CyberLink"""
    
    def __init__(self):
        self.page = None
        self.current_page = 'chats'
        self.nav_items = []
    
    def main(self, page: ft.Page):
        """Точка входа"""
        self.page = page
        
        # Настройки страницы
        page.title = "CyberLink"
        page.bgcolor = COLORS['bg_primary']
        page.padding = 0
        page.spacing = 0
        page.theme_mode = ft.ThemeMode.DARK
        
        # Максимизируем окно
        page.window_width = 1200
        page.window_height = 800
        page.window_min_width = 900
        page.window_min_height = 600
        
        # Шрифты (позже добавим локальные)
        page.fonts = {
            "Karvx": "assets/fonts/interface/KarvxBold.otf",
            "Interphases": "assets/fonts/interface/TTInterphasesProRegular.ttf",
            "InterphasesMedium": "assets/fonts/interface/TTInterphasesProMedium.ttf",
            "InterphasesBold": "assets/fonts/interface/TTInterphasesProBold.ttf",
            "Mussels": "assets/fonts/text/TTMusselsRegular.ttf",
            "MusselsItalic": "assets/fonts/text/TTMusselsItalic.ttf",
            "MusselsBold": "assets/fonts/text/TTMusselsBold.ttf",
        }
        
        # Основной контейнер
        main_container = ft.Container(
            content=self._build_main_layout(),
            expand=True,
            bgcolor=COLORS['bg_primary'],
        )
        
        page.add(main_container)
        page.update()
    
    def _build_main_layout(self):
        """Сборка основного макета"""
        return ft.Stack(
            [
                # Космический фон
                StarField(150),
                
                # Основной стеклянный контейнер
                GlassPanel(
                    content=ft.Column(
                        [
                            # Верхний бар
                            self._build_top_bar(),
                            
                            # Навигация
                            self._build_navigation(),
                            
                            # Основное содержимое
                            ft.Container(
                                content=self._build_content(),
                                expand=True,
                                padding=ft.padding.only(left=10, right=10, bottom=10),
                            ),
                        ],
                        spacing=0,
                        expand=True,
                    ),
                    expand=True,
                    margin=ft.margin.all(15),
                    border_radius=24,
                    height=None,
                ),
            ],
            expand=True,
        )
    
    def _build_top_bar(self):
        """Верхний бар с логотипом и кнопками"""
        return ft.Container(
            content=ft.Row(
                [
                    # Логотип
                    ft.Row(
                        [
                            ft.Text(
                                "✦ CYBERLINK",
                                font_family="Karvx",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.WHITE,
                                letter_spacing=4,
                            ),
                        ],
                        spacing=0,
                    ),
                    
                    # Справа: кнопки
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.icons.SETTINGS,
                                icon_color=ft.colors.WHITE54,
                                icon_size=20,
                                on_click=lambda e: self._open_settings(),
                            ),
                            ft.IconButton(
                                icon=ft.icons.REMOVE,
                                icon_color=ft.colors.WHITE54,
                                icon_size=20,
                                on_click=lambda e: self.page.window_minimize(),
                            ),
                            ft.IconButton(
                                icon=ft.icons.CROP_SQUARE,
                                icon_color=ft.colors.WHITE54,
                                icon_size=18,
                                on_click=lambda e: self._toggle_maximize(),
                            ),
                            ft.IconButton(
                                icon=ft.icons.CLOSE,
                                icon_color=ft.colors.WHITE54,
                                icon_size=20,
                                on_click=lambda e: self.page.window_close(),
                            ),
                        ],
                        spacing=2,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(left=20, right=10, top=10, bottom=10),
            bgcolor=ft.colors.TRANSPARENT,
            border=ft.border.only(bottom=ft.BorderSide(1, COLORS['glass_border'])),
        )
    
    def _build_navigation(self):
        """Панель навигации"""
        # Список вкладок
        tabs = [
            {"icon": Icons.CHATS(), "label": "Чаты", "key": "chats"},
            {"icon": Icons.CONTACTS(), "label": "Контакты", "key": "contacts"},
            {"icon": Icons.FILES(), "label": "Файлы", "key": "files"},
            {"icon": Icons.CHANNELS(), "label": "Каналы", "key": "channels"},
            {"icon": Icons.PROFILE(), "label": "Профиль", "key": "profile"},
        ]
        
        nav_buttons = []
        for tab in tabs:
            btn = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(tab["icon"], size=18),
                        ft.Text(
                            tab["label"],
                            size=13,
                            weight=ft.FontWeight.MEDIUM,
                            font_family="Interphases",
                        ),
                    ],
                    spacing=8,
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                border_radius=ft.border_radius.all(10),
                bgcolor=COLORS['accent_primary'] if tab["key"] == self.current_page else ft.colors.TRANSPARENT,
                opacity=1.0 if tab["key"] == self.current_page else 0.7,
                on_click=lambda e, key=tab["key"]: self._switch_page(key),
                data=tab["key"],
            )
            nav_buttons.append(btn)
            self.nav_items.append(btn)
        
        return ft.Container(
            content=ft.Row(
                nav_buttons,
                spacing=5,
            ),
            padding=ft.padding.only(left=20, top=5, bottom=10),
            bgcolor=ft.colors.TRANSPARENT,
        )
    
    def _build_content(self):
        """Основное содержимое в зависимости от текущей страницы"""
        if self.current_page == 'chats':
            return self._build_chats_page()
        elif self.current_page == 'contacts':
            return self._build_contacts_page()
        elif self.current_page == 'files':
            return self._build_files_page()
        elif self.current_page == 'channels':
            return self._build_channels_page()
        elif self.current_page == 'profile':
            return self._build_profile_page()
        return self._build_chats_page()
    
    def _build_chats_page(self):
        """Страница чатов"""
        return ft.Row(
            [
                # Список чатов
                ft.Container(
                    content=self._build_chat_list(),
                    width=320,
                    padding=ft.padding.all(5),
                ),
                # Разделитель
                ft.VerticalDivider(width=1, color=COLORS['glass_border']),
                # Окно чата
                ft.Container(
                    content=self._build_chat_view(),
                    expand=True,
                    padding=ft.padding.all(10),
                ),
            ],
            expand=True,
            spacing=0,
        )
    
    def _build_chat_list(self):
        """Список чатов"""
        return ft.Column(
            [
                # Поиск
                ft.TextField(
                    hint_text="Поиск...",
                    prefix_icon=ft.icons.SEARCH,
                    border=ft.InputBorder.NONE,
                    filled=True,
                    fill_color=COLORS['bg_input'],
                    text_style=ft.TextStyle(color=COLORS['text_primary'], font_family="Interphases"),
                    hint_style=ft.TextStyle(color=COLORS['text_dim']),
                ),
                
                # Список
                ft.ListView(
                    [
                        self._build_chat_item("Alice", "Привет! Как дела?", "12:30", True),
                        self._build_chat_item("Bob", "Ок, договорились!", "11:15", False),
                        self._build_chat_item("Charlie", "Спс", "10:00", True, 3),
                        self._build_chat_item("Dave", "Завтра встреча!", "09:30", True),
                        self._build_chat_item("Eve", "Привет!", "08:45", False),
                    ],
                    spacing=5,
                    expand=True,
                ),
            ],
            expand=True,
        )
    
    def _build_chat_item(self, name, preview, time, is_online, unread=0):
        """Элемент списка чатов"""
        return ft.Container(
            content=ft.Row(
                [
                    # Аватар
                    ft.Container(
                        content=ft.Text("🟢" if is_online else "⚪", size=12),
                        width=40,
                        height=40,
                        alignment=ft.alignment.center,
                        bgcolor=COLORS['bg_card'],
                        border_radius=ft.border_radius.all(20),
                        border=ft.border.all(1, COLORS['accent_primary'] if is_online else COLORS['text_dim']),
                    ),
                    # Информация
                    ft.Column(
                        [
                            ft.Text(
                                name,
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=COLORS['text_primary'],
                                font_family="InterphasesMedium",
                            ),
                            ft.Text(
                                preview,
                                size=12,
                                color=COLORS['text_secondary'],
                                font_family="Interphases",
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    # Время и непрочитанные
                    ft.Column(
                        [
                            ft.Text(
                                time,
                                size=10,
                                color=COLORS['text_dim'],
                                font_family="Interphases",
                            ),
                            ft.Container(
                                content=ft.Text(
                                    str(unread),
                                    size=10,
                                    color=ft.colors.WHITE,
                                    font_family="InterphasesBold",
                                ),
                                bgcolor=COLORS['accent_primary'] if unread > 0 else None,
                                border_radius=ft.border_radius.all(10),
                                padding=ft.padding.all(2) if unread > 0 else 0,
                                width=20 if unread > 0 else 0,
                                height=20 if unread > 0 else 0,
                                alignment=ft.alignment.center,
                                visible=unread > 0,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=2,
                    ),
                ],
            ),
            padding=ft.padding.all(10),
            border_radius=ft.border_radius.all(10),
            bgcolor=COLORS['bg_hover'] if unread > 0 else ft.colors.TRANSPARENT,
            on_click=lambda e: self._open_chat(name),
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
        )
    
    def _build_chat_view(self):
        """Окно чата"""
        return ft.Column(
            [
                # Заголовок чата
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Text("👤", size=20),
                                    ft.Column(
                                        [
                                            ft.Text(
                                                "@Alice",
                                                size=16,
                                                weight=ft.FontWeight.BOLD,
                                                color=COLORS['text_primary'],
                                                font_family="InterphasesMedium",
                                            ),
                                            ft.Text(
                                                "🟢 Онлайн",
                                                size=11,
                                                color=COLORS['accent_primary'],
                                                font_family="Interphases",
                                            ),
                                        ],
                                        spacing=0,
                                    ),
                                ],
                                spacing=10,
                            ),
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.CALL,
                                        icon_color=COLORS['accent_primary'],
                                        icon_size=20,
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.MORE_VERT,
                                        icon_color=COLORS['text_secondary'],
                                        icon_size=20,
                                    ),
                                ],
                                spacing=0,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.only(bottom=10),
                    border=ft.border.only(bottom=ft.BorderSide(1, COLORS['glass_border'])),
                ),
                
                # Сообщения
                ft.ListView(
                    [
                        self._build_message("Alice", "Привет! Как дела?", "12:30", False),
                        self._build_message("Вы", "Привет! Норм, а у тебя?", "12:31", True),
                        self._build_message("Alice", "Тоже хорошо! Что нового?", "12:32", False),
                        self._build_message("Вы", "Да всё по-старому...", "12:33", True),
                        self._build_message("Alice", "Ну ладно, встретимся завтра!", "12:35", False),
                        self._build_message("Вы", "Договорились! 👋", "12:36", True),
                    ],
                    spacing=8,
                    expand=True,
                ),
                
                # Поле ввода
                ft.Container(
                    content=ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.icons.ATTACH_FILE,
                                icon_color=COLORS['text_secondary'],
                                icon_size=22,
                            ),
                            ft.TextField(
                                hint_text="Введите сообщение...",
                                border=ft.InputBorder.NONE,
                                expanded=True,
                                text_style=ft.TextStyle(
                                    color=COLORS['text_primary'],
                                    font_family="Mussels",
                                    size=14,
                                ),
                                hint_style=ft.TextStyle(
                                    color=COLORS['text_dim'],
                                    font_family="Interphases",
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.icons.MIC,
                                icon_color=COLORS['text_secondary'],
                                icon_size=22,
                            ),
                            ft.Container(
                                content=ft.Icon(
                                    ft.icons.SEND,
                                    color=ft.colors.WHITE,
                                    size=18,
                                ),
                                bgcolor=COLORS['accent_primary'],
                                border_radius=ft.border_radius.all(25),
                                padding=ft.padding.all(10),
                                on_click=lambda e: self._send_message(),
                            ),
                        ],
                    ),
                    padding=ft.padding.all(5),
                    bgcolor=COLORS['bg_input'],
                    border_radius=ft.border_radius.all(25),
                    border=ft.border.all(1, COLORS['glass_border']),
                ),
            ],
            expand=True,
            spacing=10,
        )
    
    def _build_message(self, sender, text, time, is_my):
        """Облачко сообщения"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                f"@{sender}" if not is_my else "",
                                size=11,
                                color=COLORS['accent_primary'] if not is_my else COLORS['text_dim'],
                                font_family="Interphases",
                            ),
                            ft.Text(
                                time,
                                size=9,
                                color=COLORS['text_dim'],
                                font_family="Interphases",
                            ),
                        ],
                        spacing=5,
                    ),
                    ft.Text(
                        text,
                        size=14,
                        color=COLORS['text_primary'],
                        font_family="Mussels",
                    ),
                ],
                spacing=2,
            ),
            padding=ft.padding.all(12),
            bgcolor=COLORS['glass_bg'] if is_my else COLORS['bg_card'],
            border_radius=ft.border_radius.only(
                top_left=15,
                top_right=15,
                bottom_left=5 if is_my else 15,
                bottom_right=15 if is_my else 5,
            ),
            border=ft.border.all(1, COLORS['glass_border']),
            alignment=ft.alignment.center_right if is_my else ft.alignment.center_left,
            margin=ft.margin.only(left=50 if is_my else 0, right=0 if is_my else 50),
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
        )
    
    def _build_contacts_page(self):
        """Страница контактов (заглушка)"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "📇 Контакты",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS['text_primary'],
                        font_family="InterphasesBold",
                    ),
                    ft.Text(
                        "Скоро здесь будет список ваших контактов",
                        color=COLORS['text_secondary'],
                        font_family="Interphases",
                    ),
                    ft.Text(
                        "👤 @Alice\n👤 @Bob\n👤 @Charlie",
                        color=COLORS['text_dim'],
                        font_family="Mussels",
                    ),
                ],
                spacing=10,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
    
    def _build_files_page(self):
        """Страница файлов (заглушка)"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "📁 Файлы",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS['text_primary'],
                        font_family="InterphasesBold",
                    ),
                    ft.Text(
                        "Скоро здесь будут все ваши файлы",
                        color=COLORS['text_secondary'],
                        font_family="Interphases",
                    ),
                    ft.Row(
                        [
                            ft.Text("🖼️", size=40),
                            ft.Text("🎬", size=40),
                            ft.Text("🎵", size=40),
                            ft.Text("📄", size=40),
                        ],
                        spacing=20,
                    ),
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
    
    def _build_channels_page(self):
        """Страница каналов (заглушка)"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "📡 Каналы",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS['text_primary'],
                        font_family="InterphasesBold",
                    ),
                    ft.Text(
                        "Скоро здесь будут ваши каналы",
                        color=COLORS['text_secondary'],
                        font_family="Interphases",
                    ),
                    ft.Text(
                        "🔹 CyberLink Новости\n🔹 Космические технологии\n🔹 AI разработка",
                        color=COLORS['text_dim'],
                        font_family="Mussels",
                    ),
                ],
                spacing=10,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
    
    def _build_profile_page(self):
        """Страница профиля (заглушка)"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Text("👤", size=80),
                        width=120,
                        height=120,
                        alignment=ft.alignment.center,
                        bgcolor=COLORS['bg_card'],
                        border_radius=ft.border_radius.all(60),
                        border=ft.border.all(2, COLORS['accent_primary']),
                    ),
                    ft.Text(
                        "@Electric_Eye",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS['text_primary'],
                        font_family="InterphasesBold",
                    ),
                    ft.Text(
                        "Кибер-энтузиаст | Тестировщик",
                        size=14,
                        color=COLORS['text_secondary'],
                        font_family="Interphases",
                    ),
                    ft.Row(
                        [
                            ft.Text("🟢 Онлайн", color=COLORS['online'], font_family="Interphases"),
                            ft.Text("•", color=COLORS['text_dim']),
                            ft.Text("📍 Москва", color=COLORS['text_dim'], font_family="Interphases"),
                        ],
                        spacing=5,
                    ),
                    ft.Divider(color=COLORS['glass_border']),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("📊", size=24),
                                    ft.Text("12", size=18, weight=ft.FontWeight.BOLD, font_family="InterphasesBold"),
                                    ft.Text("Чатов", size=12, color=COLORS['text_dim'], font_family="Interphases"),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.VerticalDivider(width=1, color=COLORS['glass_border']),
                            ft.Column(
                                [
                                    ft.Text("👥", size=24),
                                    ft.Text("8", size=18, weight=ft.FontWeight.BOLD, font_family="InterphasesBold"),
                                    ft.Text("Контактов", size=12, color=COLORS['text_dim'], font_family="Interphases"),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.VerticalDivider(width=1, color=COLORS['glass_border']),
                            ft.Column(
                                [
                                    ft.Text("📁", size=24),
                                    ft.Text("23", size=18, weight=ft.FontWeight.BOLD, font_family="InterphasesBold"),
                                    ft.Text("Файлов", size=12, color=COLORS['text_dim'], font_family="Interphases"),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=20,
                    ),
                    ft.ElevatedButton(
                        "✏️ Редактировать профиль",
                        icon=ft.icons.EDIT,
                        style=ft.ButtonStyle(
                            bgcolor=COLORS['accent_primary'],
                            color=ft.colors.WHITE,
                            padding=ft.padding.symmetric(horizontal=30, vertical=12),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        on_click=lambda e: self._open_settings(),
                    ),
                ],
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
    
    def _switch_page(self, key: str):
        """Переключение страницы"""
        self.current_page = key
        
        # Обновляем навигацию
        for item in self.nav_items:
            is_active = item.data == key
            item.bgcolor = COLORS['accent_primary'] if is_active else ft.colors.TRANSPARENT
            item.opacity = 1.0 if is_active else 0.7
        
        # Обновляем содержимое
        content = self._build_content()
        # Находим контейнер с содержимым и обновляем
        for control in self.page.controls:
            if isinstance(control, ft.Container) and control.content:
                # Ищем стек с фоном
                if isinstance(control.content, ft.Stack):
                    for child in control.content.controls:
                        if isinstance(child, GlassPanel):
                            # Обновляем содержимое стеклянной панели
                            column = child.content
                            if isinstance(column, ft.Column) and len(column.controls) >= 3:
                                # Заменяем третий элемент (контейнер с содержимым)
                                if isinstance(column.controls[2], ft.Container):
                                    old_container = column.controls[2]
                                    new_container = ft.Container(
                                        content=content,
                                        expand=True,
                                        padding=ft.padding.only(left=10, right=10, bottom=10),
                                    )
                                    # Копируем свойства из старого
                                    column.controls[2] = new_container
                                    self.page.update()
                                    return
    
    def _open_chat(self, name: str):
        """Открытие чата"""
        print(f"🔓 Открыт чат с {name}")
        # Здесь будет переход к чату
    
    def _open_settings(self):
        """Открытие настроек"""
        print("⚙️ Открыты настройки")
    
    def _send_message(self):
        """Отправка сообщения"""
        print("📤 Сообщение отправлено")
    
    def _toggle_maximize(self):
        """Развернуть/свернуть окно"""
        if self.page.window_maximized:
            self.page.window_maximized = False
        else:
            self.page.window_maximized = True
        self.page.update()


# Точка входа
def main():
    app = CyberLinkApp()
    ft.app(target=app.main, assets_dir="assets")


if __name__ == "__main__":
    main()