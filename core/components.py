import flet as ft

class ActionBox(ft.Container):
    def __init__(self, title, icon, on_click=None):
        super().__init__()

        self.content = ft.Column(
            [
                ft.Icon(icon, size=28, color=ft.Colors.PRIMARY),
                ft.Text(title, size=15, weight="bold", text_align=ft.TextAlign.CENTER)
            ],
            alignment="center",
            horizontal_alignment="center",
        )

        self.padding = 15
        self.border_radius = 20
        self.width = 150
        self.height = 100
        self.bgcolor = ft.Colors.SURFACE
        self.ink = True
        self.on_click = on_click
        self.shadow = ft.BoxShadow(
            blur_radius=12,
            color=ft.Colors.with_opacity(0.1, "black"),
        )