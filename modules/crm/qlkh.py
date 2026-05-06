from core.utils import Utils
import flet as ft
import asyncio, threading
import math
import regex as re
import time

class CustomerFormPage:
    def __init__(self, page : ft.Page, app, customer=None):
        self.page = page
        self.app = app
        self.customer = customer or {}

        # ===== INPUTS =====
        self.name = ft.TextField(
            label="Họ và tên",
            hint_text="Nhập tên khách hàng",
            value=self.customer.get("name", ""),
            autofocus=True,
        )

        self.phone = ft.TextField(
            label="Số điện thoại",
            hint_text="VD: 0901234567",
            value=self.customer.get("phone", ""),
            keyboard_type=ft.KeyboardType.PHONE,
        )

        self.email = ft.TextField(
            label="Email",
            hint_text="example@gmail.com",
            value=self.customer.get("email", ""),
            keyboard_type=ft.KeyboardType.EMAIL,
        )

        self.sources = ft.Dropdown(
            label="Từ Nguồn",
            options=[],
            value=self.customer.get("source", "other")
        )

        self.types = ft.Dropdown(
            label="Phân Loại",
            options=[],
            value=self.customer.get("type", "individual"),
        )

        self.states = ft.Dropdown(
            label="Trạng Thái",
            options=[],
            value=self.customer.get("type", "active"),
        )

        # ===== BUTTON =====
        self.save_btn = ft.Button(
            content="Lưu khách hàng",
            icon=ft.Icons.SAVE,
            on_click=self.save,
            style=ft.ButtonStyle(
                padding=15,
            ),
        )

        # store selected project ids
        self.selected_projects = set(self.customer.get("project_ids", []))

        # build checkbox list
        self.project_checkboxes = ft.Column(
            spacing=5,
            height=150,
            scroll=ft.ScrollMode.AUTO
        )

        self.__load_projects()
        self.__load_types()
        self.__load_sources()
        self.__load_states()


    def __load_projects(self):
        projects = self.app.projects  # or from Odoo

        self.project_checkboxes.controls = [
            ft.Checkbox(
                label=p["name"],
                value=p["id"] in self.selected_projects,
                on_change=lambda e, pid=p["id"]: self.toggle_project(pid, e.control.value)
            )
            for p in projects
        ]
    
    def __load_types(self):
        types = self.app.types

        self.types.options = [
            ft.DropdownOption(
                key=key,
                text=label
            )
            for key, label in types
        ]

    def __load_sources(self):
        sources = self.app.sources

        self.sources.options = [
            ft.DropdownOption(
                key=key,
                text=label
            )
            for key, label in sources
        ]

    def __load_states(self):
        states = self.app.states

        self.states.options = [
            ft.DropdownOption(
                key=key,
                text=label
            )
            for key, label in states
        ]    
    
    def toggle_project(self, project_id, checked):
        if checked:
            self.selected_projects.add(project_id)
        else:
            self.selected_projects.discard(project_id)

    # ===== VALIDATION =====
    def validate(self):
        if not self.name.value.strip():
            self.name.error = "Tên không được để trống"
            return False
        self.name.error = None
        return True

    # ===== SAVE =====
    def __build_payload(self):
        return {
            "name": self.name.value,
            "phone": self.phone.value,
            "email": self.email.value,
            "type": self.types.value,
            "state": self.states.value,
            "project_ids": list(self.selected_projects)
        }

    def save_customer(self, data):
        if self.customer:
            return self.app.client.update_record(
                model="sale.customer",
                record_id=self.customer['id'],
                values=data
            )
        else:
            return self.app.client.create_record(
                model="sale.customer",
                values=data
            )

    def save(self, e):
        if not self.validate():
            self.page.update()
            return

        data = self.__build_payload()
        
        if self.customer:
            self.customer.update(data)
            data['project_ids'] = [(6, 0, list(self.selected_projects))]
            success = self.app.client.update_record(
                model="sale.customer",
                record_id=self.customer['id'],
                values=data
            )
            if not success:
                raise Exception("API rejected update")
        else:
            data["id"] = len(self.app.customers) + 1
            self.app.customers.append(data)
            success = self.app.client.create_record(
                model="sale.customer",
                values=data
            )
            if not success:
                raise Exception("API rejected update")
       

        Utils.show_message(self.page, "Saved!")
        self.app.filtered = self.app.customers
        self.app.update_list()

        self.page.views.pop()
        self.page.update()

    # ===== VIEW =====
    def get_view(self):
        return ft.View(
            route="/dashboard/KH/Form",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.START,
            controls=[
                ft.AppBar(title=ft.Text("Khách hàng")),

                ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Card(
                            elevation=3,
                            content=ft.Container(
                                width=500,
                                padding=20,
                                content=ft.Column(
                                    spacing=15,
                                    controls=[
                                        ft.Text(
                                            "Thông tin khách hàng",
                                            size=18,
                                            weight=ft.FontWeight.BOLD,
                                        ),

                                        self.name,
                                        self.phone,
                                        self.email,
                                        self.types,
                                        self.sources,

                                        ft.Text("Dự án quan tâm", weight=ft.FontWeight.BOLD),
                                        self.project_checkboxes,

                                        ft.Divider(),

                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.END,
                                            controls=[self.save_btn],
                                        ),
                                    ],
                                ),
                            ),
                        )
                    ],
                ),
            ],
        )

