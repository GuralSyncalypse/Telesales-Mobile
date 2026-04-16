import flet as ft

friends = [
    "Nguyen Van A * 0901234567",
    "Tran Thi B * 0912345678",
    "Le Van C * 0923456789",
]

work = [
    "Boss John * 0981111111",
    "HR Anna * 0982222222",
    "IT Mike * 0983333333",
]


def main(page: ft.Page):
    page.title = "Tabs + ListViews"
    page.padding = 20

    # --- ListViews for each tab ---
    friends_list = ft.ListView(expand=True, spacing=5)
    work_list = ft.ListView(expand=True, spacing=5)

    def render_lists(query: str):
        query = query.lower()

        # Clear both lists
        friends_list.controls.clear()
        work_list.controls.clear()

        # Filter friends
        for item in friends:
            if query in item.lower():
                friends_list.controls.append(
                    ft.Container(
                        content=ft.Text(item),
                        padding=10,
                        border=ft.border.all(1, ft.Colors.BLUE_200),
                        border_radius=8,
                    )
                )

        # Filter work
        for item in work:
            if query in item.lower():
                work_list.controls.append(
                    ft.Container(
                        content=ft.Text(item),
                        padding=10,
                        border=ft.border.all(1, ft.Colors.GREEN_200),
                        border_radius=8,
                    )
                )

        page.update()

    # --- Search bar ---
    search = ft.TextField(
        label="Search contacts",
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: render_lists(e.control.value),
    )

    # --- Tabs (like TabBarView) ---
    tabs = ft.Tabs(
        length=2,
        animation_duration=300,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                        tabs=[
                            ft.Tab(label="Friends"),
                            ft.Tab(label="Works")
                        ],
                    ),
                ft.TabBarView(
                        expand=True,
                        controls=[
                            friends_list,
                            work_list

                        ],
                    ),
            ]
        )
    )

    # Initial render
    render_lists("")

    page.add(search, tabs)


ft.run(main)