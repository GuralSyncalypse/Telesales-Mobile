import flet as ft
import asyncio
from functools import partial
import time

class TelesalesApp:
    protocol = 'https'

    def __init__(self):
        self.is_syncing = False
        self.is_editing = False

        self.not_called_lv = None
        self.called_lv = None
        
        self.client = None
        self.phonebook = {
            'called': [],
            'not_called': []
        }

    def refresh_counters(self):
        # 1. Update the Data Counts
        not_called_count = len(self.phonebook['not_called'])
        called_count = len(self.phonebook['called'])

        # 2. Update the actual Tab objects
        self.tabs.content.controls[0].tabs[0].label = f"Chưa gọi ({not_called_count})"
        self.tabs.content.controls[0].tabs[1].label = f"Đã gọi ({called_count})"
        self.tabs.content.controls[0].tabs[0].update()
        self.tabs.content.controls[0].tabs[1].update()

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
            
            tabs = ft.Tabs(
                length=2,
                expand=True,
                content=ft.Column(
                    expand=True,
                    controls=[
                        ft.TabBar(
                            tabs=[
                                ft.Tab(label="Chưa gọi"),
                                ft.Tab(label="Đã gọi"),
                            ],
                        ),
                        ft.TabBarView(
                            expand=True,
                            controls=[
                                self.not_called_lv,
                                self.called_lv,
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
        is_called = record.get("is_called", False)

        
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

        return ft.ListTile(
            leading=ft.Icon(
                ft.Icons.PERSON, 
                color=ft.Colors.BLUE_GREY if is_called else ft.Colors.BLUE
            ),
            title=ft.Text(
                f"{name} • {phone}",
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK if not is_called else ft.Colors.GREY_500,
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
                controls=[call_btn, switch_btn],
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
    
        self.sync_button = ft.IconButton(icon=ft.Icons.REFRESH, on_click=lambda e: asyncio.create_task(self.fetch_data(e)))

        self.tabs = self.__build_tabs()

        self.data_view = ft.Column([
            ft.Row([
                ft.Text("Danh sách SĐT", size=20, weight=ft.FontWeight.W_500, color=ft.Colors.GREY_900),
                self.sync_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.tabs
        ], expand=True, visible=True)

        return ft.View(
            route=f"/dashboard/marketing/telesales",
            controls=[
                ft.AppBar(
                    title=ft.Text("Telesales"),
                    leading=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: asyncio.create_task(self.__on_exit(page, back_route))
                    ),
                    bgcolor=ft.Colors.BLUE
                ),
                ft.Column(
                    [
                        self.data_view
                    ],
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ],
            padding=20,
        )
        
    
    def edit_note(self, e):
        """
        Handles the UI transition and logic for editing a note within a ListView.
        """
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
                new_note = note_field.value.strip()
                success = self.client.update_field(
                    model="sale.phonebook",
                    record_id=record["id"],
                    field_name="note",
                    new_value=new_note
                )

                if success:
                    record["note"] = new_note
                    original_tile.subtitle = ft.Text(f"Note: {new_note or 'No notes'}")
                    self.show_message("Note updated!")
                    restore_ui()
                else:
                    raise Exception("API rejected update")

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
        print(f"Elapsed time: {end - start:.6f} seconds")


    async def __on_exit(self, page : ft.Page, backroute):
        self.phonebook = []
        self.is_editing = False
        self.is_syncing = False

        await page.push_route(backroute)

    async def make_call(self, e, phone_number):
        await self.url_launcher.launch_url(f"tel:{phone_number}", )

    async def fetch_data(self, e):
        # 1. Prevent concurrent runs
        if self.sync_button.disabled:
            return

        # 2. UI Feedback: Disable button and show loading state
        self.sync_button.disabled = True
        self.sync_button.icon = ft.Icons.HOURGLASS_EMPTY

        if not self.client:
            self.show_message("No client!", is_error=True)
            return

        if self.is_syncing:
            self.show_message("Đang đồng bộ, vui lòng chờ!")
            return

        self.is_syncing = True
        self.sync_button.disabled = True

        try:
            called_task = asyncio.to_thread(
                self.client.get_table,
                "sale.phonebook",
                [("is_called", "=", True)],
                ['customer_id', 'phone_number', 'is_called', 'note']
            )

            not_called_task = asyncio.to_thread(
                self.client.get_table,
                "sale.phonebook",
                [("is_called", "=", False)],
                ['customer_id', 'phone_number', 'is_called', 'note']
            )

            # 2. Run them concurrently
            # This returns a list containing the results of both calls in order
            self.phonebook['called'], self.phonebook['not_called'] = await asyncio.gather(
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
            # ✅ always restore state
            self.is_syncing = False
            self.sync_button.disabled = False
            self.sync_button.icon = ft.Icons.REFRESH
            self.sync_button.update()
            self.page.update()