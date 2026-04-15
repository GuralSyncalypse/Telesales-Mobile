import flet as ft
import asyncio
import threading
from functools import partial
import time

class TelesalesApp:
    protocol = 'https'

    def __init__(self):
        self.is_syncing = False
        self.is_editing = False

        self.not_called_lv = None
        self.called_lv = None
        self.unreachable_lv = None
        
        self.client = None
        self.phonebook = {
            'called': [],
            'not_called': [],
            'unreachable': []
        }

    def refresh_counters(self):
        # 1. Update the Data Counts
        not_called_count = len(self.phonebook['not_called'])
        called_count = len(self.phonebook['called'])
        unreachable = len(self.phonebook['unreachable'])

        # 2. Update the actual Tab objects
        self.tabs.content.controls[0].tabs[0].label = f"Chưa gọi ({not_called_count})"
        self.tabs.content.controls[0].tabs[1].label = f"Đã gọi ({called_count})"
        self.tabs.content.controls[0].tabs[2].label = f"Không gọi được ({unreachable})"

        for i in range(0, 3):
            self.tabs.content.controls[0].tabs[i].update()

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
            bgcolor=ft.Colors.RED_400 if is_error else ft.Colors.GREEN_400
        )
        self.page.show_dialog(self.page.snack_bar) 

    def get_view(self, page: ft.Page, back_route="/"):
        # Page
        self.page = page
        self.client = page.session.store.get("client")

        # Needed for calling
        self.url_launcher = ft.UrlLauncher()
    
        self.sync_button = ft.IconButton(icon=ft.Icons.REFRESH, on_click=self.fetch_data)
        # self.save_button = ft.IconButton(
        #     icon=ft.Icons.SAVE,
        #     tooltip="Save changes",
        #     on_click=self.save_data
        # )


        self.tabs = self.__build_tabs()

        self.data_view = ft.Column([
            ft.Row([
                ft.Text("Danh sách SĐT", size=20, weight=ft.FontWeight.W_500),
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
            parent.update()

            try:
                record["note"] = note_field.value.strip()

                threading.Thread(
                    target=update_note,
                    args=(record,)
                ).start()

                original_tile.subtitle = ft.Text(f"Note: {record["note"] or 'No notes'}")
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
            autofocus=True,
            on_change=lambda _: setattr(save_btn, "disabled", note_field.value == (record.get("note") or "")) or parent.update()
        )

        save_btn = ft.IconButton(icon=ft.Icons.SAVE, tooltip="Save", disabled=True, on_click=handle_save)
        cancel_btn = ft.IconButton(icon=ft.Icons.CANCEL, tooltip="Cancel", on_click=lambda _: restore_ui())

        # 4. UI Swap
        controls_list[idx] = ft.Row([note_field, save_btn, cancel_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        parent.update()
           

    def __toggle_call_status(self, e):
        """Toggles a record between 'Called' and 'Not Called' states"""
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
        
        # Define source/destination ListViews
        src_lv = self.called_lv if is_called else self.not_called_lv
        dst_lv = self.not_called_lv if is_called else self.called_lv

        # 🔹 Find ListTile container
        tile = e.control
        while tile and not isinstance(tile, ft.ListTile):
            tile = tile.parent
        if not tile: return

        # Update Data state
        record["is_called"] = not is_called
        self.phonebook[src_key].remove(record)
        self.phonebook[dst_key].append(record)

        

        # Move UI components
        src_lv.controls.remove(tile)
        dst_lv.controls.append(self.__build_tile(record))

        # Refresh UI
        src_lv.update()
        dst_lv.update()
        self.refresh_counters()
        
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

        start = time.perf_counter()

        record = e.control.data
        # Determine direction based on current status
        unreachable = record.get("unreachable")
        
        # Define source/destination ListViews
        src_lv = self.called_lv
        dst_lv = self.unreachable_lv

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

        # Move UI components
        src_lv.controls.remove(tile)
        dst_lv.controls.append(tile) # No need function

        # Refresh UI
        src_lv.update()
        dst_lv.update()

        print("X")
        self.refresh_counters()
        
        self.show_message(f"Canceled!")

        end = time.perf_counter()

        threading.Thread(
            target=on_cancel,
            args=(record,)
        ).start()

        print(f"Elapsed time: {end - start:.6f} seconds")


    async def __on_exit(self, page : ft.Page, backroute):
        #self.phonebook = []
        self.is_editing = False
        self.is_syncing = False

        await page.push_route(backroute)

    async def make_call(self, e, phone_number):
        await self.url_launcher.launch_url(f"tel:{phone_number}", )

    async def fetch_data(self, e):
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

            self.refresh_counters()

            # Temporary solution
            self.called_lv.controls = [self.__build_tile(r) for r in self.phonebook['called']]
            self.not_called_lv.controls = [self.__build_tile(r) for r in self.phonebook['not_called']]

            self.show_message("Synced!")

        except Exception as err:
            self.show_message(f"Lỗi: {str(err)}", is_error=True)

        finally:
            self.is_syncing = False
            self.sync_button.disabled = False
            self.sync_button.icon = ft.Icons.REFRESH
            self.sync_button.update()
            self.called_lv.update()
            self.not_called_lv.update()