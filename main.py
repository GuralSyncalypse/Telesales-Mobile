import flet as ft
from functools import partial
from odoo_client import OdooClient

def main(page: ft.Page):
    page.title = "Odoo Mobile Bridge"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.ADAPTIVE

    url_launcher = ft.UrlLauncher()
    state = {"client": None}

    # --- UI Components: Login Screen ---
    # Split URL into IP and Port
    ip_input = ft.TextField(label="Server IP", value="192.168.1.194", hint_text="e.g. 192.168.x.x")
    port_input = ft.TextField(label="Port", value="8069", hint_text="Default: 8069")
    
    db_input = ft.TextField(label="Database Name", value="Telesales")
    user_input = ft.TextField(label="Username", value="admin")
    pass_input = ft.TextField(label="Password", password=True, can_reveal_password=True)
    
    login_button = ft.Button("Login to Odoo", icon=ft.Icons.LOGIN, on_click=lambda e: perform_login())

    login_view = ft.Column([
        ft.Text("Odoo Connection", size=25, weight=ft.FontWeight.BOLD),
        ft.Row([
            ip_input, 
            port_input
        ], tight=True), # Groups IP and Port side-by-side
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
        temp = list_view.controls[index]
        tile = e.control
        index = list_view.controls.index(tile)

        note_field = ft.TextField(
            value=record.get("note") or "",
            label="Edit Note",
            multiline=True
        )

        def toggle_off():
            list_view.controls.pop(index)

        def toggle_on():
            list_view.controls.insert(index, temp)

        def save_note(ev):
            new_note = note_field.value
            
            success = state["client"].update_field(
                model="sale.customer",   # <-- replace with your actual model
                record_id=record["id"],
                field_name="note",
                new_value=new_note
            )

            if success:
                show_message("Note updated!")
                record["note"] = new_note  # update UI data
                page.update()
            else:
                show_message("Failed to update note!")
        
            list_view.controls[index] = ft.Row(
                [
                    note_field,
                    ft.IconButton(icon=ft.Icons.SAVE, on_click=save_note),
                    ft.IconButton(icon=ft.Icons.CANCEL, on_click=toggle_off)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )      
        
        page.update()


    def on_click(e, record):
        tile = e.control
        index = list_view.controls.index(tile)

        # toggle behavior
        if index + 1 < len(list_view.controls) and isinstance(list_view.controls[index + 1], ft.Column):
            list_view.controls.pop(index + 1)
        else:
            dropdown = ft.Column(
                controls=[
                    ft.Text(f"Edit {record.get('name')}"),
                    ft.Text("Option A"),
                    ft.Text("Option B"),
                ]
            )
            list_view.controls.insert(index + 1, dropdown)

        page.update()

    def show_message(text, is_error=False):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(text),
            bgcolor=ft.Colors.RED_400 if is_error else ft.Colors.GREEN_400
        )
        page.show_dialog(page.snack_bar)
        page.update()

    def perform_login():
        # Validate all fields are filled
        if not all([ip_input.value, port_input.value, db_input.value, user_input.value, pass_input.value]):
            show_message("All fields are required", True)
            return

        login_button.disabled = True
        page.update()

        # Construct the URL from IP and Port
        # Note: We assume http for internal servers. Change to https if needed.
        formatted_url = f"http://{ip_input.value.strip()}:{port_input.value.strip()}"

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

        table = state["client"].getPhoneBook()

        if table:
            for record in table:
                phone = record.get('phone_number')

                list_view.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.PERSON, color="blue"),
                        title=ft.Text(record.get('name', 'Unknown')),
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