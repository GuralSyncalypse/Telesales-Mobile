import flet as ft
import asyncio
from functools import partial
from odoo_client import OdooClient

class TelesalesApp:
    protocol = 'https'

    def __init__(self):
        self.is_editing = False
       
        self.state = {"client": None}

        # --- UI Components: Data Screen ---
        self.list_view = ft.ListView(expand=True, spacing=10, divider_thickness=1)
        self.loading_indicator = ft.ProgressBar(visible=False, color="blue")
        
        self.sync_button = ft.IconButton(icon=ft.Icons.REFRESH, on_click=self.fetch_data)

        self.data_view = ft.Column([
            ft.Row([
                ft.Text("Assigned Customer List", size=20, weight=ft.FontWeight.W_500),
                ft.Row([self.sync_button])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.loading_indicator,
            self.list_view
        ], expand=True, visible=False)

    def show_message(self, text, is_error=False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(text),
            bgcolor=ft.Colors.RED_400 if is_error else ft.Colors.GREEN_400
        )
        self.page.show_dialog(self.page.snack_bar)
        self.page.update()

    def get_view(self, page: ft.Page, back_route="/"):
        self.page = page

        # Needed for calling
        self.url_launcher = ft.UrlLauncher()

        # Page config (ONLY if needed, avoid overriding global styles too much)
        # self.page.theme_mode = ft.ThemeMode.DARK

        return ft.View(
            route=f"/dashboard/marketing/telesales",
            controls=[
                ft.AppBar(
                    title=ft.Text("Telesales"),
                    leading=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: asyncio.create_task(page.push_route(back_route))
                    ),
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
        
        # 1. Setup Reference and State
        self.is_editing = True
        original_tile = e.control

        for control in self.list_view.controls:
            if control != original_tile:
                control.disabled = True

        def validate():
            if note_field.value != record.get("note"):
                save_btn.disabled = False
            else:
                save_btn.disabled = True

        def restore_ui():
            """Resets the list item to its original state."""
            self.is_editing = False

            # Re-enable everything
            for control in self.list_view.controls:
                control.disabled = False

            controls_list[idx] = original_tile
            self.page.update()

        def handle_save(ev):

            # Prevent double-clicking save
            save_btn.disabled = True
            note_field.disabled = True
            self.page.update()

            try:
                new_note = note_field.value.strip()
                success = self.state["client"].update_field(
                    model="sale.customer",
                    record_id=record["id"],
                    field_name="note",
                    new_value=new_note
                )

                if success:
                    record["note"] = new_note
                    # Safely update the original UI component
                    if hasattr(original_tile, "subtitle"):
                        original_tile.subtitle = ft.Text(new_note)
                    
                    self.show_message("Note updated!")
                    restore_ui()
                else:
                    raise Exception("API rejected update")

            except Exception as err:
                self.show_message(f"Update failed: {str(err)}", color="red")
                save_btn.disabled = False
                note_field.disabled = False
                self.page.update()

        # Identify the container (ListView) and the position
        try:
            controls_list = self.list_view.controls
            idx = controls_list.index(original_tile)
        except (ValueError, AttributeError):
            self.is_editing = False
            return

        # 2. Define the Editor UI Components
        note_field = ft.TextField(
            value=record.get("note") or "",
            label="Edit Note",
            multiline=True,
            on_change=validate,
            expand=True,
            autofocus=True, # Improved UX: user can start typing immediately
        )

        save_btn = ft.IconButton(icon=ft.Icons.SAVE, tooltip="Save Changes", disabled=True)
        cancel_btn = ft.IconButton(icon=ft.Icons.CANCEL, tooltip="Cancel")

        # 4. Bind Events and Swap UI
        save_btn.on_click = handle_save
        cancel_btn.on_click = lambda _: restore_ui()

        editor_row = ft.Row(
            controls=[note_field, save_btn, cancel_btn],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        controls_list[idx] = editor_row
        self.page.update()

    def fetch_data(self):
        if not self.state["client"]: return
        
        self.loading_indicator.visible = True
        self.list_view.controls.clear()
        self.page.update()

        table = self.state["client"].get_table("sale.customer", ["name", "phone_number", "note"])

        if table:
            for record in table:
                phone = record.get('phone_number')
                name = record.get('name', 'Unknown')

                self.list_view.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.PERSON, color="blue"),
                        title=ft.Text(f"{name} - {phone}"),
                        subtitle=ft.Text(f"Note: {record.get('note') or 'No notes'}"),
                        # Trigger the edit dialog when clicking the row
                        on_click=partial(self.edit_note, record=record),
                        
                        # Add a phone icon on the right side
                        trailing=ft.IconButton(
                            icon=ft.Icons.PHONE,
                            icon_color="green",
                            tooltip="Call Customer",
                            on_click=partial(self.make_call, phone_number=phone)
                        )
                    )
                )
        else:
            self.list_view.controls.append(ft.Text("No data found.", italic=True))

        self.loading_indicator.visible = False
        self.page.update()