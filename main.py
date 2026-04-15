import asyncio
import flet as ft
from modules.telesales import telesales
from login_view import LoginView
from odoo_client import OdooAPI as OdooAPI

client = OdooAPI()

routes = {
    'dashboard' : '/dashboard',
    'login': '/login',
    'marketing': '/dashboard/marketing',
    'telesales': '/dashboard/marketing/telesales'
}

async def main(page: ft.Page):
    page.title = "Routes + Box Layout"
    page.padding = 20

    # 🔹 LIGHT THEME
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE,
            secondary=ft.Colors.AMBER,
            surface=ft.Colors.WHITE,
            on_surface=ft.Colors.BLACK,   # ✅ correct contrast
            on_primary=ft.Colors.WHITE,
        ),
        text_theme=ft.TextTheme(
            body_medium=ft.TextStyle(size=16),
            title_large=ft.TextStyle(size=22, weight=ft.FontWeight.BOLD),
        )
    )

    # 🔹 DARK THEME
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_200,
            secondary=ft.Colors.AMBER_200,
            surface=ft.Colors.GREY_900,
            on_surface=ft.Colors.WHITE,   # ✅ correct contrast
            on_primary=ft.Colors.BLACK,
        )
    )

    # 🔹 Default mode
    page.theme_mode = ft.ThemeMode.DARK

    def get_dashboard():
        return ft.View(
                    route="/dashboard",
                    controls=[
                        ft.AppBar(
                            title=ft.Text("Dashboard", color=ft.Colors.ON_PRIMARY),
                            leading=ft.Icon(ft.Icons.DASHBOARD, color=ft.Colors.ON_PRIMARY),
                            bgcolor=ft.Colors.PRIMARY,
                        ),

                        ft.Row(
                            [
                                box(
                                    "Nhân Sự",
                                    ft.Icons.GROUP,
                                ),
                                box(
                                    "Khách Hàng",
                                    ft.Icons.PERSON_OUTLINE,
                                )                         
                            ],
                            wrap=True,  # responsive
                            spacing=20,
                        ),
                        ft.Row(
                            [
                                box(
                                    "Dự Án",
                                    ft.Icons.HOUSE,
                                ),
                                box(
                                    "Marketing",
                                    ft.Icons.CAMPAIGN,
                                    lambda e: asyncio.create_task(page.push_route(routes["marketing"]))
                                )
                            ],
                            wrap=True,  # responsive
                            spacing=20
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )

    # 🔹 Reusable box
    def box(title, icon=None, on_click=None):
        return ft.Container(
            content=ft.Column(
                [ 
                    ft.Icon(icon, size=28, color=ft.Colors.PRIMARY),
                    ft.Text(title, size=15, weight="bold"),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=15,
            border_radius=20,
            width=150,
            height=100,
            bgcolor=ft.Colors.SURFACE,
            shadow=ft.BoxShadow(
                blur_radius=12,
                spread_radius=1,
                color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
            ),
            ink=True,
            on_click=on_click,
        )

    def route_change():
        page.views.clear()

        page.views.append(
            login_view.get_view(page)
        )

        # 🔹 HOME VIEW
        if page.route == routes["dashboard"]:
            page.views.append(
                get_dashboard()
            )

        # 🔹 Marketing View
        if page.route == routes["marketing"]:
            page.views.append(
                ft.View(
                    route=routes["marketing"],
                    controls=[
                        ft.AppBar(
                            title=ft.Text(
                                "Marketing",
                                color=ft.Colors.ON_PRIMARY
                            ),
                            leading=ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                icon_color=ft.Colors.ON_PRIMARY,
                                on_click=lambda e: asyncio.create_task(
                                    page.push_route(routes["dashboard"])
                                )
                            ),
                            bgcolor=ft.Colors.PRIMARY,
                        ),

                        ft.Row(
                            [
                                box("Telesales", ft.Icons.PHONE, lambda e: asyncio.create_task(page.push_route(routes["telesales"]))),
                                box("Mailing", ft.Icons.MAIL),
                                box("Posting", ft.Icons.POST_ADD)
                            ],
                            wrap=True,  # responsive
                            spacing=20
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

        # 🔹 Telesales View
        if page.route == routes["telesales"]:
            page.views.append(sales_phone.get_view(page, routes["marketing"]))

        page.update()
    
    async def view_pop(e):
        if e.view:
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    route_change()

sales_phone = telesales.TelesalesApp()
login_view = LoginView()
if __name__ == "__main__":
    ft.run(main)
