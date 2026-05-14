from core.utils import Utils
import asyncio, threading
import math
import time
import regex as re
import flet as ft
import datetime
from functools import partial

class TelesalesApp:
    def __init__(self):
        # Số phần tử trong 1 trang.
        self.items_per_page = 20

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
        self.list_in_use = 0
        self.current_page = 1
        self.is_paginating = False

        self.is_syncing = False
        self.is_editing = False

        self.search_bar = ft.TextField(
            label="Search contacts",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            on_change=lambda e: self.__on_search(e.control.value),
        )
        
        # List Views
        self.not_called_lv = ft.ListView(
            expand=True,
            spacing=10,
            divider_thickness=1
        )

        self.called_lv = ft.ListView(
            expand=True,
            spacing=10,
            divider_thickness=1
        )

        self.cancel_lv = ft.ListView(
            expand=True,
            spacing=10,
            divider_thickness=1
        )


        self.filtered = []
        self.client = None
        self.phonebook = {
            'called': [],
            'new': [],
            'invalid': []
        }

    def __get_list_in_use(self):
        lists = [
            self.not_called_lv,
            self.called_lv,
            self.cancel_lv
        ]
        return lists[self.list_in_use]

    def __get_data_source(self):
        source = [
            self.phonebook['new'],
            self.phonebook['called'],
            self.phonebook['invalid']
        ]
        return source[self.list_in_use]

    def update_list(self):
        lv = self.__get_list_in_use()

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

        # Update pagination info
        self.page_info.value = f"Page {self.current_page} of {total_pages}"

        self.prev_btn.disabled = (self.current_page == 1)
        self.next_btn.disabled = (self.current_page == total_pages)

        self.refresh_counters(use_ui_counts=True)
        
        self.page_info.update()
        lv.update()       

    def __paginate(self, e, delta: int):
        if self.is_paginating:
            return

        self.is_paginating = True
        btn = e.control
        btn.disabled = True
        btn.update()

        start = time.perf_counter()

        try:
            self.current_page += delta
            self.update_list()
        finally:
            self.is_paginating = False
            btn.update()

        end = time.perf_counter()
        print(f"paginate took {end - start:.6f} seconds")

    def next_page(self, e):
        self.__paginate(e, 1)

    def prev_page(self, e):
        self.__paginate(e, -1)

    async def __on_exit(self, page : ft.Page, backroute):
        self.called_lv.controls.clear()
        self.not_called_lv.controls.clear()
        self.is_editing = False
        self.is_syncing = False
    
        await page.push_route(backroute)

    def __on_search(self, query: str):
        # Define a helper to check matches to avoid repeating code
        def matches_query(item):
            text = f"{item['name']} • {item['phone']}".lower()
            return re.search(pattern, text) is not None

        query = query.lower()
        self.filtered = []
        source = self.__get_data_source()

        # Create a regex pattern: 
        # ^ matches start of string
        # | is 'OR'
        # •\s+ matches the dot separator and the space
        # re.escape ensures dots/pluses in query don't break regex
        pattern = rf"\b{re.escape(query)}"
        
        
        # Filters
        if query == "":
            self.filtered = source
        else:
            self.filtered = [
                item for item in source
                if matches_query(item)
            ]
        
        self.current_page = 1
        self.update_list()
          
    def refresh_counters(self, use_ui_counts=False):
        """
        Updates tab labels. 
        If use_ui_counts is True, it counts active UI widgets.
        Otherwise, it counts items in the phonebook data.
        """
        if use_ui_counts:
            counts = {
                "new": len(self.not_called_lv.controls),
                "called": len(self.called_lv.controls),
                "invalid": len(self.cancel_lv.controls)
            }
        else:
            counts = {
                "new": len(self.phonebook['new']),
                "called": len(self.phonebook['called']),
                "invalid": len(self.phonebook['invalid'])
            }
        
        # Labels configuration to avoid repeating index logic
        labels = [
            f"Chưa gọi ({counts['new']})",
            f"Đã gọi ({counts['called']})",
            f"Đã hủy ({counts['invalid']})"
        ]

        # Update the actual Tab objects
        tabs_list = self.tabs.content.controls[0].tabs
        for i, label in enumerate(labels):
            tabs_list[i].label = label
            tabs_list[i].update()

    def on_tab_change(self, e):
        self.is_editing = False

        self.list_in_use = e.control.selected_index
        self.__on_search(self.search_bar.value)
        
        self.update_list()

    def __build_tabs(self):
        tabs = ft.Tabs(
            selected_index=0,
            on_change=self.on_tab_change,
            length=3,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Chưa gọi"),
                            ft.Tab(label="Đã gọi"),
                            ft.Tab(label="Hủy")
                        ],
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            self.not_called_lv,
                            self.called_lv,
                            self.cancel_lv
                        ],
                    ),
                ],
            ),
        )

        return tabs

    def __build_tile(self, record):
        name = record.get("name", "Không tên")

        phone = record.get("phone", "Không SĐT")
        status = record.get("status")
        created_on = record.get("created_on")
        is_new = False

        if created_on:
            if isinstance(created_on, str):
                created_dt = datetime.datetime.fromisoformat(created_on)
            else:
                created_dt = created_on

            is_new = created_dt >= (datetime.datetime.now() - datetime.timedelta(hours=24))
        
        call_btn = ft.IconButton(
            icon=ft.Icons.PHONE,
            icon_color=ft.Colors.GREEN, # Use ft.Colors for better IDE intellisense
            tooltip="Gọi",
            on_click=partial(self.make_call, phone=phone)
        ) 

        switch_btn = ft.IconButton(
            icon=ft.Icons.ARROW_BACK if status == 'called' else ft.Icons.ARROW_FORWARD,
            icon_color=ft.Colors.BLUE,
            data=record,
            on_click=self.__toggle_call_status
        )

        buttons = [call_btn, switch_btn]

        if status == 'called':
            buttons.append(
                ft.IconButton(
                    icon=ft.Icons.CANCEL,
                    icon_color=ft.Colors.BLUE,
                    data=record,
                    on_click=self.__move_to_invalid
                )
            )
        
        if status == 'invalid':
            buttons = []

        return ft.ListTile(
            leading = ft.Icon(
                ft.Icons.PERSON,
                color=ft.Colors.ON_SURFACE_VARIANT if status == 'called' else ft.Colors.PRIMARY
            ),
            title=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.NEW_RELEASES,
                        size=16,
                        color=ft.Colors.DEEP_ORANGE,
                    ) if is_new else ft.Container(),

                    ft.Text(
                        f"{name} • {phone}",
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_SURFACE if status != 'called' else ft.Colors.ON_SURFACE_VARIANT,
                        spans=[
                            ft.TextSpan(
                                style=ft.TextStyle(
                                    decoration=ft.TextDecoration.LINE_THROUGH
                                )
                            )
                        ] if status == 'called' else []
                    )
                ],
                spacing=6,
            ),
            subtitle=ft.Text(
                f"Note: {record.get('note') or 'No notes'}",
                italic=True,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS
            ),
            data=record,
            on_click=self.edit_note,
            trailing=ft.Row(
                controls=buttons,
                tight=True,
                spacing=0, # Keeps buttons close together
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            shape=ft.RoundedRectangleBorder(radius=10)
        )

    def get_view(self, page: ft.Page, back_route="/"):
        self.page = page
        self.client = page.session.store.get("client")

        # Needed for calling
        self.url_launcher = ft.UrlLauncher()
    
        self.sync_button = ft.IconButton(icon=ft.Icons.REFRESH, on_click=self.fetch_data)

        self.tabs = self.__build_tabs()

        self.data_view = ft.Column([
            ft.Row([
                self.search_bar,
                self.sync_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.tabs
        ], expand=True, visible=True)

        return ft.View(
            route=f"/dashboard/marketing/telesales",
            controls=[
                ft.AppBar(
                    title=ft.Text(
                        "Telesales",
                        color=ft.Colors.ON_PRIMARY
                    ),
                    leading=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color=ft.Colors.ON_PRIMARY, 
                        on_click=lambda e: asyncio.create_task(
                            self.__on_exit(page, back_route)
                        )
                    ),
                    bgcolor=ft.Colors.PRIMARY,
                ),
                ft.Column(
                    [
                        self.data_view
                    ],
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    [self.prev_btn, self.page_info, self.next_btn],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            ],
        )
        
    def edit_note(self, e):
        def validate(e=None):
            if note_field.value == record.get("note", ""):
                save_btn.disabled = True
            else:
                save_btn.disabled = False

        def update_note(record):
            success = self.client.update_field(
                model="sale.phonebook",
                record_id=record["id"],
                field_name="note",
                new_value=record["note"]
            )

            if not success:
                raise Exception("API rejected update")

        if self.is_editing:
            return

        # 1. Context Extraction
        original_tile = e.control
        record = original_tile.data
        
        # Locate parent ListView
        parent = original_tile.parent
        while parent and not isinstance(parent, ft.ListView):
            parent = parent.parent
        
        if not parent:
            return

        self.is_editing = True
        self.is_valid = False
        controls_list = parent.controls
        idx = controls_list.index(original_tile)

        # 2. Define Sub-actions
        def restore_ui():
            self.is_editing = False
            controls_list[idx] = original_tile
            parent.update()

        def handle_save(ev):
            save_btn.disabled = True
            note_field.disabled = True

            try:
                record["note"] = note_field.value

                threading.Thread(
                    target=update_note,
                    args=(record,)
                ).start()

                original_tile.subtitle = ft.Text(f"Note: {record["note"] or 'No notes'}", italic=True)
                Utils.show_message(self.page, "Note updated!")
                restore_ui()

            except Exception as err:
                Utils.show_message(self.page, f"Update failed: {str(err)}", is_error=True)
                save_btn.disabled = False
                note_field.disabled = False
                parent.update()

        # 3. Component Construction
        note_field = ft.TextField(
            value=record.get("note") or "",
            label="Edit Note",
            multiline=True,
            expand=True,
            min_lines=1,
            max_lines=3,
            autofocus=True,
            on_change=validate
        )

        save_btn = ft.IconButton(icon=ft.Icons.SAVE, tooltip="Save", disabled=True, on_click=handle_save)
        cancel_btn = ft.IconButton(icon=ft.Icons.CANCEL, tooltip="Cancel", on_click=lambda _: restore_ui())

        # 4. UI Swap
        controls_list[idx] = ft.Row([note_field, save_btn, cancel_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        parent.update()
           
    def __toggle_call_status(self, e):
        def __update_call_status(record):
            success = self.client.update_field(
                model="sale.phonebook",
                record_id=record["id"],
                field_name="status",
                new_value=record["status"]
            )

            if not success:
                print("API failed!")

        start = time.perf_counter()

        record = e.control.data
        # Determine direction based on current status
        status = record.get("status")
        
        # Define source/destination keys
        src_key = 'called' if status == 'called' else 'new'
        dst_key = 'new' if status == 'called' else 'called'

        # 🔹 Find ListTile container
        tile = e.control
        while tile and not isinstance(tile, ft.ListTile):
            tile = tile.parent
        if not tile: return

        # Update Data status
        record["status"] = 'called' if status == 'new' else 'new'
        self.phonebook[src_key].remove(record)
        self.phonebook[dst_key].append(record)


        # Refresh UI
        self.filtered = self.__get_data_source().copy()
        self.update_list()
        
        Utils.show_message(self.page, f"Moved to {dst_key.replace('_', ' ').title()}!")

        end = time.perf_counter()

        threading.Thread(
            target=__update_call_status,
            args=(record,)
        ).start()

        print(f"Elapsed time: {end - start:.6f} seconds")

    def __move_to_invalid(self, e):
        def move(record):
            success = self.client.update_field(
                model="sale.phonebook",
                record_id=record["id"],
                field_name="status",
                new_value=record["status"]
            )

            if not success:
                print("API failed!")

        start = time.perf_counter()
    
        record = e.control.data

        # 🔹 Find ListTile container
        tile = e.control
        while tile and not isinstance(tile, ft.ListTile):
            tile = tile.parent
        if not tile: return

        # Update Data status
        record["status"] = 'invalid'
        self.phonebook['called'].remove(record)
        self.phonebook['invalid'].append(record)

        tile.trailing.controls = []
        tile.on_click = None

        # Refresh UI
        self.filtered = self.__get_data_source().copy()
        self.update_list()
        
        Utils.show_message(self.page, f"Canceled!")

        end = time.perf_counter()

        threading.Thread(
            target=move,
            args=(record,)
        ).start()

        print(f"Elapsed time: {end - start:.6f} seconds")

    async def make_call(self, e, phone):
        await self.url_launcher.launch_url(f"tel:{phone}", )

    async def fetch_data(self, e=None):
        if getattr(self, "_loading", False):
            self.update_list()
            return

        # 1. Prevent concurrent runs    
        if not self.client:
            Utils.show_message(self.page, "No client!", is_error=True)
            return

        if self.is_syncing:
            Utils.show_message(self.page, "Đang đồng bộ, vui lòng chờ!")
            return

        # 2. UI Feedback: Disable button and show loading status
        self.sync_button.disabled = True
        self.sync_button.icon = ft.Icons.HOURGLASS_EMPTY
        self.sync_button.update()
        
        self.is_syncing = True
        self._loading = True
        try:
            required_fields = ['created_on', 'name', 'phone', 'status', 'note']
            called_task = asyncio.to_thread(
                self.client.get_table,
                "sale.phonebook",
                [("status", "=", 'called')],
                required_fields
            )

            not_called_task = asyncio.to_thread(
                self.client.get_table,
                "sale.phonebook",
                [("status", "=", 'new')],
                required_fields
            )

            # 2. Run them concurrently
            # This returns a list containing the results of both calls in order
            self.phonebook['called'], self.phonebook['new']= await asyncio.gather(
                called_task,
                not_called_task
            )   

            self.filtered = self.__get_data_source().copy()
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