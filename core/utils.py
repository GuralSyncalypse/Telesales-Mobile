import flet as ft
import asyncio

class Utils:
    @staticmethod
    def show_message(page : ft.Page, text, is_error=False):
        page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.ERROR if is_error else ft.Icons.CHECK_CIRCLE,
                    color=ft.Colors.WHITE
                ),
                ft.Text(text)
            ]),
            bgcolor=ft.Colors.RED_400 if is_error else ft.Colors.GREEN_400,
            duration=2000
        )
        page.show_dialog(page.snack_bar)
        page.update()

    @staticmethod
    def safe_route(page : ft.Page, route):
        asyncio.create_task(page.push_route(route))