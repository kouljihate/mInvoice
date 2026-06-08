import flet as ft
from app.theme import PRIMARY, SECONDARY, CARD_BG, BACKGROUND, BORDER_COLOR, TEXT_SECONDARY, SUCCESS, ERROR, WARNING, border_all
from app.theme import LANG_EN, LANG_AR, LANG_FR, LANG_NAMES, LANG_FONTS, FONT_COMFORTAA, FONT_REEM
from app import __version__


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
    STATUS_COLORS = {"draft": "#9E9E9E", "validated": SUCCESS, "completed": SUCCESS,
                     "sent": "#0891B2", "partial": WARNING, "confirmed": "#2563EB",
                     "cancelled": ERROR, "waiting": "#F59E0B", "incomplete": "#EF4444",
                     "done": SUCCESS}
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


def language_bar(page):
    current = page.session.store.get("lang") or LANG_EN
    def switch_lang(lang):
        page.session.store.set("lang", lang)
        font = LANG_FONTS.get(lang, FONT_COMFORTAA)
        page.theme.font_family = font
        page.update()
        page.navigate(page.session.store.get("current_route") or "/dashboard")
    return ft.Container(
        content=ft.Column([
            ft.Divider(height=1, color="#E5E7EB"),
            ft.Row(
                [ft.TextButton(
                    LANG_NAMES[code],
                    on_click=lambda e, c=code: switch_lang(c),
                    style=ft.ButtonStyle(
                        color=PRIMARY if code == current else TEXT_SECONDARY,
                        bgcolor=ft.Colors.TRANSPARENT,
                    ),
                ) for code in [LANG_EN, LANG_FR, LANG_AR]],
                alignment=ft.MainAxisAlignment.CENTER, spacing=4,
            ),
            ft.Text(f"v{__version__} - @koul", size=10, color=TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
            ft.Container(height=6),
        ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=ft.Colors.WHITE,
        padding=ft.Padding(left=0, top=4, right=0, bottom=0),
    )


def page_layout(page, navigate, title, content, back_route=None, actions=None):
    return ft.Column([
        make_appbar(page, navigate, title, back_route=back_route, actions=actions),
        ft.Container(content=content, expand=True, padding=16),
    ], expand=True, spacing=0)
