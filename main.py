import asyncio
import flet as ft
from modules.telesales import telesales
from modules.qlkh import CustomerApp
from login_view import LoginView

# 1. Configuration & Routes
routes = {
    'login': '/login',
    'home': '/home',
    'settings': '/settings',
    'dashboard': '/dashboard',
    'KH': '/dashboard/KH',
    'marketing': '/dashboard/marketing',
    'telesales': '/dashboard/marketing/telesales'
}

async def main(page: ft.Page):
    # Initialize basic page settings
    page.title = "HT Land"
    page.padding = 20

    # 🔹 THEMES (Keeping your exact setup)
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE,
            secondary=ft.Colors.AMBER,
            surface=ft.Colors.WHITE,
            on_surface=ft.Colors.BLACK,
            on_primary=ft.Colors.WHITE,
        )
    )
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_200,
            secondary=ft.Colors.AMBER_200,
            surface=ft.Colors.GREY_900,
            on_surface=ft.Colors.WHITE,
            on_primary=ft.Colors.BLACK,
        )
    )
    page.theme_mode = ft.ThemeMode.DARK

    # --- UI COMPONENTS ---
    
    def get_nav_bar():
        # Logic to determine which tab is selected based on route
        current_index = 0
        if page.route == routes["dashboard"] or page.route.startswith("/dashboard"):
            current_index = 1
        elif page.route == routes["settings"]:
            current_index = 2

        return ft.NavigationBar(
            selected_index=current_index,
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Home"),
                ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Dashboard"),
                ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Cài Đặt")
            ],
            on_change=handle_nav_click
        )

    async def handle_nav_click(e):
        target_routes = [routes["home"], routes["dashboard"], routes["settings"]]
        await page.push_route(target_routes[e.control.selected_index])

    def box(title, icon, on_click=None):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=28, color=ft.Colors.PRIMARY),
                ft.Text(title, size=15, weight="bold"),
            ], alignment="center", horizontal_alignment="center"),
            padding=15, border_radius=20, width=150, height=100,
            bgcolor=ft.Colors.SURFACE, ink=True, on_click=on_click,
            shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.with_opacity(0.1, "black"))
        )

    def logout():
        page.session.store.set("client", None)
        asyncio.create_task(page.push_route(routes["login"]))

    # --- VIEW GENERATORS (Clean tracking) ---

    def home_view():
        return ft.View(
            route=routes["home"],
            navigation_bar=get_nav_bar(),
            controls=[
                ft.AppBar(
                    title=ft.Text("Home"),
                    bgcolor=ft.Colors.PRIMARY,
                ),

                ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=15,
                    controls=[
                        ft.Container(
                            padding=20,
                            content=ft.Text(
                                "Welcome back!",
                                size=20,
                                weight=ft.FontWeight.BOLD
                            )
                        ),

                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Card(
                                    content=ft.Container(
                                        padding=15,
                                        width=150,
                                        content=ft.Column([
                                            ft.Text("Customers"),
                                            ft.Text("0", size=18, weight=ft.FontWeight.BOLD)
                                        ])
                                    )
                                ),
                                ft.Card(
                                    content=ft.Container(
                                        padding=15,
                                        width=150,
                                        content=ft.Column([
                                            ft.Text("Projects"),
                                            ft.Text("0", size=18, weight=ft.FontWeight.BOLD)
                                        ])
                                    )
                                ),
                            ]
                        ),

                        ft.Text("Quick Actions", weight=ft.FontWeight.BOLD),

                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.PERSON_ADD),
                            title=ft.Text("Add Customer"),
                        ),

                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.SEARCH),
                            title=ft.Text("Search Customers"),
                        ),
                    ]
                )
            ]
        )

    def settings_view():
        return ft.View(
            route=routes["settings"],
            navigation_bar=get_nav_bar(),
            controls=[
                ft.AppBar(
                    title=ft.Text("Settings"),
                    bgcolor=ft.Colors.PRIMARY,
                ),

                ft.Column(
                    expand=True,
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.PERSON),
                            title=ft.Text("Account"),
                            subtitle=ft.Text("Profile, password, personal info"),
                        ),

                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.LANGUAGE),
                            title=ft.Text("Language"),
                            subtitle=ft.Text("Change app language"),
                        ),

                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.SECURITY),
                            title=ft.Text("Security"),
                            subtitle=ft.Text("Sessions, devices"),
                        ),

                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.SETTINGS),
                            title=ft.Text("System"),
                            subtitle=ft.Text("App configuration"),
                        ),

                        ft.Divider(),

                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.LOGOUT, color=ft.Colors.RED),
                            title=ft.Text("Log out", color=ft.Colors.RED),
                            subtitle=ft.Text("Sign out of your account"),
                            on_click=logout
                        )
                    ]
                )
            ]
        )

    def dashboard_view():
        return ft.View(
            route=routes["dashboard"],
            navigation_bar=get_nav_bar(),
            controls=[
                ft.AppBar(title=ft.Text("Dashboard"), bgcolor=ft.Colors.PRIMARY),

                ft.Container(
                    content=ft.GridView(
                        runs_count=2,
                        max_extent=200,
                        spacing=20,
                        run_spacing=20,
                        controls=[
                            box("Nhân Sự", ft.Icons.GROUP),
                            box("Khách Hàng", ft.Icons.PERSON_OUTLINE, on_click=lambda _: asyncio.create_task(page.push_route(routes["KH"]))),
                            box("Dự Án", ft.Icons.HOUSE),
                            box("Marketing", ft.Icons.CAMPAIGN,
                                on_click=lambda _: asyncio.create_task(page.push_route(routes["marketing"]))),
                        ],
                    ),
                    padding=20
                )
            ]
        )

    def marketing_view():
        return ft.View(
            route=routes["marketing"],
            navigation_bar=get_nav_bar(),
            controls=[
                ft.AppBar(
                    title=ft.Text("Marketing", color=ft.Colors.ON_PRIMARY),
                    leading=ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                icon_color=ft.Colors.ON_PRIMARY,
                                on_click=lambda e: asyncio.create_task(
                                    page.push_route(routes["dashboard"])
                                )
                            ),
                    bgcolor=ft.Colors.PRIMARY,
                ),
                ft.Container(
                    content=ft.GridView(
                        runs_count=2,
                        max_extent=200,
                        spacing=20,
                        run_spacing=20,
                        controls=[
                            box("Telesales", ft.Icons.PHONE, 
                                on_click=lambda _: asyncio.create_task(page.push_route(routes["telesales"]))),
                            box("Mailing", ft.Icons.MAIL),
                            box("Posting", ft.Icons.POST_ADD)
                        ]
                    ),
                    padding=20
                )              
            ]
        )

    # --- ROUTING ENGINE ---
    def route_change():
        page.views.clear()

        # 🔹 1. LOGIN VIEW
        # We check if the user is on the login route
        if page.route == routes["login"]:
            login_screen = login_view.get_view(page)
            
            page.views.append(login_screen)

        # 🔹 2. DASHBOARD VIEW
        elif page.route == routes["dashboard"]:
            page.views.append(dashboard_view())
        
        elif page.route == routes["KH"]:          
            kh_view = customers.get_view(page, back_route=routes["dashboard"])
            kh_view.navigation_bar = get_nav_bar() 
            
            page.views.append(kh_view)

        # 🔹 3. MARKETING VIEW
        elif page.route == routes["marketing"]:
            page.views.append(marketing_view())

        # 🔹 4. TELESALES VIEW (External Module)
        elif page.route == routes["telesales"]:
            # Get the view from your sales_phone instance            
            ts_view = sales_phone.get_view(page, back_route=routes["marketing"])

            # Inject the Navigation Bar so it appears here too
            ts_view.navigation_bar = get_nav_bar() 
            
            page.views.append(ts_view)
        
        #🔹 5. SETTINGS VIEW
        elif page.route == routes["settings"]:
            page.views.append(settings_view())
            #🔹 5. SETTINGS VIEW
        elif page.route == routes["home"]:
            page.views.append(home_view())

        page.update()

    async def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            await page.push_route(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Start the app
    await page.push_route('/login')

login_view = LoginView()
sales_phone = telesales.TelesalesApp()
customers = CustomerApp()
if __name__ == "__main__":
    ft.run(main)