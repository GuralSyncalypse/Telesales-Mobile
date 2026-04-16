import flet as ft
import math

def main(page: ft.Page):
    page.title = "Paginated List View"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 1. Setup Data
    total_items = 300
    items_per_page = 80
    data = [f"Item #{i + 1}" for i in range(total_items)]
    
    # 2. State Variable
    current_page = 1

    # 3. UI Components
    list_view = ft.ListView(expand=True, spacing=10, padding=20)
    page_info = ft.Text(size=16, weight=ft.FontWeight.BOLD)
    
    def update_list():
        nonlocal current_page
        list_view.controls.clear()
        
        # Calculate indices
        start = (current_page - 1) * items_per_page
        end = start + items_per_page
        
        # Slice and add items to the view
        for item in data[start:end]:
            list_view.controls.append(
                ft.ListTile(
                    leading=ft.Icons.LABEL_OUTLINED,
                    title=ft.Text(item)
                )
            )
        
        # Update pagination controls
        total_pages = math.ceil(total_items / items_per_page)
        page_info.value = f"Page {current_page} of {total_pages}"
        
        prev_btn.disabled = (current_page == 1)
        next_btn.disabled = (current_page == total_pages)
        
        page.update()

    # 4. Button Handlers
    def next_page(e):
        nonlocal current_page
        current_page += 1
        update_list()

    def prev_page(e):
        nonlocal current_page
        current_page -= 1
        update_list()

    prev_btn = ft.Button("Previous", on_click=prev_page)
    next_btn = ft.Button("Next", on_click=next_page)

    # 5. Build Layout
    page.add(
        ft.Text("Inventory Management", size=30, weight="bold"),
        ft.Container(
            content=list_view,
            expand=True,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=10,
        ),
        ft.Row(
            [prev_btn, page_info, next_btn],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )
    )

    # Initial Render
    update_list()

ft.run(main)