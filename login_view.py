import flet as ft
import asyncio
import json
from odoo_client import OdooAPI as OdooAPI
from core.utils import Utils

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

        self.remember_password_checkbox = ft.Checkbox(
            label="Remember password",
            value=False
        )

    async def __get_previous_login_info(self):
        login_info = await self.page.shared_preferences.get("login_info")

        if login_info:
            login_info = json.loads(login_info)

            self.domain_input.value = login_info.get("domain", "")
            self.db_input.value = login_info.get("db", "")
            self.user_input.value = login_info.get("user", "")
            self.https_checkbox.value = login_info.get("https", True)

            self.remember_password_checkbox.value = login_info.get("remember_password", False)

            if self.remember_password_checkbox.value:
                self.password_input.value = login_info.get("password", "")
            else:
                self.password_input.value = ""
        
        self.page.update()


    def get_view(self, page: ft.Page):
        self.login_button.on_click = lambda e: asyncio.create_task(self.handle_login())
        self.page : ft.Page = page

        asyncio.create_task(self.__get_previous_login_info())

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
                                    self.remember_password_checkbox,

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

    async def __store_login_session(self):
        data = {
            "domain": self.domain_input.value,
            "db": self.db_input.value,
            "user": self.user_input.value,
            "https": self.https_checkbox.value,
            "password": self.password_input.value if self.remember_password_checkbox.value else "",
            "remember_password": self.remember_password_checkbox.value
        }

        await self.page.shared_preferences.set(
            "login_info",
            json.dumps(data)
        )

    async def handle_login(self):
        # Validate
        if not all([
            self.domain_input.value,
            self.db_input.value,
            self.user_input.value,
            self.password_input.value
        ]):
            self.show_message(self.page, "Vui lòng điền đầy đủ thông tin", True)
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
        self.page.session.store.set("client", client)

        success = client.login()

        if success:
            await self.__store_login_session()

            Utils.show_message(self.page, "Đăng nhập thành công.")
            await self.page.push_route("/dashboard")         
        else:
            Utils.show_message(self.page, "Đăng nhập thất bại, vui lòng kiểm tra lại thông tin.", True)
            self.page.update()