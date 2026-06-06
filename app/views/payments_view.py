import flet as ft
from app.ui_helper import make_appbar, card, status_badge
from app.theme import PRIMARY, BACKGROUND

STATUS_OPTIONS = ["draft", "waiting", "incomplete", "done"]


def payments_view(page, navigate):
    def load():
        payments = page.db.get_all_payments()
        rows.controls.clear()
        if not payments:
            rows.controls.append(ft.Text("No payments recorded.", color="#6B7280"))
        else:
            for p in payments:
                inv = page.db.get_invoice(p.invoice_id)
                inv_label = f"INV #{p.invoice_id}" if inv else f"Inv #{p.invoice_id}"
                rows.controls.append(card(
                    ft.Row([
                        ft.Column([
                            ft.Text(p.payment_number or inv_label, weight=ft.FontWeight.BOLD, size=15, color="#1A1A2E"),
                            ft.Row([
                                ft.Text(f"{p.date[:10]} | {p.method}", size=12, color="#6B7280"),
                                status_badge(p.status),
                            ], spacing=6),
                        ], expand=True, spacing=2),
                        ft.Row([
                            ft.Text(f"{p.amount:,.2f}", size=15, weight=ft.FontWeight.BOLD, color="#059669"),
                            ft.IconButton(ft.Icons.EDIT, icon_color=PRIMARY, icon_size=20,
                                          on_click=lambda e, pid=p.id, oi=p.status: edit_pay(pid, oi)),
                            ft.IconButton(ft.Icons.DELETE, icon_color="#DC2626", icon_size=20,
                                          on_click=lambda e, pid=p.id, iid=p.invoice_id: delete_pay(pid, iid)),
                        ], spacing=4),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ))
        page.update()

    def edit_pay(pid, old_status):
        p = next((x for x in page.db.get_all_payments() if x.id == pid), None)
        if not p:
            return
        inv = page.db.get_invoice(p.invoice_id)
        inv_label = f"INV #{p.invoice_id}" if inv else f"Inv #{p.invoice_id}"
        status_dd = ft.Dropdown(
            label="Status", value=p.status,
            options=[ft.dropdown.Option(s) for s in STATUS_OPTIONS],
            width=300, border_radius=8, focused_border_color=PRIMARY,
        )
        def save(e):
            page.db.conn.execute("UPDATE payments SET status=? WHERE id=?", (status_dd.value, pid))
            page.db.conn.commit()
            page.db.recalc_invoice_status(p.invoice_id)
            page.snack_bar = ft.SnackBar(ft.Text("Status updated", color=ft.Colors.WHITE), bgcolor=ft.Colors.GREEN, open=True)
            page.overlay.remove(dlg); page.update(); load()
        dlg = ft.AlertDialog(
            title=ft.Text("Edit Payment", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                card(ft.Column([
                    ft.Row([ft.Text("Invoice", weight=ft.FontWeight.BOLD, size=14, color="#6B7280"),
                            ft.Text(inv_label, size=14, color="#1A1A2E")], spacing=8),
                    ft.Row([ft.Text("Amount", weight=ft.FontWeight.BOLD, size=14, color="#6B7280"),
                            ft.Text(f"{p.amount:,.2f} MAD", size=14, weight=ft.FontWeight.BOLD, color=PRIMARY)], spacing=8),
                    ft.Row([ft.Text("Date", weight=ft.FontWeight.BOLD, size=14, color="#6B7280"),
                            ft.Text(p.date[:10], size=14, color="#1A1A2E")], spacing=8),
                    ft.Row([ft.Text("Method", weight=ft.FontWeight.BOLD, size=14, color="#6B7280"),
                            ft.Text(p.method, size=14, color="#1A1A2E")], spacing=8),
                    ft.Row([ft.Text("Reference", weight=ft.FontWeight.BOLD, size=14, color="#6B7280"),
                            ft.Text(p.reference or "-", size=14, color="#1A1A2E")], spacing=8),
                    ft.Row([ft.Text("Notes", weight=ft.FontWeight.BOLD, size=14, color="#6B7280"),
                            ft.Text(p.notes or "-", size=14, color="#1A1A2E")], spacing=8),
                    ft.Row([ft.Text("Status", weight=ft.FontWeight.BOLD, size=14, color="#6B7280"),
                            status_badge(p.status)], spacing=8),
                ], spacing=6)),
                ft.Container(height=12),
                status_dd,
            ], spacing=8, tight=True, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: (page.overlay.remove(dlg), page.update(), load())),
                ft.FilledButton("Save", on_click=save),
            ],
        )
        page.overlay.append(dlg); dlg.open = True; page.update()

    def delete_pay(pid, iid):
        page.db.delete_payment(pid)
        page.db.recalc_invoice_status(iid)
        load()

    rows = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    page.controls.clear()
    page.bgcolor = BACKGROUND
    page.add(ft.Column([
        make_appbar(page, navigate, "Payments", back_route="/dashboard"),
        ft.Container(content=rows, expand=True, padding=16),
    ], expand=True, spacing=0))
    page.update()
    load()
