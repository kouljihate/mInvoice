import flet as ft
from app.theme import PRIMARY, SECONDARY, CARD_BG, BACKGROUND, BORDER_COLOR, TEXT_SECONDARY, SUCCESS, ERROR, WARNING, border_all


def make_appbar(page, navigate, title, back_route=None, actions=None):
    items = []
    if back_route:
        items.append(ft.IconButton(ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE,
                                   on_click=lambda e: navigate(back_route)))
    items.append(ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, expand=True))
    right = []
    right.append(ft.IconButton(ft.Icons.HOME, icon_color=ft.Colors.WHITE,
                                on_click=lambda e: navigate("/dashboard")))
    if actions:
        right.extend(actions)
    items.append(ft.Row(right, tight=True))
    return ft.Container(
        content=ft.Row(items, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=PRIMARY,
        padding=ft.Padding(left=5, top=8, right=5, bottom=8),
        shadow=ft.BoxShadow(blur_radius=4, color="rgba(0,0,0,0.15)", offset=ft.Offset(0, 2)),
    )


def card(content, on_click=None, padding=14):
    return ft.Container(
        content=content,
        bgcolor=CARD_BG,
        border_radius=12,
        padding=padding,
        ink=True,
        on_click=on_click,
        shadow=ft.BoxShadow(blur_radius=6, color="rgba(0,0,0,0.06)", offset=ft.Offset(0, 2)),
        border=border_all(),
    )


def status_badge(text):
    STATUS_COLORS = {"draft": "#9E9E9E", "validated": SUCCESS, "paid": SUCCESS,
                     "unpaid": ERROR, "partial": WARNING, "confirmed": "#2563EB",
                     "sent": "#0891B2", "cancelled": ERROR}
    color = STATUS_COLORS.get(text.lower(), "#9E9E9E") if text else "#9E9E9E"
    return ft.Container(
        content=ft.Text(text.upper(), size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        padding=ft.Padding(left=10, top=4, right=10, bottom=4),
        bgcolor=color,
        border_radius=20,
    )


def primary_button(text, on_click, width=400, icon=None, disabled=False):
    return ft.Button(
        text, on_click=on_click, width=width, height=48, disabled=disabled,
        style=ft.ButtonStyle(
            bgcolor=PRIMARY, color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=10),
            elevation=2,
        ),
        icon=icon,
    )


def styled_field(label, width=400, **kwargs):
    return ft.TextField(
        label=label, width=width,
        border_radius=8,
        border_color=BORDER_COLOR,
        focused_border_color=PRIMARY,
        **kwargs
    )
