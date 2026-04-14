import flet as ft
import asyncio
from odoo_client import OdooClient


class LoginView:
    def __init__(self):
        self.logo = ft.Image(
            src="assets/HTLand-1.png", 
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
            icon=ft.Icons.LOGIN,   # 👈 add icon
            width=350,
            height=50,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),  # rounded corners
                text_style=ft.TextStyle(size=16, weight="bold"),
            )
        )

    def get_view(self, page: ft.Page):
        self.login_button.on_click = lambda e: asyncio.create_task(self.handle_login(page))

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
                            self.logo,
                            ft.Divider(height=10, color="transparent"),

                            self.domain_input,
                            self.https_checkbox,
                            self.db_input,
                            self.user_input,
                            self.password_input,

                            ft.Divider(height=20, color="transparent"),
                            self.login_button                        
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    )
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
            self._show(page, "All fields are required", True)
            return

        # Build URL
        protocol = "https" if self.https_checkbox.value else "http"
        base_url = f"{protocol}://{self.domain_input.value.strip()}"


        client = OdooClient(
            base_url=base_url,
            db="Odoo",
            username=self.user_input.value,
            password=self.password_input.value             
        )
        page.session.store.set("client", client)

        success = client.login()


        if success:
            # ✅ correct navigation
            await page.push_route("/dashboard")
            self._show(page, "Đăng nhập thành công.", True)

        else:
            self._show(page, "Đăng nhập thất bại, vui lòng kiểm tra lại thông thin.", True)

        page.update()

    def _show(self, page, msg, error=False):
        page.snack_bar = ft.SnackBar(
            ft.Text(msg),
            bgcolor=ft.Colors.RED if error else ft.Colors.GREEN
        )
        page.snack_bar.open = True
        page.update()