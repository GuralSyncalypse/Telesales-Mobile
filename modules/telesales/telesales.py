import flet as ft
import asyncio
import threading
import math
import regex as re
from functools import partial
import time

class TelesalesApp:
    protocol = 'https'

    def __init__(self):
        # Số phần tử trong 1 trang.
        self.items_per_page = 20

        self.page_info = ft.Text(size=16, weight=ft.FontWeight.BOLD)
        self.prev_btn = ft.Button("Previous", on_click=self.prev_page)
        self.next_btn = ft.Button("Next", on_click=self.next_page)
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
        self.not_called_lv = None
        self.called_lv = None
        self.unreachable_lv = None
        
        self.filtered = []
        self.client = None
        self.phonebook = {
            'called': [],
            'not_called': [],
            'unreachable': []
        }

    def __get_list_in_use(self):
        lists = [
            self.not_called_lv,
            self.called_lv,
            self.unreachable_lv
        ]
        return lists[self.list_in_use]

    def __get_data_source(self):
        source = [
            self.phonebook['not_called'],
            self.phonebook['called'],
            self.phonebook['unreachable']
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

        # Show "no results"
        if total_filtered == 0:
            lv.controls.append(ft.Text("No results found"))

        # Update pagination info
        self.page_info.value = f"Page {self.current_page} of {total_pages}"
        print(self.page_info.value)
        self.prev_btn.disabled = (self.current_page == 1)
        self.next_btn.disabled = (self.current_page == total_pages)

        self.refresh_counters(use_ui_counts=True)
        
        self.page_info.update()
        lv.update()       

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

    def __on_search(self, query: str):
        # Define a helper to check matches to avoid repeating code
        def matches_query(item):
            text = f"{item['customer_id'][1]} • {item['phone_number']}".lower()
            return re.search(pattern, text) is not None

        query = query.lower()
        self.filtered = []
        source = self.__get_data_source()

        # Create a regex pattern: 
        # ^ matches start of string
        # | is 'OR'
        # •\s+ matches the dot separator and the space
        # re.escape ensures dots/pluses in query don't break regex
        pattern = rf"(^|•\s+){re.escape(query)}"
        
        
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
                "not_called": len(self.not_called_lv.controls),
                "called": len(self.called_lv.controls),
                "unreachable": len(self.unreachable_lv.controls)
            }
        else:
            counts = {
                "not_called": len(self.phonebook['not_called']),
                "called": len(self.phonebook['called']),
                "unreachable": len(self.phonebook['unreachable'])
            }
        
        # Labels configuration to avoid repeating index logic
        labels = [
            f"Chưa gọi ({counts['not_called']})",
            f"Đã gọi ({counts['called']})",
            f"Không gọi được ({counts['unreachable']})"
        ]

        # Update the actual Tab objects
        tabs_list = self.tabs.content.controls[0].tabs
        for i, label in enumerate(labels):
            tabs_list[i].label = label
            tabs_list[i].update()

    def on_tab_change(self, e):
        self.list_in_use = e.control.selected_index
        self.filtered = self.__get_data_source().copy()
        self.update_list()

    def __build_tabs(self):
        if not self.not_called_lv:
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

            self.unreachable_lv = ft.ListView(
                expand=True,
                spacing=10,
                divider_thickness=1
            )
            
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
                            ft.Tab(label="Không gọi được")
                        ],
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            self.not_called_lv,
                            self.called_lv,
                            self.unreachable_lv
                        ],
                    ),
                ],
            ),
        )

        return tabs

    def __build_tile(self, record):
        customer_data = record.get("customer_id")
        name = customer_data[1] if isinstance(customer_data, (list, tuple)) else "Unknown Customer"

        phone = record.get("phone_number", "No Phone")
        is_called = record.get("is_called")
        unreachable = record.get("unreachable")

        
        call_btn = ft.IconButton(
            icon=ft.Icons.PHONE,
            icon_color=ft.Colors.GREEN, # Use ft.Colors for better IDE intellisense
            tooltip="Call Customer",
            on_click=partial(self.make_call, phone_number=phone)
        ) 

        switch_btn = ft.IconButton(
            icon=ft.Icons.ARROW_BACK if is_called else ft.Icons.ARROW_FORWARD,
            icon_color=ft.Colors.BLUE,
            data=record,
            on_click=self.__toggle_call_status
        )

        buttons = [call_btn, switch_btn]

        if is_called:
            buttons.append(
                ft.IconButton(
                    icon=ft.Icons.CANCEL,
                    icon_color=ft.Colors.BLUE,
                    data=record,
                    on_click=self.__cancel_number
                )
            )
        
        if unreachable:
            buttons = []

        return ft.ListTile(
            leading = ft.Icon(
                ft.Icons.PERSON,
                color=ft.Colors.ON_SURFACE_VARIANT if is_called else ft.Colors.PRIMARY
            ),
            title=ft.Text(
                f"{name} • {phone}",
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.ON_SURFACE if not is_called else ft.Colors.ON_SURFACE_VARIANT,
                spans=[ft.TextSpan(style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH))] if is_called else []
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
            )
        )

    def show_message(self, text, is_error=False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(text),
            bgcolor=ft.Colors.RED_400 if is_error else ft.Colors.GREEN_400,
            duration=1500,
            behavior=ft.SnackBarBehavior.FLOATING
        )
        self.page.show_dialog(self.page.snack_bar) 

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

        asyncio.create_task(self.fetch_data())

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
        """
        Handles the UI transition and logic for editing a note within a ListView.
        """
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
                self.show_message("Note updated!")
                restore_ui()

            except Exception as err:
                self.show_message(f"Update failed: {str(err)}", is_error=True)
                save_btn.disabled = False
                note_field.disabled = False
                parent.update()

        # 3. Component Construction
        note_field = ft.TextField(
            value=record.get("note") or "",
            label="Edit Note",
            multiline=True,
            expand=True,
            min_lines=1,    # Shows 3 lines of space immediately
            max_lines=3,   # Stops growing after 10 lines
            autofocus=True
        )

        save_btn = ft.IconButton(icon=ft.Icons.SAVE, tooltip="Save", disabled=False, on_click=handle_save)
        cancel_btn = ft.IconButton(icon=ft.Icons.CANCEL, tooltip="Cancel", on_click=lambda _: restore_ui())

        # 4. UI Swap
        controls_list[idx] = ft.Row([note_field, save_btn, cancel_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        parent.update()
           

    def __toggle_call_status(self, e):
        def __update_call_status(record):
            success = self.client.update_field(
                model="sale.phonebook",
                record_id=record["id"],
                field_name="is_called",
                new_value=record["is_called"]
            )

            if not success:
                print("API failed!")

        start = time.perf_counter()

        record = e.control.data
        # Determine direction based on current status
        is_called = record.get("is_called")
        
        # Define source/destination keys
        src_key = 'called' if is_called else 'not_called'
        dst_key = 'not_called' if is_called else 'called'

        # 🔹 Find ListTile container
        tile = e.control
        while tile and not isinstance(tile, ft.ListTile):
            tile = tile.parent
        if not tile: return

        # Update Data state
        record["is_called"] = not is_called
        self.phonebook[src_key].remove(record)
        self.phonebook[dst_key].append(record)


        # Refresh UI
        self.filtered = self.__get_data_source().copy()
        self.update_list()
        
        self.show_message(f"Moved to {dst_key.replace('_', ' ').title()}!")

        end = time.perf_counter()

        threading.Thread(
            target=__update_call_status,
            args=(record,)
        ).start()

        print(f"Elapsed time: {end - start:.6f} seconds")

    def __cancel_number(self, e):
        def on_cancel(record):
            success = self.client.update_field(
                model="sale.phonebook",
                record_id=record["id"],
                field_name="unreachable",
                new_value=record["unreachable"]
            )

            if not success:
                print("API failed!")

        def undo(ev):
            record["unreachable"] = prev_unreachable

            # Move lại list cũ
            if record in self.phonebook['unreachable']:
                self.phonebook['unreachable'].remove(record)
                self.phonebook['is_called'].append(record)

            self.update_list()

        start = time.perf_counter()
    
        record = e.control.data
        # Determine direction based on current status
        prev_unreachable = record.get("unreachable")
        unreachable = record.get("unreachable")

        # 🔹 Find ListTile container
        tile = e.control
        while tile and not isinstance(tile, ft.ListTile):
            tile = tile.parent
        if not tile: return

        # Update Data state
        record["unreachable"] = not unreachable
        self.phonebook['called'].remove(record)
        self.phonebook['unreachable'].append(record)

        tile.trailing.controls = []
        tile.on_click = None

        # Refresh UI
        self.filtered = self.__get_data_source().copy()
        self.update_list()
        
        self.show_message(f"Canceled!")

        end = time.perf_counter()

        threading.Thread(
            target=on_cancel,
            args=(record,)
        ).start()

        print(f"Elapsed time: {end - start:.6f} seconds")

    async def __on_exit(self, page : ft.Page, backroute):
        self.phonebook = {
            'called': [],
            'not_called': [],
            'unreachable': []
        }

        self.called_lv.controls.clear()
        self.not_called_lv.controls.clear()
        self.unreachable_lv.controls.clear()
        self.is_editing = False
        self.is_syncing = False
    
        await page.push_route(backroute)

    async def make_call(self, e, phone_number):
        await self.url_launcher.launch_url(f"tel:{phone_number}", )

    def _get_phonebook_task(self, domain):
        required_fields = [
            'customer_id',
            'phone_number',
            'is_called',
            'unreachable',
            'note'
        ]

        return asyncio.to_thread(
            self.client.get_table,
            "sale.phonebook",
            domain,
            required_fields
        )

    async def fetch_data(self, e=None):
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
            required_fields = ['customer_id', 'phone_number', 'is_called', 'unreachable', 'note']
            called_task = asyncio.to_thread(
                self.client.get_table,
                "sale.phonebook",
                [("is_called", "=", True), ("unreachable", "=", False)],
                required_fields
            )

            not_called_task = asyncio.to_thread(
                self.client.get_table,
                "sale.phonebook",
                [("is_called", "=", False)],
                required_fields
            )

            # 2. Run them concurrently
            # This returns a list containing the results of both calls in order
            self.phonebook['called'], self.phonebook['not_called']= await asyncio.gather(
                called_task,
                not_called_task
            )   

            self.filtered = self.__get_data_source().copy()
            self.update_list()     
            self.show_message("Synced!")

        except Exception as err:
            self.show_message(f"Lỗi: {str(err)}", is_error=True)

        finally:
            self.is_syncing = False
            self.sync_button.disabled = False
            self.sync_button.icon = ft.Icons.REFRESH
            self.sync_button.update()