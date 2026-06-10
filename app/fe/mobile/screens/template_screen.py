import flet as ft, json
from app.shared.models import TemplateSection
from app.fe.mobile.widgets.ui_helpers import page_layout, card
from app.fe.mobile.widgets.theme import PRIMARY, BACKGROUND


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


# Appended from template_view.py
def quote_template_view(page, navigate, quote_id):
    quote = page.db.get_quote(quote_id)
    if not quote: navigate("/quotes"); return

    header_f = ft.TextField(label="Header text", multiline=True, min_lines=3, width=500)
    footer_f = ft.TextField(label="Footer text", multiline=True, min_lines=2, width=500)
    notes_f = ft.TextField(label="Notes", value=quote.notes, multiline=True, min_lines=2, width=500)
    msg = ft.Text("", color=ft.Colors.GREEN)

    def save_template(e):
        quote.notes = notes_f.value
        quote.template = f"HEADER:{header_f.value}||FOOTER:{footer_f.value}"
        page.db.update_quote(quote)
        msg.value = "Template saved!"; page.update()

    def reset_template(e):
        header_f.value = ""; footer_f.value = ""; notes_f.value = quote.notes; page.update()

    if quote.template and quote.template != "default":
        for p in quote.template.split("||"):
            if p.startswith("HEADER:"): header_f.value = p[7:]
            elif p.startswith("FOOTER:"): footer_f.value = p[7:]

    page.controls.clear()
    page.add(
        ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=lambda e: navigate(f"/view_quote/{quote_id}")),
                    ft.Text(f"Template - {quote.quote_number}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ]),
                bgcolor=ft.Colors.BLUE, padding=ft.Padding(left=5, top=10, right=15, bottom=10),
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Edit Quote Template", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Customize the header and footer of the PDF.", size=13, color=ft.Colors.GREY_700),
                    ft.Divider(),
                    ft.Text("Header", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE), header_f,
                    ft.Text("Footer", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE), footer_f,
                    ft.Divider(), notes_f,
                    ft.Row([ft.Button("Save Template", on_click=save_template),
                            ft.OutlinedButton("Reset", on_click=reset_template)]),
                    msg,
                ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=30, expand=True,
            ),
        ], expand=True, spacing=0)
    )
    page.update()
