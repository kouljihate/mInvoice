import flet as ft
from app import __version__
from app.shared.utils import tr_static
from app.fe.mobile.widgets.theme import PRIMARY, SECONDARY, TEXT_SECONDARY
from app.fe.mobile.widgets.ui_helpers import language_bar


def login_view(page, navigate):
    lang = page.session.store.get("lang") or "en"

    username = ft.TextField(label=tr_static(lang, "username"), prefix_icon=ft.Icons.PERSON, width=300,
                            border_radius=8, focused_border_color=PRIMARY)
    password = ft.TextField(label=tr_static(lang, "password"), prefix_icon=ft.Icons.LOCK, password=True,
                            can_reveal_password=True, width=300,
                            border_radius=8, focused_border_color=PRIMARY)
    error_text = ft.Text("", color=ft.Colors.RED, size=13)

    def do_login(e):
        if not username.value or not password.value:
            error_text.value = tr_static(page.session.store.get("lang") or "en", "fill_fields"); page.update(); return
        user = page.db.login(username.value, password.value)
        if user:
            page.session.store.set("user_id", user.id)
            page.session.store.set("username", user.username)
            navigate("/dashboard")
        else:
            error_text.value = tr_static(page.session.store.get("lang") or "en", "invalid_credentials")
        page.update()

    def do_reset(e):
        page.db.reset_password()
        page.snack_bar = ft.SnackBar(ft.Text("Password reset to admin123", color=ft.Colors.WHITE), bgcolor=ft.Colors.GREEN, open=True)
        page.update()

    def do_change(e):
        old = old_pwd.value
        new = new_pwd.value
        if not new:
            page.snack_bar = ft.SnackBar(ft.Text("New password cannot be empty", color=ft.Colors.WHITE), bgcolor=ft.Colors.RED, open=True)
            page.update()
            return
        if page.db.update_password(old, new):
            page.snack_bar = ft.SnackBar(ft.Text("Password changed successfully", color=ft.Colors.WHITE), bgcolor=ft.Colors.GREEN, open=True)
            dlg.open = False
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Current password is incorrect", color=ft.Colors.WHITE), bgcolor=ft.Colors.RED, open=True)
        page.update()

    old_pwd = ft.TextField(label="Current password", password=True, width=280, border_radius=8, focused_border_color=PRIMARY)
    new_pwd = ft.TextField(label="New password", password=True, width=280, border_radius=8, focused_border_color=PRIMARY)
    dlg = ft.AlertDialog(
        title=ft.Text("Change Password", size=16, weight=ft.FontWeight.BOLD),
        content=ft.Column([old_pwd, ft.Container(height=6), new_pwd], spacing=6, tight=True, scroll=ft.ScrollMode.AUTO),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dlg, 'open', False) or page.update()),
            ft.FilledButton("Change", on_click=do_change),
        ],
    )

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
                    ft.Text(tr_static(lang, "mobile_invoicing"), size=28, weight=ft.FontWeight.BOLD, color=PRIMARY),
                    ft.Text(tr_static(lang, "manage_business"), size=8, color=TEXT_SECONDARY),
                    ft.Container(height=40),
                    username,
                    ft.Container(height=12),
                    password,
                    ft.Container(height=6),
                    error_text,
                    ft.Container(height=16),
                    ft.Button(
                        tr_static(lang, "login"), width=300, height=48, on_click=do_login,
                        style=ft.ButtonStyle(
                            bgcolor=PRIMARY, color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=30),
                            elevation=2,
                        ),
                    ),
                    ft.Container(height=12),
                    ft.Row([
                        ft.OutlinedButton("Reset Password", on_click=do_reset, width=145,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20), side=ft.BorderSide(1, SECONDARY), color=SECONDARY)),
                        ft.OutlinedButton("Change Password", on_click=lambda e: page.overlay.append(dlg) or setattr(dlg, 'open', True) or page.update(), width=145,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20), side=ft.BorderSide(1, SECONDARY), color=SECONDARY)),
                    ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=16),
                    ft.Text(f"v{__version__} - @koul", size=9, color=TEXT_SECONDARY),
                ], expand=True, alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                language_bar(page),
            ], expand=True),
            expand=True,
        )
    )
    page.update()
