import flet as ft
from app.ui_helper import make_appbar
from app.theme import PRIMARY, BACKGROUND


def edit_template_view(page, navigate, doc_type, back_route):
    title_map = {"quote": "Quote Template", "delivery_note": "BL Template", "invoice": "Invoice Template"}
    header_f = ft.TextField(label="Header Text", multiline=True, min_lines=3, width=400, border_radius=8, focused_border_color=PRIMARY)
    footer_f = ft.TextField(label="Footer Text", multiline=True, min_lines=3, width=400, border_radius=8, focused_border_color=PRIMARY)
    error_txt = ft.Text("", color=ft.Colors.RED, size=13)

    tpl = page.db.get_template(doc_type)
    if tpl: header_f.value = tpl.header_text; footer_f.value = tpl.footer_text

    def save(e):
        page.db.save_template(doc_type, header_f.value or "", footer_f.value or "")
        navigate(back_route)

    page.controls.clear()
    page.bgcolor = BACKGROUND
    page.add(ft.Column([
        make_appbar(page, navigate, title_map.get(doc_type, "Template"), back_route=back_route),
        ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        header_f,
                        ft.Container(height=12),
                        footer_f,
                        error_txt,
                        ft.Container(height=16),
                        ft.Button("Save Template", width=400, height=48, on_click=save,
                            style=ft.ButtonStyle(bgcolor=PRIMARY, color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=10), elevation=2)),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.Colors.WHITE, padding=24, border_radius=16,
                    shadow=ft.BoxShadow(blur_radius=8, color="rgba(0,0,0,0.04)", offset=ft.Offset(0, 2)),
                ),
            ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=16, expand=True,
        ),
    ], expand=True, spacing=0))
    page.update()
