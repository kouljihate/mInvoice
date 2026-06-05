import flet as ft
from app.ui_helper import make_appbar, card
from app.theme import PRIMARY, BACKGROUND


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
                            ft.Text(inv_label, weight=ft.FontWeight.BOLD, size=15, color="#1A1A2E"),
                            ft.Text(f"{p.date[:10]} | {p.method}", size=12, color="#6B7280"),
                        ], expand=True, spacing=2),
                        ft.Row([
                            ft.Text(f"{p.amount:,.2f}", size=15, weight=ft.FontWeight.BOLD, color="#059669"),
                            ft.IconButton(ft.Icons.DELETE, icon_color="#DC2626", icon_size=20,
                                          on_click=lambda e, pid=p.id, iid=p.invoice_id: delete_pay(pid, iid)),
                        ], spacing=8),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ))
        page.update()

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
