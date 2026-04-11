import flet as ft
import asyncio

class LoginView:
    def __init__(self):
        # UI Elements
        self.domain_input = ft.TextField(
            label="Domain Name", 
            hint_text="example.odoo.com",
            prefix_icon=ft.Icons.LANGUAGE
        )
        self.https_checkbox = ft.Checkbox(label="Use HTTPS", value=True)
        self.db_input = ft.TextField(
            label="Database Name",
            prefix_icon=ft.Icons.STORAGE
        )
        self.user_input = ft.TextField(
            label="User / Email",
            prefix_icon=ft.Icons.PERSON
        )
        self.password_input = ft.TextField(
            label="Password", 
            password=True, 
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK
        )

    def get_view(self, page: ft.Page):
        return ft.View(
            route="/login",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=350,
                    padding=30,
                    bgcolor=ft.Colors.SURFACE_BRIGHT,
                    border_radius=20,
                    content=ft.Column(
                        [
                            ft.Text("Odoo Login", size=28, weight="bold", color=ft.Colors.BLUE),
                            ft.Divider(height=10, color="transparent"),
                            self.domain_input,
                            self.https_checkbox,
                            self.db_input,
                            self.user_input,
                            self.password_input,
                            ft.Divider(height=20, color="transparent"),
                            ft.Button(
                                content="Login",
                                width=float("inf"),
                                height=50,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                                on_click=lambda e: asyncio.create_task(self.handle_login(page))
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    )
                )
            ]
        )

    async def handle_login(self, page: ft.Page):
        # Add your authentication logic here
        # On success:
        await page.push_route("/dashboard")