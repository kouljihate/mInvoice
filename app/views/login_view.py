import flet as ft
from app.theme import PRIMARY, SECONDARY, TEXT_SECONDARY
from app import __version__


def login_view(page, navigate):
    username = ft.TextField(label="Username", prefix_icon=ft.Icons.PERSON, width=300,
                            border_radius=8, focused_border_color=PRIMARY)
    password = ft.TextField(label="Password", prefix_icon=ft.Icons.LOCK, password=True,
                            can_reveal_password=True, width=300,
                            border_radius=8, focused_border_color=PRIMARY)
    error_text = ft.Text("", color=ft.Colors.RED, size=13)

    def do_login(e):
        if not username.value or not password.value:
            error_text.value = "Fill in all fields"; page.update(); return
        user = page.db.login(username.value, password.value)
        if user:
            page.session.store.set("user_id", user.id)
            page.session.store.set("username", user.username)
            navigate("/dashboard")
        else:
            error_text.value = "Invalid credentials"
        page.update()

    page.controls.clear()
    page.bgcolor = ft.Colors.WHITE
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Column([
                    ft.Container(height=60),
                    ft.Container(
                        content=ft.Image(src="images/tech-logo.png", width=70, height=70, fit=ft.BoxFit.CONTAIN),
                        padding=10,
                    ),
                    ft.Container(height=20),
                    ft.Text("mobile Invoicing", size=28, weight=ft.FontWeight.BOLD, color=PRIMARY),
                    ft.Text("Manage your Business", size=8, color=TEXT_SECONDARY),
                    ft.Container(height=40),
                    username,
                    ft.Container(height=12),
                    password,
                    ft.Container(height=6),
                    error_text,
                    ft.Container(height=16),
                    ft.Button(
                        "Login", width=300, height=48, on_click=do_login,
                        style=ft.ButtonStyle(
                            bgcolor=PRIMARY, color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=30),
                            elevation=2,
                        ),
                    ),
                ], expand=True, alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(
                    content=ft.Text(f"v{__version__} - @koul", size=11, color=TEXT_SECONDARY),
                    alignment=ft.alignment.Alignment.CENTER,
                    padding=ft.Padding.only(bottom=10),
                ),
            ], expand=True),
            expand=True,
        )
    )
    page.update()
