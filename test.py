import flet as ft


def main(page: ft.Page):
    page.title = "Theme Switch Demo"
    page.theme_mode = ft.ThemeMode.LIGHT  # default

    # 🔹 Function to toggle theme
    def toggle_theme(e):
        if theme_switch.value:
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
        page.update()

    # 🔹 Switch control
    theme_switch = ft.Switch(
        label="Dark Mode",
        value=False,
        on_change=toggle_theme
    )

    # 🔹 Example UI components (auto adapt)
    content = ft.Column(
        controls=[
            ft.Text("Hello, Flet!", size=30, weight="bold"),
            ft.Text("This UI adapts to theme changes."),
            ft.Button("Click me"),
            ft.TextField(label="Enter something"),
            theme_switch,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.add(content)


ft.app(target=main)