import flet as ft, json
from app.database import TemplateSection
from app.ui_helper import page_layout, card
from app.theme import PRIMARY, BACKGROUND


def edit_template_view(page, navigate, doc_type, back_route):
    title_map = {"quote": "Quote Template", "delivery_note": "BL Template", "invoice": "Invoice Template"}
    sections = page.db.get_template_sections(doc_type)

    section_cards = ft.Column(spacing=10)

    def rebuild_section_list():
        section_cards.controls.clear()
        for sec in sections:
            skey = sec.section_key
            sname = sec.section_name
            visible_sw = ft.Switch(value=sec.is_visible, active_color=PRIMARY, on_change=lambda e, s=sec: toggle_visible(s, e.control.value))
            font_sz = ft.TextField(value=str(sec.font_size), width=60, height=40, dense=True, text_size=12,
                                    on_change=lambda e, s=sec: update_field(s, "font_size", float(e.control.value or 10)),
                                    border_radius=6)
            align_dd = ft.Dropdown(value=sec.text_align, width=90, height=40, dense=True, options=[
                ft.dropdown.Option("left"), ft.dropdown.Option("center"), ft.dropdown.Option("right"),
            ], on_change=lambda e, s=sec: update_field(s, "text_align", e.control.value), border_radius=6)
            section_cards.controls.append(card(
                ft.Column([
                    ft.Row([
                        ft.Text(f"{sec.position}. {sname}", size=14, weight=ft.FontWeight.BOLD, color="#1A1A2E", expand=True),
                        ft.Text("Visible:"), visible_sw,
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Row([
                        ft.Text("Font size:", size=11, color="#6B7280"), font_sz,
                        ft.Text("Align:", size=11, color="#6B7280"), align_dd,
                    ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ], spacing=4), padding=14,
            ))
        page.update()

    def toggle_visible(sec, val):
        sec.is_visible = val
        page.db.save_template_section(sec)

    def update_field(sec, field, val):
        setattr(sec, field, val)
        page.db.save_template_section(sec)

    error_txt = ft.Text("", color=ft.Colors.RED, size=13)

    rebuild_section_list()

    page.controls.clear()
    page.bgcolor = BACKGROUND
    page.add(page_layout(page, navigate, title_map.get(doc_type, "Template"), back_route=back_route,
        content=ft.Container(
            content=ft.Column([
                ft.Text("Arrange and customize template sections:", size=13, color="#6B7280"),
                ft.Divider(height=4, color="transparent"),
                section_cards,
                error_txt,
            ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=16, expand=True,
        )))
    page.update()
