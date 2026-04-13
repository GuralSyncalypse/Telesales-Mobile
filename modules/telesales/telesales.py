import flet as ft
import asyncio
from functools import partial

class TelesalesApp:
    protocol = 'https'

    def __init__(self):
        self.not_called_lv = None
        self.called_lv = None
        self.not_called_label = "Chưa gọi"
        self.called_label = "Đã gọi"
        self.is_syncing = False
        self.is_editing = False
        self.client = None
        self.phonebook = {
            'called': [],
            'not_called': []
        }

    def refresh_lists(self):
        # ✅ Update labels
        self.not_called_label = f"Chưa gọi ({len(self.phonebook['not_called'])})"
        self.called_label = f"Đã gọi ({len(self.phonebook['called'])})"

        # ✅ Update list content
        self.not_called_lv.controls.clear()
        self.not_called_lv.controls.extend(
            [self.__build_tile(r) for r in self.phonebook['not_called']]
        )

        self.called_lv.controls.clear()
        self.called_lv.controls.extend(
            [self.__build_tile(r) for r in self.phonebook['called']]
        )

        self.page.update()

    def __build_tabs(self):
        # ✅ Create only once
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

            self.tabs = ft.Tabs(
                length=2,
                expand=True,
                content=ft.Column(
                    expand=True,
                    controls=[
                        ft.TabBar(
                            tabs=[
                                ft.Tab(label=self.not_called_label),
                                ft.Tab(label=self.called_label),
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

        return self.tabs

    def __build_tile(self, record):
        name = record.get("customer_id")[1]
        phone = record.get("phone_number")
        switch_icon_btn = ft.IconButton(
            icon=ft.Icons.PHONE,
            icon_color="green",
            tooltip="Call Customer",
            on_click=partial(self.make_call, phone_number=phone)
        ) 
        switch_btn = ft.IconButton(
            icon=ft.Icons.ARROW_BACK if record["is_called"] else ft.Icons.ARROW_FORWARD,
            icon_color="blue",
            on_click=partial(self.__switch_state, record=record)
        )


        return ft.ListTile(
            leading=ft.Icon(ft.Icons.PERSON, color="blue"),
            title=ft.Text(f"{name} - {phone}"),
            subtitle=ft.Text(f"Note: {record.get('note') or 'No notes'}"),
            on_click=partial(self.edit_note, record=record),
            trailing=ft.Row(
                controls=[
                    switch_icon_btn,
                    switch_btn,
                ],
                tight=True
            ),
            text_color=ft.Colors.GREY_900
        )

    def show_message(self, text, is_error=False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(text),
            bgcolor=ft.Colors.RED_400 if is_error else ft.Colors.GREEN_400
        )
        self.page.show_dialog(self.page.snack_bar)
        self.page.update()

    async def __on_exit(self, page : ft.Page, backroute):
        self.phonebook = []
        self.is_editing = False
        self.is_syncing = False

        await page.push_route(backroute)

    def get_view(self, page: ft.Page, back_route="/"):
        self.page = page
        self.client = page.session.store.get("client")

        # Needed for calling
        self.url_launcher = ft.UrlLauncher()
        
        self.sync_button = ft.IconButton(icon=ft.Icons.REFRESH, on_click=lambda e: asyncio.create_task(self.fetch_data(e, page)))

        self.data_view = ft.Column([
            ft.Row([
                ft.Text("Danh sách SĐT", size=20, weight=ft.FontWeight.W_500, color=ft.Colors.GREY_900),
                self.sync_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.__build_tabs()
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
    
    async def make_call(self, e, phone_number):
        await self.url_launcher.launch_url(f"tel:{phone_number}", )
    
    def edit_note(self, e, record):
        if self.is_editing:
            return

        self.is_editing = True
        original_tile = e.control

        # 🔹 Find parent ListView dynamically
        parent = original_tile.parent
        while parent and not isinstance(parent, ft.ListView):
            parent = parent.parent

        if not parent:
            self.is_editing = False
            return

        controls_list = parent.controls

        # 🔹 Find index
        try:
            idx = controls_list.index(original_tile)
        except ValueError:
            self.is_editing = False
            return

        # 🔹 Validation
        def validate(e):
            save_btn.disabled = note_field.value == (record.get("note") or "")
            self.page.update()

        # 🔹 Restore UI
        def restore_ui():
            self.is_editing = False

            for control in controls_list:
                control.disabled = False

            controls_list[idx] = original_tile
            self.page.update()

        # 🔹 Save handler
        def handle_save(ev):
            save_btn.disabled = True
            note_field.disabled = True
            self.page.update()

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

                    # Update UI text
                    original_tile.subtitle = ft.Text(
                        f"Note: {new_note or 'No notes'}"
                    )

                    self.show_message("Note updated!")
                    restore_ui()
                else:
                    raise Exception("API rejected update")

            except Exception as err:
                self.show_message(f"Update failed: {str(err)}", is_error=True)
                save_btn.disabled = False
                note_field.disabled = False
                self.page.update()

        # 🔹 Editor UI
        note_field = ft.TextField(
            value=record.get("note") or "",
            label="Edit Note",
            multiline=True,
            expand=True,
            autofocus=True,
            on_change=validate
        )

        save_btn = ft.IconButton(
            icon=ft.Icons.SAVE,
            tooltip="Save Changes",
            disabled=True
        )

        cancel_btn = ft.IconButton(
            icon=ft.Icons.CANCEL,
            tooltip="Cancel",
            on_click=lambda _: restore_ui()
        )

        save_btn.on_click = handle_save

        editor_row = ft.Row(
            controls=[note_field, save_btn, cancel_btn],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # 🔥 Replace tile with editor
        controls_list[idx] = editor_row
        self.page.update()

    def __switch_state(self, e, record):
        record["is_called"] = not record["is_called"]
        record["_switch_btn"].icon = (
            ft.Icons.ARROW_BACK
            if record["is_called"]
            else ft.Icons.ARROW_FORWARD
        )
        # 🔹 find ListTile container
        tile = e.control
        while tile and not isinstance(tile, ft.ListTile):
            tile = tile.parent

        if not tile:
            return

        # 🔹 remove from current list
        if record["is_called"]:
            try:
                self.not_called_lv.controls.remove(tile)
            except ValueError:
                pass
            self.called_lv.controls.append(tile)
        else:
            try:
                self.called_lv.controls.remove(tile)
                tile
            except ValueError:
                pass
            self.not_called_lv.controls.append(tile)

        self.show_message("Moved succesfully!")
        self.page.update()


    async def fetch_data(self, e, page):
        page = self.page  # ✅ always safe

        if not self.client:
            self.show_message("No client!", is_error=True)
            return

        if self.is_syncing:
            self.show_message("Đang đồng bộ, vui lòng chờ!")
            return

        # ✅ lock immediately
        self.is_syncing = True
        self.sync_button.disabled = True
        page.update()

        try:
            # ✅ ALWAYS fetch (allow refresh)
            self.phonebook['called'] = await asyncio.to_thread(
                self.client.get_table,
                "sale.phonebook",
                ['customer_id', 'phone_number', 'note', 'is_called'],
                [["is_called", "=", True]]
            )

            self.phonebook['not_called'] = await asyncio.to_thread(
                self.client.get_table,
                "sale.phonebook",
                ['customer_id', 'phone_number', 'note', 'is_called'],
                [["is_called", "=", False]]
            )

            self.refresh_lists()
            page.update()

            self.show_message("Synced!")

        except Exception as err:
            self.show_message(f"Lỗi: {str(err)}", is_error=True)

        finally:
            # ✅ always restore state
            self.is_syncing = False
            self.sync_button.disabled = False
            page.update()