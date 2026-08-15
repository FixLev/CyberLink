import flet as ft

def main(page: ft.Page):
    # Настройки окна
    page.title = "CyberLink"
    page.bgcolor = "#0a0a12"
    page.padding = 0
    page.window_width = 1000
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.DARK

    # Верхняя панель
    header = ft.Container(
        content=ft.Row(
            [
                ft.Text("✦ CYBERLINK", size=24, weight="bold", color="white"),
                ft.Row([
                    ft.TextButton("⚙️"),
                    ft.TextButton("━"),
                    ft.TextButton("☐"),
                    ft.TextButton("✕"),
                ]),
            ],
            alignment="spaceBetween",
        ),
        padding=15,
    )

    # Навигация
    nav = ft.Container(
        content=ft.Row(
            [
                ft.TextButton("Чаты", style=ft.ButtonStyle(color="white", bgcolor="#4fc3f7")),
                ft.TextButton("Контакты", style=ft.ButtonStyle(color="gray")),
                ft.TextButton("Файлы", style=ft.ButtonStyle(color="gray")),
                ft.TextButton("Каналы", style=ft.ButtonStyle(color="gray")),
                ft.TextButton("Профиль", style=ft.ButtonStyle(color="gray")),
            ],
            spacing=5,
        ),
        padding=15,
    )

    # Контент
    content = ft.Container(
        content=ft.Column(
            [
                ft.Text("🌌 Добро пожаловать в CyberLink!", size=28, weight="bold", color="white"),
                ft.Text("Космический P2P мессенджер с полным шифрованием", size=16, color="gray400"),
                ft.Text("🚀 Скоро здесь будет полный функционал", size=14, color="gray600"),
            ],
            horizontal_alignment="center",
            spacing=10,
        ),
        expand=True,
    )

    # Сборка
    page.add(
        ft.Column(
            [header, nav, content],
            spacing=0,
            expand=True,
        )
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)