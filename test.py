import flet as ft

def main(page: ft.Page):
    page.title = "Gemini Fluid UI"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 700
    
    # Header Component
    header = ft.Text("My Dashboard", size=28, weight=ft.FontWeight.BOLD)

    # Content Container (This swaps out based on selection)
    main_content = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE)

    def get_feature_view(index):
        """Returns the UI for each of the 4 main features."""
        main_content.controls.clear()
        
        if index == 0:
            # FEATURE 1: WORKSPACE
            main_content.controls.extend([
                ft.ListTile(leading=ft.Icons.TASK_ALT, title=ft.Text("Active Projects"), subtitle=ft.Text("Sub-feature: Track progress")),
                ft.ListTile(leading=ft.Icons.GROUP, title=ft.Text("Team Chat"), subtitle=ft.Text("Sub-feature: Instant messaging")),
            ])
        elif index == 1:
            # FEATURE 2: ANALYTICS
            main_content.controls.extend([
                ft.ListTile(leading=ft.Icons.BAR_CHART, title=ft.Text("Revenue Stats"), subtitle=ft.Text("Sub-feature: Monthly growth")),
                ft.ListTile(leading=ft.Icons.PIE_CHART, title=ft.Text("User Demographics"), subtitle=ft.Text("Sub-feature: Regional data")),
            ])
        elif index == 2:
            # FEATURE 3: MEDIA
            main_content.controls.extend([
                ft.ListTile(leading=ft.Icons.IMAGE, title=ft.Text("Cloud Gallery"), subtitle=ft.Text("Sub-feature: Auto-backup")),
                ft.ListTile(leading=ft.Icons.VIDEOCAM, title=ft.Text("Video Editor"), subtitle=ft.Text("Sub-feature: Quick trim")),
            ])
        elif index == 3:
            # FEATURE 4: SETTINGS
            main_content.controls.extend([
                ft.ListTile(leading=ft.Icons.PERSON, title=ft.Text("Profile Security"), subtitle=ft.Text("Sub-feature: 2FA Setup")),
                ft.ListTile(leading=ft.Icons.PALETTE, title=ft.Text("Theme Engine"), subtitle=ft.Text("Sub-feature: Custom Colors")),
            ])
        page.update()

    # Navigation Logic
    def on_nav_change(e):
        selected = e.control.selected_index
        header.value = ["Workspace", "Analytics", "Media", "Settings"][selected]
        get_feature_view(selected)

    # Bottom Navigation Bar
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.ANALYTICS_OUTLINED, selected_icon=ft.Icons.ANALYTICS, label="Stats"),
            ft.NavigationBarDestination(icon=ft.Icons.PERM_MEDIA_OUTLINED, selected_icon=ft.Icons.PERM_MEDIA, label="Library"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Settings"),
        ],
        on_change=on_nav_change,
    )

    # Initial view
    page.add(
        ft.Container(
            content=ft.Column([
                header,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                main_content
            ]),
            padding=30,
            expand=True
        )
    )
    get_feature_view(0)

ft.run(main)