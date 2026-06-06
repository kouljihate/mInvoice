import flet as ft, os
from app.ui_helper import make_appbar, card, status_badge, primary_button
from app.theme import PRIMARY, BACKGROUND


def delivery_notes_view(page, navigate):
    def share_dn(d):
        if d.pdf_path and os.path.exists(d.pdf_path):
            os.startfile(d.pdf_path)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("No PDF generated yet."))
            page.snack_bar.open = True
            page.update()

    def load():
        docs = page.db.get_all_delivery_notes()
        rows.controls.clear()
        if not docs:
            rows.controls.append(ft.Text("No delivery notes yet.", color="#6B7280"))
        else:
            for d in docs:
                cname = page.db.get_customer(d.customer_id).name if d.customer_id else "N/A"
                rows.controls.append(card(
                    ft.Row([
                        ft.Column([
                            ft.Text(d.delivery_number or f"BL #{d.id}", weight=ft.FontWeight.BOLD, size=15, color="#1A1A2E"),
                            ft.Text(cname, size=12, color="#6B7280"),
                        ], expand=True, spacing=2),
                        ft.Column([
                            ft.Text(f"{d.total_ht:,.2f}", size=14, weight=ft.FontWeight.BOLD, color="#1A1A2E"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=4),
                        ft.IconButton(ft.Icons.REMOVE_RED_EYE, icon_color="#2563EB", icon_size=20,
                                      on_click=lambda e, did=d.id: navigate(f"/view_delivery_note/{did}")),
                        ft.IconButton(ft.Icons.SHARE, icon_color="#0891B2", icon_size=20,
                                      on_click=lambda e, d=d: share_dn(d)),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ))
        page.update()

    rows = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    page.controls.clear()
    page.bgcolor = BACKGROUND
    page.add(ft.Column([
        make_appbar(page, navigate, "Delivery Notes", back_route="/dashboard"),
        ft.Container(content=rows, expand=True, padding=16),
    ], expand=True, spacing=0))
    page.update()
    load()


def delivery_note_view_view(page, navigate, doc_id):
    d = page.db.get_delivery_note(doc_id)
    if not d: navigate("/delivery_notes"); return
    cname = page.db.get_customer(d.customer_id).name if d.customer_id else "Walk-in / Unknown"

    def gen_pdf(e):
        from app.pdf_gen import generate_dn_pdf
        items = page.db.get_quote_items(d.quote_id) if d.quote_id else []
        generate_dn_pdf(page.db.get_company(), d, items)
        page.snack_bar = ft.SnackBar(ft.Text("PDF generated in pdfs/"))
        page.snack_bar.open = True; page.update()

    def edit_template(e):
        from app.views.template_editor import edit_template_view
        edit_template_view(page, navigate, "delivery_note", back_route=f"/view_delivery_note/{doc_id}")

    items = page.db.get_quote_items(d.quote_id) if d.quote_id else []
    items_col = ft.Column(spacing=6)
    for item in items:
        items_col.controls.append(ft.Row([
            ft.Text(f"{item.product_name}", expand=2, size=13),
            ft.Text(f"x{item.quantity}", expand=1, size=13),
            ft.Text(f"{item.unit_price:,.0f}", expand=1, size=13),
            ft.Text(f"{item.quantity * item.unit_price:,.0f}", expand=1, size=13, weight=ft.FontWeight.BOLD),
        ], spacing=4))

    page.controls.clear()
    page.bgcolor = BACKGROUND
    page.add(ft.Column([
        make_appbar(page, navigate, f"{d.delivery_number}", back_route="/delivery_notes"),
        ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text("Customer:", weight=ft.FontWeight.BOLD, size=14, color="#374151"), ft.Text(cname, size=14, color="#374151")], spacing=8),
                        ft.Row([ft.Text("Number:", weight=ft.FontWeight.BOLD, size=14, color="#374151"), ft.Text(d.delivery_number, size=14, color="#374151")], spacing=8),
                        ft.Row([ft.Text("Total:", weight=ft.FontWeight.BOLD, size=16, color=PRIMARY), ft.Text(f"{d.total_ht:,.2f}", size=16, weight=ft.FontWeight.BOLD, color=PRIMARY)], spacing=8),
                    ], spacing=8),
                    bgcolor=ft.Colors.WHITE, padding=20, border_radius=14,
                    shadow=ft.BoxShadow(blur_radius=6, color="rgba(0,0,0,0.04)", offset=ft.Offset(0, 2)),
                ),
                ft.Container(height=12),
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text("Description", weight=ft.FontWeight.BOLD, expand=2, size=12, color="#6B7280"),
                                ft.Text("Qty", weight=ft.FontWeight.BOLD, expand=1, size=12, color="#6B7280"),
                                ft.Text("Price", weight=ft.FontWeight.BOLD, expand=1, size=12, color="#6B7280"),
                                ft.Text("Total", weight=ft.FontWeight.BOLD, expand=1, size=12, color="#6B7280")]),
                        ft.Divider(height=4),
                        items_col,
                    ]),
                    bgcolor=ft.Colors.WHITE, padding=20, border_radius=14,
                    shadow=ft.BoxShadow(blur_radius=6, color="rgba(0,0,0,0.04)", offset=ft.Offset(0, 2)),
                ),
                ft.Container(height=20),
                ft.Row([
                    primary_button("Generate PDF", on_click=gen_pdf),
                    ft.TextButton("Edit Template", icon=ft.Icons.EDIT, on_click=edit_template, style=ft.ButtonStyle(color=PRIMARY)),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
            ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=16, expand=True,
        ),
    ], expand=True, spacing=0))
    page.update()
