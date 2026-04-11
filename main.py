import asyncio
import flet as ft
from modules.telesales import telesales
from functools import partial
from odoo_client import OdooClient
from login_view import LoginView

def main(page: ft.Page):
    page.title = "Routes + Box Layout"
    page.padding = 20

    # 🔹 Reusable box
    def box(title, icon=None, on_click=None):
        return ft.Container(
            content=ft.Column(
                [ 
                    ft.Icon(icon, size=25) if icon else ft.Container(),
                    ft.Text(title, size=15, weight="bold"),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=10,
            border_radius=15,
            bgcolor=ft.Colors.BLUE_50,
            width=150,
            height=100,  # ✅ square
            on_click=on_click,  # ✅ whole box clickable
            ink=True,  # ripple effect on click
        )

    def route_change():
        page.views.clear()

        page.views.append(
            login_view.get_view(page)
        )

        # 🔹 HOME VIEW
        if page.route == "/dashboard":
            page.views.append(
                ft.View(
                    route="/dashboard",
                    controls=[
                        ft.AppBar(
                            title=ft.Text("Dashboard"),
                            leading=ft.Icon(ft.Icons.DASHBOARD),
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
                                    lambda e: asyncio.create_task(page.push_route("/dashboard/marketing"))
                                )
                            ],
                            wrap=True,  # responsive
                            spacing=20
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

        # 🔹 Marketing View
        if page.route == "/dashboard/marketing":
            page.views.append(
                ft.View(
                    route="/dashboard/marketing",
                    controls=[
                        ft.AppBar(
                            title=ft.Text("Marketing"),
                            leading=ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=lambda e: asyncio.create_task(page.push_route("/dashboard"))
                            )
                        ),

                        ft.Row(
                            [
                                box("Telesales", ft.Icons.PHONE, lambda e: asyncio.create_task(page.push_route("/dashboard/marketing/telesales"))),
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
        if page.route == "/dashboard/marketing/telesales":
            page.views.append(sales_phone.get_view(page, "/dashboard/marketing"))

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

# box(
#                                 "Telesales",
#                                 ft.Icons.PHONE,
#                                 lambda e: asyncio.create_task(page.push_route("/telesales")),
#                             ),