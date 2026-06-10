import flet as ft

PRIMARY = "#1B2A4A"
PRIMARY_LIGHT = "#2C3E6B"
SECONDARY = "#C8A84E"
SURFACE = "#FFFFFF"
BACKGROUND = "#F0F2F5"
CARD_BG = "#FFFFFF"
ERROR = "#D32F2F"
SUCCESS = "#2E7D32"
WARNING = "#F57C00"
TEXT_PRIMARY = "#1A1A2E"
TEXT_SECONDARY = "#6B7280"
BORDER_COLOR = "#E5E7EB"
DIVIDER_COLOR = "#E5E7EB"


def border_all(width=1, color=BORDER_COLOR):
    side = ft.BorderSide(width, color)
    return ft.Border(left=side, top=side, right=side, bottom=side)


FONT_COMFORTAA = "Comfortaa"
FONT_REEM = "ReemKufiFun"
LANG_EN = "en"
LANG_AR = "ar"
LANG_FR = "fr"
LANG_NAMES = {LANG_EN: "EN", LANG_AR: "AR", LANG_FR: "FR"}
LANG_FONTS = {LANG_EN: FONT_COMFORTAA, LANG_FR: FONT_COMFORTAA, LANG_AR: FONT_REEM}

def apply_theme(page: ft.Page):
    lang = LANG_EN
    font = LANG_FONTS.get(lang, FONT_COMFORTAA)
    page.fonts = {
        FONT_COMFORTAA: "https://github.com/google/fonts/raw/main/ofl/comfortaa/Comfortaa%5Bwght%5D.ttf",
        FONT_REEM: "https://github.com/google/fonts/raw/main/ofl/reemkufifun/ReemKufiFun%5Bwght%5D.ttf",
    }
    page.theme = ft.Theme(
        font_family=font,
        color_scheme=ft.ColorScheme(
            primary=PRIMARY,
            primary_container=PRIMARY_LIGHT,
            secondary=SECONDARY,
            surface=SURFACE,
            error=ERROR,
        ),
        use_material3=True,
    )
    page.bgcolor = BACKGROUND
    page.padding = 0
    page.update()


def top_bar(page, navigate, title, back_route=None, actions=None):
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


def status_badge(text, color):
    return ft.Container(
        content=ft.Text(text.upper(), size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        padding=ft.Padding(left=10, top=4, right=10, bottom=4),
        bgcolor=color,
        border_radius=20,
    )


def section_title(text):
    return ft.Text(text, size=13, weight=ft.FontWeight.BOLD, color=TEXT_SECONDARY)


def primary_button(text, on_click, width=400, icon=None):
    return ft.Button(
        text, on_click=on_click, width=width, height=48,
        style=ft.ButtonStyle(
            bgcolor=PRIMARY, color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=10),
            elevation=2,
        ),
        icon=icon,
    )


def outlined_button(text, on_click, width=400):
    return ft.OutlinedButton(
        text, on_click=on_click, width=width, height=48,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            side=ft.BorderSide(1, PRIMARY),
            color=PRIMARY,
        ),
    )


def styled_field(label, width=400, **kwargs):
    return ft.TextField(
        label=label, width=width,
        border_radius=8,
        border_color=BORDER_COLOR,
        focused_border_color=PRIMARY,
        **kwargs
    )
