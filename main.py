import flet as ft
from functools import partial
from odoo_client import OdooClient

def main(page: ft.Page):
    page.title = "Odoo Mobile Bridge"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.ADAPTIVE
    # This centers the content vertically
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    # This centers the content horizontally
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER


    logo = ft.Image(
        src="https://htland.net.vn/wp-content/uploads/2026/01/Logo-light-h-nobg-2x-1.png", # Replace with your logo path
        width=200,
        height=150,
        fit="CONTAIN",
    )
    url_launcher = ft.UrlLauncher()
    state = {"client": None}

    # --- UI Components: Login Screen ---
    # Split URL into IP and Port
<<<<<<< Updated upstream
    ip_input = ft.TextField(label="Server IP", value="localhost", hint_text="e.g. 192.168.x.x")
    port_input = ft.TextField(label="Port", value="8069", hint_text="Default: 8069")
=======
    host_input = ft.TextField(
        label="Server Address", 
        value="erp.yourcompany.com", 
        hint_text="e.g. odoo.instance.com",
        icon=ft.Icons.LANGUAGE  # Adds a nice globe icon
    )
>>>>>>> Stashed changes
    
    db_input = ft.TextField(label="Database Name", value="Telesales", icon=ft.Icons.STORAGE_ROUNDED)
    user_input = ft.TextField(label="Username", value="admin", icon=ft.Icons.PERSON_OUTLINE)
    pass_input = ft.TextField(label="Password", password=True, can_reveal_password=True, icon=ft.Icons.LOCK_OUTLINED)
    
    login_button = ft.Button("HTLand", icon=ft.Icons.LOGIN, on_click=lambda e: perform_login(), style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)))

    login_view = ft.Column([
        ft.Text("", size=25, weight=ft.FontWeight.BOLD),
        logo,
        ft.Text("", size=15, weight=ft.FontWeight.BOLD),
        host_input, 
        db_input,
        user_input,
        pass_input,
        login_button
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, visible=True)

    # --- UI Components: Data Screen ---
    list_view = ft.ListView(expand=True, spacing=10, divider_thickness=1)
    loading_indicator = ft.ProgressBar(visible=False, color="blue")
    
    sync_button = ft.IconButton(icon=ft.Icons.REFRESH, on_click=lambda e: fetch_data())
    logout_button = ft.TextButton("Logout", icon=ft.Icons.LOGOUT, icon_color=ft.Colors.RED_400, on_click=lambda e: perform_logout())

    data_view = ft.Column([
        ft.Row([
            ft.Text("Assigned Customer List", size=20, weight=ft.FontWeight.W_500),
            ft.Row([sync_button, logout_button])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        loading_indicator,
        list_view
    ], expand=True, visible=False)

    # --- Logic Functions ---
    def edit_note(e, record):
<<<<<<< Updated upstream
=======
        # 1. Identify which control was clicked
        # We find the tile's parent in the list to know where to swap
>>>>>>> Stashed changes
        tile = e.control
        try:
            index = list_view.controls.index(tile)
        except ValueError:
            return # Control not found in list

<<<<<<< Updated upstream
        original_tile = list_view.controls[index]

=======
        # Keep a reference to the original tile to restore it later
        original_tile = list_view.controls[index]

        # 2. Define the UI for the Editor
>>>>>>> Stashed changes
        note_field = ft.TextField(
            value=record.get("note") or "",
            label="Edit Note",
            multiline=True,
            expand=True, # Allows it to take up available space in the Row
        )

<<<<<<< Updated upstream
        def restore_original():
=======
        def close_editor(ev):
            """Swaps the editor back for the original list tile."""
>>>>>>> Stashed changes
            list_view.controls[index] = original_tile
            page.update()

        def save_note(ev):
            """Handles the API call and UI update."""
            new_note = note_field.value

            success = state["client"].update_field(
                model="sale.customer",
                record_id=record["id"],
                field_name="note",
                new_value=new_note
            )

            if success:
                record["note"] = new_note
<<<<<<< Updated upstream
                show_message("Note updated!")
            else:
                show_message("Failed to update note!")
=======
                # If the original tile has a title/subtitle, update it here
                original_tile.subtitle = ft.Text(new_note) 
                show_message("Note updated!")
                close_editor(None)
            else:
                show_message("Failed to update note!", color="red")

        # 3. Create the Editor Row
        editor_row = list_view.controls[index] = ft.Row(
            [
                note_field,
                ft.IconButton(icon=ft.Icons.SAVE, on_click=save_note),
                ft.IconButton(icon=ft.Icons.CANCEL, on_click=close_editor)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )      

        # 4. Swap the tile for the editor
        list_view.controls[index] = editor_row
        page.update()
>>>>>>> Stashed changes

            restore_original()

<<<<<<< Updated upstream
        edit_row = ft.Row(
            controls=[
                note_field,
                ft.IconButton(icon=ft.Icons.SAVE, on_click=save_note),
                ft.IconButton(icon=ft.Icons.CANCEL, on_click=lambda _: restore_original())
            ],
            alignment=ft.MainAxisAlignment.END
        )

        list_view.controls[index] = edit_row
        page.update()

=======
>>>>>>> Stashed changes
    def show_message(text, is_error=False):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(text),
            bgcolor=ft.Colors.RED_400 if is_error else ft.Colors.GREEN_400
        )
        page.show_dialog(page.snack_bar)
        page.update()

    def perform_login():
        # Validate all fields are filled
        if not all([host_input.value, db_input.value, user_input.value, pass_input.value]):
            show_message("All fields are required", True)
            return

        login_button.disabled = True
        page.update()

        # Construct the URL from IP and Port
        # Note: We assume http for internal servers. Change to https if needed.
        formatted_url = f"https://{host_input.value.strip()}"

        client = OdooClient(formatted_url, db_input.value, user_input.value, pass_input.value)
        
        if client.login():
            state["client"] = client
            login_view.visible = False
            data_view.visible = True
            show_message("Successfully connected!")
            fetch_data() 
        else:
            show_message("Login Failed: Check IP/Port or credentials", True)
            login_button.disabled = False
        page.update()

    def perform_logout():
        state["client"] = None
        pass_input.value = ""
        data_view.visible = False
        login_view.visible = True
        login_button.disabled = False
        show_message("Logged out")
        page.update()

    # 1. Define the call function as async
    async def make_call(e, phone_number):
        await url_launcher.launch_url(f"tel:{phone_number}", )
    
    def fetch_data():
        if not state["client"]: return
        
        loading_indicator.visible = True
        list_view.controls.clear()
        page.update()

        table = state["client"].get_table("sale.customer", ["name", "phone_number", "note"])

        if table:
            for record in table:
                phone = record.get('phone_number')
<<<<<<< Updated upstream
                title = f"{record.get('name', 'Unknown')} - {record.get('phone_number', '')}"
                list_view.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.PERSON, color="blue"),
                        title=ft.Text(title),
=======
                name = record.get('name', 'Unknown')

                list_view.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.PERSON, color="blue"),
                        title=ft.Text(f"{name} - {phone}"),
>>>>>>> Stashed changes
                        subtitle=ft.Text(f"Note: {record.get('note') or 'No notes'}"),
                        # Trigger the edit dialog when clicking the row
                        on_click=partial(edit_note, record=record),
                        
                        # Add a phone icon on the right side
                        trailing=ft.IconButton(
                            icon=ft.Icons.PHONE,
                            icon_color="green",
                            tooltip="Call Customer",
                            on_click=partial(make_call, phone_number=phone)
                        )
                    )
                )
        else:
            list_view.controls.append(ft.Text("No data found.", italic=True))

        loading_indicator.visible = False
        page.update()

    page.add(login_view, data_view)

if __name__ == "__main__":
    ft.run(main)