class CustomerApp:
    def __init__(self):
        self.items_per_page = 30
        self.page = None
        self.client = None
        self.projects = []
        self.types = []
        self.sources = []

        self.customers = []
        self.filtered = []
        
        self.current_page = 1
        self.is_paginating = False

        self.is_syncing = False
        self.page_info = ft.Text(size=16, weight=ft.FontWeight.BOLD)
        self.prev_btn = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            tooltip="Previous",
            on_click=self.prev_page
        )

        self.next_btn = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD,
            tooltip="Next",
            on_click=self.next_page
        )

        self.list_view = ft.ListView(
            expand=True,
            spacing=8,
            divider_thickness=1,
            padding=ft.Padding.symmetric(horizontal=10, vertical=8),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )
        self.search_bar = ft.TextField(
            label="Tìm KH",
            prefix_icon=ft.Icons.SEARCH,
            on_change=lambda e: self.on_search(e.control.value),
            expand=True
        )

    async def __on_exit(self, backroute):
        self.customers = []
        self.filtered = []
        
        self.list_view.controls.clear()
        self.is_syncing = False
       
        self.update_list()
        await self.page.push_route(backroute)

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

        return ft.View(
            route="/dashboard/KH",
            controls=[
                ft.AppBar(
                    title=ft.Text("Khách Hàng"),
                    leading=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: asyncio.create_task(
                            self.__on_exit(back_route)
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
        def matches_query(item):
            text = f"{item['name']}".lower()
            return re.search(pattern, text) is not None

        query = query.lower()
        pattern = re.compile(rf"(^|\s){re.escape(query)}", re.IGNORECASE)

        source = self.customers.copy()
        if query == "":
            self.filtered = source
        else:
            self.filtered = [
                item for item in source
                if matches_query(item)
            ]


        self.current_page = 1
        self.update_list()

    def __build_tile(self, record):
        name = record['name']
        phone = record['phone']
        customer_type = record.get('type', '')
        projects = record.get('project_ids', [])

        return ft.ListTile(
            leading=ft.Icon(
                ft.Icons.PERSON,
                size=20,
                color=ft.Colors.PRIMARY
            ),

            title=ft.Text(
                name,
                weight=ft.FontWeight.BOLD
            ),

            subtitle=ft.Text(
                f"{phone} • {customer_type} • {len(projects)} projects"
            ),

            data=record,
            on_click=self.open_form
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
        if getattr(self, "_loading", False):
            return

        start = time.time()

        # 1. Prevent concurrent runs    
        if not self.client:
            Utils.show_message(self.page, "No client!", is_error=True)
            return

        if self.is_syncing:
            Utils.show_message(self.page, "Đang đồng bộ, vui lòng chờ!")
            return

        # 2. UI Feedback: Disable button and show loading state
        self.sync_button.disabled = True
        self.sync_button.icon = ft.Icons.HOURGLASS_EMPTY
        self.sync_button.update()
        
        self.is_syncing = True

        self._loading = True
        try:
            fields = ['name', 'phone', 'email', 'salesperson_id', 'source', 'type', 'state', 'project_ids']
            self.customers = await asyncio.to_thread(
                self.client.get_table,
                "sale.customer",
                [],
                fields
            )

            self.projects = await asyncio.to_thread(
                self.client.get_table,
                "estate.project",
                [],
                ['name', 'investor', 'location']
            )

            if not self.types:
                self.types = await asyncio.to_thread(
                    self.client.get_selection,
                    "sale.customer",
                    'type'
                )

            if not self.sources:
                self.sources = await asyncio.to_thread(
                    self.client.get_selection,
                    "sale.customer",
                    'source'
                )

            if not self.states:
                self.states = await asyncio.to_thread(
                    self.client.get_selection,
                    "sale.customer",
                    'state'
                )

            self.filtered = self.customers.copy()
            self.update_list()     
            Utils.show_message(self.page, "Synced!")

        except Exception as err:
            Utils.show_message(self.page, f"Lỗi: {str(err)}", is_error=True)

        finally:
            self._loading = False
            self.is_syncing = False
            self.sync_button.disabled = False
            self.sync_button.icon = ft.Icons.REFRESH
            self.sync_button.update()

    def open_form(self, e=None, customer : dict = {}):
        if e != None:
            customer = e.control.data
        self.page.views.append(
            CustomerFormPage(self.page, self, customer).get_view()
        )
        self.page.update()