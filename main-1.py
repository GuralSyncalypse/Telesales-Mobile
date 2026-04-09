import flet as ft
from functools import partial
from odoo_client import OdooClient

class TelesalesApp:
    protocol = 'https'

    def __init__(self):
        self.is_editing = False
       
        self.state = {"client": None}
        # --- UI Components: Login Screen ---
        self.logo = ft.Image(
            src="HTLand-1.png", 
            width=200,
            height=150,
            fit='CONTAIN',
            margin=ft.Margin.only(top=10, bottom=10)
        )
        
        self.domain_input = ft.TextField(
            label="Domain Name",
            icon=ft.Icons.LANGUAGE
        )
        
        self.protocol_checkbox = ft.Checkbox(label="Use HTTPS", value=True)


        self.db_input = ft.TextField(label="Database Name", value="Telesales", icon=ft.Icons.STORAGE_ROUNDED)
        self.user_input = ft.TextField(label="Username", value="admin", icon=ft.Icons.PERSON_OUTLINE)
        self.pass_input = ft.TextField(label="Password", password=True, can_reveal_password=True, icon=ft.Icons.LOCK_OUTLINED)
        
        self.login_button = ft.Button(
            "HTLand", 
            icon=ft.Icons.LOGIN, 
            on_click=self.__on_login,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
        )

        self.login_view = ft.Column([
            self.logo,
            self.domain_input,
            ft.Row(controls=[self.protocol_checkbox], alignment=ft.MainAxisAlignment.CENTER),
            self.db_input,
            self.user_input,
            self.pass_input,     
            self.login_button
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, visible=True)

        # --- UI Components: Data Screen ---
        self.list_view = ft.ListView(expand=True, spacing=10, divider_thickness=1)
        self.loading_indicator = ft.ProgressBar(visible=False, color="blue")
        
        self.sync_button = ft.IconButton(icon=ft.Icons.REFRESH, on_click=self.fetch_data)
        self.logout_button = ft.TextButton("Logout", icon=ft.Icons.LOGOUT, icon_color=ft.Colors.RED_400, on_click=self.__on_logout)

        self.data_view = ft.Column([
            ft.Row([
                ft.Text("Assigned Customer List", size=20, weight=ft.FontWeight.W_500),
                ft.Row([self.sync_button, self.logout_button])
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

    def build(self, page: ft.Page):
        # Do not move this outside the function.
        self.url_launcher = ft.UrlLauncher()

        self.page = page
        self.page.title = "HTLand CRM"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.ADAPTIVE
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # self.__build_tab()

        # Add both views to the page
        self.page.add(self.login_view, self.data_view)

    def __build_tab(self):
        # 1. Define the content areas for each "feature"
        feature_1 = ft.Column([ft.Text("Feature 1: Analytics Dashboard", size=25)], visible=True)
        feature_2 = ft.Column([ft.Text("Feature 2: Settings & Profile", size=25)], visible=True)
        feature_3 = ft.Column([ft.Text("Feature 3: Data Export", size=25)], visible=False)

        # 2. Function to handle tab switching
        def tab_changed(e):
            # Hide everything first
            feature_1.visible = False
            feature_2.visible = False
            feature_3.visible = False
            
            # Show the selected feature based on index
            index = e.control.selected_index
            if index == 0:
                feature_1.visible = True
            elif index == 1:
                feature_2.visible = True
            elif index == 2:
                feature_3.visible = True
                
            self.page.update()

        # 3. Create the Tabs control
        tabs = ft.Tabs(
            content=[
                ft.Tab(label="Analytics", icon=ft.Icons.ANALYTICS),
                ft.Tab(label="Settings", icon=ft.Icons.SETTINGS),
                ft.Tab(label="Export", icon=ft.Icons.SAVE_ALT),
            ],
            selected_index=0,
            animation_duration=300,
            on_change=tab_changed,
            length=5,
            expand=1 # Allows tabs to take up available space
        )

        # 4. Add to page
        self.page.add(
            tabs,
            ft.Divider(),
            feature_1, 
            feature_2, 
            feature_3
        )

    def __switch_view(self, active_view):
        """
        Hides all views and shows only the one passed as an argument.
        Usage: self.switch_view(self.data_view)
        """
        views = [self.login_view, self.data_view]
        
        for view in views:
            view.visible = (view == active_view)

    def __on_login(self):
        # Validate all fields are filled
        if not all([self.domain_input.value, self.db_input.value, self.user_input.value, self.pass_input.value]):
            self.show_message("All fields are required", True)
            return

        self.login_button.disabled = True
        self.page.update()

        protocol = "https" if self.protocol_checkbox.value else "http"
        base_url = f"{protocol}://{self.domain_input.value.strip()}"

        client = OdooClient(base_url, self.db_input.value, self.user_input.value, self.pass_input.value)
        
        if client.login():
            self.state["client"] = client
            self.__switch_view(self.data_view)
            self.show_message("Successfully connected!")
            self.fetch_data() 
        else:
            self.show_message("Login Failed: Check IP/Port or credentials", True)
            self.login_button.disabled = False
        self.page.update()

    def __on_logout(self):
        self.state["client"] = None
        self.pass_input.value = ""
        
        self.__switch_view(self.login_view)
        self.login_button.disabled = False
        self.show_message("Logged out")
        self.page.update()
    
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

# Launch the app
if __name__ == "__main__":
    app = TelesalesApp()
    ft.run(app.build)