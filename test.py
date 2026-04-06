import flet as ft

async def main(page: ft.Page):
    page.title = "Phone Call Test"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # The fixed phone number
    PHONE_NUMBER = "1234567890"

    async def handle_call(e):
        try:
            # FIX 1: Using the new recommended way to launch URLs
            # FIX 2: Using 'await' so the coroutine actually runs
            print(f"Attempting to call: {PHONE_NUMBER}")
            await ft.UrlLauncher().launch_url(f"tel:{PHONE_NUMBER}")
        except Exception as ex:
            print(f"Error launching dialer: {ex}")

    # UI Layout
    page.add(
        ft.Icon(icon=ft.Icons.PHONE, size=50),
        ft.Text(f"Test Dialer", size=30, weight=ft.FontWeight.BOLD),
        ft.Text(f"Target: {PHONE_NUMBER}", italic=True),
        ft.Button(
            "Launch Phone App", 
            icon=ft.Icons.PHONE,
            on_click=handle_call  # Flet handles the 'await' for on_click automatically
        )
    )

# Run the app
if __name__ == "__main__":
    ft.run(main)