import flet as ft
import requests
import json

class OdooClient:
    def __init__(self, url, db, username, password):
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.cookies = None
        self.uid = None

    def login(self):
        addr = f"{self.url}/web/session/authenticate"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": self.db,
                "login": self.username,
                "password": self.password
            }
        }
        try:
            res = requests.post(addr, json=payload, timeout=10)
            res.raise_for_status()
            result = res.json().get('result')
            if result:
                self.uid = result.get('uid')
                self.cookies = res.cookies
                return True
        except Exception as e:
            print(f"Login Error: {e}")
        return False

    # def get_users(self):
    #     if not self.cookies:
    #         return []
            
    #     addr = f"{self.url}/web/dataset/call_kw"
    #     payload = {
    #         "jsonrpc": "2.0",
    #         "method": "call",
    #         "params": {
    #             "model": "res.users",
    #             "method": "search_read",
    #             "args": [],
    #             "kwargs": {
    #                 "fields": ["name", "login", "email"],
    #                 "limit": 10
    #             }
    #         }
    #     }
    #     try:
    #         res = requests.post(addr, json=payload, cookies=self.cookies, timeout=10)
    #         return res.json().get('result', [])
    #     except Exception as e:
    #         print(f"Fetch Error: {e}")
    #         return []
    
    def get_users(self):
        if not self.cookies:
            return []
            
        addr = f"{self.url}/web/dataset/call_kw"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "sale.customer",
                "method": "search_read",
                "args": [],
                "kwargs": {
                    "fields": ["name", "phone_number", "note"],
                    "limit": 10
                }
            }
        }
        try:
            res = requests.post(addr, json=payload, cookies=self.cookies, timeout=10)
            return res.json().get('result', [])
        except Exception as e:
            print(f"Fetch Error: {e}")
            return []

def main(page: ft.Page):
    page.title = "Odoo Mobile Bridge"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 1
    page.scroll = ft.ScrollMode.ADAPTIVE

    # Instance Configuration
    odoo = OdooClient("http://192.168.1.194:8069", "Telesales", "admin", "admin")

    # UI Components
    list_view = ft.ListView(expand=True, spacing=10, divider_thickness=1)
    loading_indicator = ft.ProgressBar(visible=False, color="blue")
    
    def show_message(text, is_error=False):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(text),
            bgcolor=ft.Colors.RED_400 if is_error else ft.Colors.GREEN_400
        )
        page.snack_bar.open = True
        page.update()

    def fetch_data(e):
        # 1. Start Loading UI
        sync_button.disabled = True
        loading_indicator.visible = True
        list_view.controls.clear()
        page.update()

        # 2. Perform Logic
        if odoo.login():
            users = odoo.get_users()
            if users:
                for user in users:
                    list_view.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.PERSON_OUTLINE, color="blue"),
                            title=ft.Text(user.get('name', 'Unknown')),
                            subtitle=ft.Text(f"{user.get('phone_number')}")
                        )
                    )
                show_message(f"Fetched {len(users)} users")
            else:
                list_view.controls.append(ft.Text("No data found.", italic=True))
        else:
            show_message("Connection Failed: Check server or credentials", True)

        # 3. Reset UI
        sync_button.disabled = False
        loading_indicator.visible = False
        page.update()

    sync_button = ft.Button(
        "Sync Users", 
        on_click=fetch_data, 
        icon=ft.Icons.SYNC,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )

    # Layout Construction
    page.add(
        ft.Column(
            [
                sync_button,
                loading_indicator,
                list_view
            ],
            expand=True
        )
    )

if __name__ == "__main__":
    ft.run(main)