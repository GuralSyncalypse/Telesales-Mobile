import flet as ft
import asyncio
import threading
import math
import regex as re
import time
from functools import partial

class CustomerFormPage:
    def __init__(self, page, app, customer=None):
        self.page = page
        self.app = app
        self.customer = customer or {}

        self.name = ft.TextField(
            label="Name",
            value=self.customer.get("name", "")
        )

        self.phone = ft.TextField(
            label="Phone",
            value=self.customer.get("phone", "")
        )

        self.email = ft.TextField(
            label="Email",
            value=self.customer.get("email", "")
        )

        self.zalo = ft.TextField(
            label="Zalo",
            value=self.customer.get("zalo", "")
        )

        self.zalo = ft.TextField(
            label="Zalo",
            value=self.customer.get("zalo", "")
        )

        self.types = ft.Dropdown(
            label="Loại Khách",
            options=['Cá nhân', 'Môi giới', 'Nhà đầu tư', 'Doanh nghiệp'],
            value='Cá nhân'
        )


    def save(self, e):
        data = {
            "name": self.name.value,
            "phone": self.phone.value,
            "email": self.email.value,
            "zalo": self.zalo.value,
            "type": self.types.value
        }

        if self.customer:
            self.customer.update(data)
        else:
            data["id"] = len(self.app.customers) + 1
            self.app.customers.append(data)

        self.app.filtered = self.app.customers
        self.app.render_list()

        self.page.views.pop()
        self.page.update()

    def get_view(self):
        return ft.View(
            route="/dashboard/KH/Form",
            controls=[
                ft.AppBar(title=ft.Text("Form KH")),

                ft.Container(
                    padding=20,
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            self.name,
                            self.phone,
                            self.email,
                            self.zalo,
                            self.types,
                            ft.Button("Save", on_click=self.save)
                        ]
                    ),
                )
            ]
        )

class CustomerApp:
    def __init__(self):
        self.items_per_page = 30
        self.page = None
        self.client = None

        self.customers = []
        self.filtered = []
        
        self.current_page = 1
        self.is_paginating = False

        self.is_syncing = False
        self.page_info = ft.Text(size=16, weight=ft.FontWeight.BOLD)
        self.prev_btn = ft.Button("Previous", on_click=self.prev_page)
        self.next_btn = ft.Button("Next", on_click=self.next_page)

        self.list_view = ft.ListView(
            expand=True,
            spacing=8,
            divider_thickness=1,
            padding=ft.padding.symmetric(horizontal=10, vertical=8),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )
        self.search_bar = ft.TextField(
            label="Tìm KH",
            prefix_icon=ft.Icons.SEARCH,
            on_change=lambda e: self.on_search(e.control.value),
            expand=True
        )

    def show_message(self, text, is_error=False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(text),
            bgcolor=ft.Colors.RED_400 if is_error else ft.Colors.GREEN_400,
            duration=1500,
            behavior=ft.SnackBarBehavior.FLOATING
        )
        self.page.show_dialog(self.page.snack_bar) 

    def next_page(self, e):
        if self.is_paginating:
            return

        self.is_paginating = True
        btn = e.control
        btn.disabled = True
        btn.update()

        start = time.perf_counter()

        try:
            self.current_page += 1
            self.update_list()
        finally:
            self.is_paginating = False
            btn.update()

        end = time.perf_counter()
        print(f"next_page took {end - start:.6f} seconds")

    def prev_page(self, e):
        if self.is_paginating:
            return

        self.is_paginating = True
        btn = e.control
        btn.disabled = True
        btn.update()

        start = time.perf_counter()

        try:
            self.current_page -= 1
            self.update_list()
        finally:
            self.is_paginating = False
            btn.update()

        end = time.perf_counter()
        print(f"next_page took {end - start:.6f} seconds")

    def get_view(self, page: ft.Page, back_route="/"):
        self.page = page
        self.client = page.session.store.get("client")
        self.sync_button = ft.IconButton(icon=ft.Icons.REFRESH, on_click=self.fetch_data)

        self.data_view = ft.Column([
            ft.Row([
                self.search_bar,
                self.sync_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.list_view,
        ], expand=True)

        asyncio.create_task(self.fetch_data())

        return ft.View(
            route="/dashboard/KH",
            controls=[
                ft.AppBar(
                    title=ft.Text("Khách Hàng"),
                    leading=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: asyncio.create_task(
                            self.__on_exit(page, back_route)
                        )
                    )
                ),

                ft.Column(
                    [
                        self.data_view,
                        ft.FloatingActionButton(
                            icon=ft.Icons.ADD,
                            on_click=lambda e: self.open_form()
                        )
                    ],
                    expand=True
                ),

                ft.Row(
                    [self.prev_btn, self.page_info, self.next_btn],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            ]
        )
    
    def on_search(self, query):
        query = query.lower()

        self.filtered = [
            c for c in self.customers
            if query in c["name"].lower()
            or query in c["phone"]
        ]

        self.render_list()

    def __build_tile(self, record):
        name = record['name']
        phone = record['phone']
        
        return ft.ListTile(
            leading = ft.Icon(
                ft.Icons.PERSON
            ),
            title=ft.Text(
                f"{name} • {phone}",
                weight=ft.FontWeight.BOLD
            ),
            data=record
        )

    def update_list(self):
        lv = self.list_view

        lv.controls.clear()

        total_filtered = len(self.filtered)
        total_pages = max(1, math.ceil(total_filtered / self.items_per_page))

        # Clamp current page (important after search)
        self.current_page = max(1, min(self.current_page, total_pages))

        start = (self.current_page - 1) * self.items_per_page
        end = start + self.items_per_page

        items = [
            self.__build_tile(item)
            for item in self.filtered[start:end]
        ]

        lv.controls = items        

        # Show "no results"
        if total_filtered == 0:
            lv.controls.append(ft.Text("No results found"))

        # Update pagination info
        self.page_info.value = f"Page {self.current_page} of {total_pages}"

        self.prev_btn.disabled = (self.current_page == 1)
        self.next_btn.disabled = (self.current_page == total_pages)
        
        self.page_info.update()
        lv.update()

    async def fetch_data(self, e=None):
        # # Fake data (replace with API)
        # self.customers = [
        #     {"id": 1, "name": "Alice", "phone": "123"},
        #     {"id": 2, "name": "Bob", "phone": "456"},
        # ]

        # self.filtered = self.customers
        # self.render_list()

        start = time.time()

        # 1. Prevent concurrent runs    
        if not self.client:
            self.show_message("No client!", is_error=True)
            return

        if self.is_syncing:
            self.show_message("Đang đồng bộ, vui lòng chờ!")
            return

        # 2. UI Feedback: Disable button and show loading state
        self.sync_button.disabled = True
        self.sync_button.icon = ft.Icons.HOURGLASS_EMPTY
        self.sync_button.update()
        
        self.is_syncing = True

        try:
            fields = ['name', 'phone', 'email', 'zalo', 'salesperson_id']
            self.customers = await asyncio.to_thread(
                self.client.get_table,
                "sale.customer",
                [],
                fields
            )

            self.filtered = self.customers.copy()
            self.update_list()     
            self.show_message("Synced!")

        except Exception as err:
            self.show_message(f"Lỗi: {str(err)}", is_error=True)

        finally:
            self.is_syncing = False
            self.sync_button.disabled = False
            self.sync_button.icon = ft.Icons.REFRESH
            self.sync_button.update()

    def open_form(self, customer=None):
        self.page.views.append(
            CustomerFormPage(self.page, self, customer).get_view()
        )
        self.page.update()