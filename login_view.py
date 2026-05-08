import flet as ft
import asyncio
import time
from odoo_client import OdooAPI as OdooAPI

class LoginView:
    def __init__(self):
        self.logo = ft.Image(
            src="assets/logo.png", 
            width=250,
            height=200,
            fit='CONTAIN',
            margin=ft.Margin.only(top=10, bottom=10)
        )

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

        self.login_button = ft.Button(
            content="Login to HT",
            icon=ft.Icons.LOGIN,
            height=50,
            expand=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
            )
        )

    def get_view(self, page: ft.Page):
        self.login_button.on_click = lambda e: asyncio.create_task(self.handle_login(page))

        return ft.View(
            route="/login",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,  # center when possible
            controls=[
                ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,  # keep scroll
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=350,
                            padding=30,
                            bgcolor=ft.Colors.SURFACE_BRIGHT,
                            border_radius=20,
                            margin=ft.Margin(20, 40, 20, 40),  # breathing space for scroll
                            content=ft.Column(
                                controls=[
                                    self.logo,

                                    self.domain_input,
                                    self.https_checkbox,
                                    self.db_input,

                                    self.user_input,
                                    self.password_input,

                                    self.login_button,
                                ],
                                spacing=15,
                                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                            )
                        )
                    ]
                )
            ]
        )

    async def handle_login(self, page: ft.Page):
        # Validate
        if not all([
            self.domain_input.value,
            self.db_input.value,
            self.user_input.value,
            self.password_input.value
        ]):
            self.show_message(page, "All fields are required", True)
            return

        # Build URL
        protocol = "https" if self.https_checkbox.value else "http"
        base_url = f"{protocol}://{self.domain_input.value.strip()}"


        client = OdooAPI(
            base_url=base_url,
            db=self.db_input.value,
            username=self.user_input.value,
            password=self.password_input.value             
        )
        page.session.store.set("client", client)

        success = client.login()


        if success:
            self.show_message(page, "Đăng nhập thành công.")
            await page.push_route("/dashboard")         
        else:
            self.show_message(page, "Đăng nhập thất bại, vui lòng kiểm tra lại thông tin.", True)
            page.update()

    def show_message(self, page, text, is_error=False):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(text),
            bgcolor=ft.Colors.RED_400 if is_error else ft.Colors.GREEN_400
        )
        page.show_dialog(page.snack_bar) 