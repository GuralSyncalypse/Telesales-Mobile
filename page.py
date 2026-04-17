import flet as ft
import math

def main(page: ft.Page):
    page.title = "Paginated List View with Search"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 1. Setup Data
    total_items = 300
    items_per_page = 80
    data = [f"Item #{i + 1}" for i in range(total_items)]

    # 2. State Variables
    current_page = 1
    filtered_data = data.copy()

    # 3. UI Components
    list_view = ft.ListView(expand=True, spacing=10, padding=20)
    page_info = ft.Text(size=16, weight=ft.FontWeight.BOLD)

    # 🔍 Search Field
    def on_search(e):
        nonlocal filtered_data, current_page

        query = e.control.value.lower()

        if query == "":
            filtered_data = data.copy()
        else:
            filtered_data = [
                item for item in data
                if query in item.lower()
            ]

        current_page = 1
        update_list()

    search_field = ft.TextField(
        hint_text="Search...",
        width=400,
        prefix_icon=ft.Icons.SEARCH,
        on_change=on_search
    )

    # 4. Update List Function
    def update_list():
        nonlocal current_page
        list_view.controls.clear()

        total_filtered = len(filtered_data)
        total_pages = max(1, math.ceil(total_filtered / items_per_page))

        # Clamp current page (important after search)
        if current_page > total_pages:
            current_page = total_pages

        start = (current_page - 1) * items_per_page
        end = start + items_per_page

        # Show items
        for item in filtered_data[start:end]:
            list_view.controls.append(
                ft.ListTile(
                    leading=ft.Icons.LABEL_OUTLINED,
                    title=ft.Text(item)
                )
            )

        # Show "no results"
        if total_filtered == 0:
            list_view.controls.append(
                ft.Text("No results found")
            )

        # Update pagination info
        page_info.value = f"Page {current_page} of {total_pages}"

        prev_btn.disabled = (current_page == 1)
        next_btn.disabled = (current_page == total_pages)

        page.update()

    # 5. Button Handlers
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

    # 6. Layout
    page.add(
        ft.Text("Inventory Management", size=30, weight="bold"),
        search_field,
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