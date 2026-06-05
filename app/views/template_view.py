import flet as ft


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

