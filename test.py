import flet as ft

def main(page: ft.Page):
    page.title = "Navigation Example"

    # 1. Define the View Switching Function
    def route_change(route):
        # Clear existing views (except the base one if desired)
        page.views.clear()
        
        # Route Map: Logic to determine which "page" to show
        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.AppBar(title=ft.Text("Home")),
                        ft.Text("Welcome to the Home Page", size=30),
                        ft.ElevatedButton("Go to Settings", on_click=lambda _: page.push_route("/settings")),
                    ],
                )
            )
        elif page.route == "/settings":
            page.views.append(
                ft.View(
                    "/settings",
                    [
                        ft.AppBar(title=ft.Text("Settings")),
                        ft.Text("Application Settings", size=30),
                        ft.ElevatedButton("Back Home", on_click=lambda _: page.go("/")),
                    ],
                )
            )
        
        page.update()

    # 2. Function to handle "Back" button (especially for mobile/web browsers)
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    # Assign the handlers
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Initialize the app at the home route
    page.go(page.route)

ft.app(target=main)