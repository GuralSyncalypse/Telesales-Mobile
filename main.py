import flet as ft
import asyncio

from core.components import ActionBox
from core.utils import Utils
from modules.telesales import telesales
from modules.crm import qlkh
from login_view import LoginView


# --- ROUTES ---
routes = {
    'login': '/login',
    'home': '/home',
    'settings': '/settings',
    'dashboard': '/dashboard',
    'KH': '/dashboard/KH',
    'marketing': '/dashboard/marketing',
    'telesales': '/dashboard/marketing/telesales'
}


# --- EXTERNAL MODULES ---
login_view = LoginView()
sales_phone = telesales.TelesalesApp()
customers = qlkh.CustomerApp()


# --- MAIN APP ---
async def main(page: ft.Page):
    page.title = "HT Land"
    page.padding = 20

    # THEMES
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

    # --- NAV BAR ---
    def get_nav_bar():
        current_index = 0

        if page.route.startswith("/dashboard"):
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

    def logout():
        page.session.store.set("client", None)
        asyncio.create_task(page.push_route(routes["login"]))

    # --- VIEW GENERATORS (Clean tracking) ---

    # --- VIEWS ---
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
                ft.GridView(
                    runs_count=2,
                    max_extent=200,
                    controls=[
                        ActionBox("Nhân Sự\n(đang phát triển)", ft.Icons.GROUP),
                        ActionBox("Khách Hàng", ft.Icons.PERSON_OUTLINE,
                                  on_click=lambda _: Utils.safe_route(page, routes["KH"])),
                        ActionBox("Dự Án\n(đang phát triển)", ft.Icons.HOUSE),
                        ActionBox("Marketing", ft.Icons.CAMPAIGN,
                                  on_click=lambda _: Utils.safe_route(page, routes["marketing"])),
                    ]
                )
            ]
        )

    def marketing_view():
        return ft.View(
            route=routes["marketing"],
            navigation_bar=get_nav_bar(),
            controls=[
                ft.AppBar(
                    title=ft.Text("Marketing"),
                    leading=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda _: Utils.safe_route(page, routes["dashboard"])
                    ),
                ),
                ft.GridView(
                    runs_count=2,
                    max_extent=200,
                    controls=[
                        ActionBox("Telesales", ft.Icons.PHONE,
                                  on_click=lambda _: Utils.safe_route(page, routes["telesales"])),
                        ActionBox("Mailing\n(đang phát triển)", ft.Icons.MAIL),
                        ActionBox("Posting\n(đang phát triển)", ft.Icons.POST_ADD)
                    ]
                )
            ]
        )

    # --- ROUTER ---
    class Router:
        def __init__(self):
            self.route_map = {
                routes["login"]: self.login,
                routes["home"]: self.home,
                routes["dashboard"]: self.dashboard,
                routes["KH"]: self.customers,
                routes["marketing"]: self.marketing,
                routes["telesales"]: self.telesales,
                routes["settings"]: self.settings,
            }

        def attach_nav(self, view):
            view.navigation_bar = get_nav_bar()
            return view

        def resolve(self):
            page.views.clear()

            handler = self.route_map.get(page.route, self.not_found)
            view = handler()

            if view:
                page.views.append(view)

            page.update()

        # --- ROUTE HANDLERS ---
        def login(self):
            return login_view.get_view(page)

        def home(self):
            return home_view()

        def dashboard(self):
            return dashboard_view()

        def customers(self):
            view = customers.get_view(page, back_route=routes["dashboard"])
            asyncio.create_task(customers.fetch_data())
            return self.attach_nav(view)

        def marketing(self):
            return marketing_view()

        def telesales(self):
            view = sales_phone.get_view(page, back_route=routes["marketing"])
            asyncio.create_task(sales_phone.fetch_data())
            return self.attach_nav(view)

        def settings(self):
            return settings_view()

        def not_found(self):
            return ft.View(controls=[ft.Text("404 - Not Found")])

    router = Router()

    def route_change(e):
        router.resolve()

    async def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            await page.push_route(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Start the app
    await page.push_route('/login')
    
if __name__ == "__main__":
    ft.run(main)