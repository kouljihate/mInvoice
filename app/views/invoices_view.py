import flet as ft, os, base64, webbrowser
from app.i18n import tr
from app.ui_helper import card, status_badge, primary_button, page_layout
from app.theme import PRIMARY, BACKGROUND


def invoices_view(page, navigate):
    def share_inv(inv):
        if inv.pdf_path and os.path.exists(inv.pdf_path):
            os.startfile(inv.pdf_path)
        else:
            page.snack_bar = ft.SnackBar(ft.Text(tr(page, "no_pdf")))
            page.snack_bar.open = True
            page.update()

    def delete_inv(iid):
        def do_delete(e):
            dlg.open = False; page.update()
            page.db.delete_invoice(iid)
            load()
        dlg = ft.AlertDialog(
            title=ft.Text("Delete Invoice", color="#DC2626", weight=ft.FontWeight.BOLD),
            content=ft.Text("This will also delete the associated delivery note and all payments. This cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: (setattr(dlg, 'open', False), page.update())),
                ft.FilledButton("Delete", on_click=do_delete, style=ft.ButtonStyle(bgcolor="#DC2626", color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg); dlg.open = True; page.update()

    def load():
        docs = page.db.get_all_invoices()
        rows.controls.clear()
        if not docs:
            rows.controls.append(ft.Text(tr(page, "no_invoices"), color="#6B7280"))
        else:
            for inv in docs:
                cname = page.db.get_customer(inv.customer_id).name if inv.customer_id else "N/A"
                rows.controls.append(card(
                    ft.Row([
                        ft.Column([
                            ft.Text(inv.invoice_number or f"INV #{inv.id}", weight=ft.FontWeight.BOLD, size=15, color="#1A1A2E"),
                            ft.Text(cname, size=12, color="#6B7280"),
                        ], expand=True, spacing=2),
                        ft.Column([
                            ft.Text(f"{inv.total_ht:,.2f}", size=14, weight=ft.FontWeight.BOLD, color="#1A1A2E"),
                            status_badge(inv.status),
                        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=4),
                        ft.Row([
                            ft.IconButton(ft.Icons.REMOVE_RED_EYE, icon_color="#2563EB", icon_size=20,
                                          on_click=lambda e, iid=inv.id: navigate(f"/view_invoice/{iid}")),
                            ft.IconButton(ft.Icons.SHARE, icon_color="#0891B2", icon_size=20,
                                          on_click=lambda e, inv=inv: share_inv(inv)),
                            ft.IconButton(ft.Icons.DELETE, icon_color="#DC2626", icon_size=20,
                                          on_click=lambda e, iid=inv.id: delete_inv(iid)),
                        ], spacing=0),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ))
        page.update()

    rows = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    page.controls.clear()
    page.bgcolor = BACKGROUND
    page.add(page_layout(page, navigate, "Invoices", back_route="/dashboard",
                content=ft.Container(content=rows, expand=True, padding=16)))
    page.update()
    load()


def invoice_view_view(page, navigate, invoice_id):
    inv = page.db.get_invoice(invoice_id)
    if not inv: navigate("/invoices"); return
    cname = page.db.get_customer(inv.customer_id).name if inv.customer_id else "Walk-in / Unknown"
    payments = page.db.get_payments(invoice_id)
    paid_total = sum(p.amount for p in payments)

    def gen_pdf(e):
        try:
            from app.pdf_gen import generate_invoice_pdf
            company = page.db.get_company()
            items = page.db.get_invoice_items(invoice_id)
            payments = page.db.get_payments(invoice_id)
            paid_total = sum(p.amount for p in payments)
            path = generate_invoice_pdf(company, inv, items, payments, paid_total)
            page.db.update_invoice_pdf(inv.id, path)
            navigate(f"/view_invoice_pdf/{invoice_id}")
        except Exception as ex:
            import traceback
            traceback.print_exc()
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}", color=ft.Colors.WHITE), bgcolor=ft.Colors.RED, open=True)
            page.update()

    def add_payment(e):
        amount_f = ft.TextField(label="Payment Amount", keyboard_type=ft.KeyboardType.NUMBER, border_radius=8, width=300, focused_border_color=PRIMARY)
        method_f = ft.Dropdown(label="Method", options=[ft.dropdown.Option("Cash"), ft.dropdown.Option("Check"), ft.dropdown.Option("Bank Transfer"), ft.dropdown.Option("Card")], width=300, border_radius=8, focused_border_color=PRIMARY)
        ref_f = ft.TextField(label="Reference", width=300, border_radius=8, focused_border_color=PRIMARY)
        pay_err = ft.Text("", color=ft.Colors.RED, size=13)

        def do_pay(ee):
            if not amount_f.value: pay_err.value = "Enter amount"; page.update(); return
            from datetime import date
            from app.database import Payment
            try:
                new_amount = float(amount_f.value)
                total_paid = paid_total + new_amount
                new_status = "done" if total_paid >= inv.total_ht else "incomplete"
                pmt = Payment(invoice_id=invoice_id, amount=new_amount,
                              date=date.today().isoformat(), method=method_f.value or "Cash",
                              reference=ref_f.value, status=new_status)
                page.db.insert_payment(pmt)
                page.db.recalc_invoice_status(invoice_id)
                dlg.open = False; page.overlay.remove(dlg); page.update()
                page.snack_bar = ft.SnackBar(ft.Text("Payment recorded", color=ft.Colors.WHITE), bgcolor=ft.Colors.GREEN, open=True)
                page.update()
                import asyncio
                async def _go():
                    await asyncio.sleep(0.8)
                    navigate(f"/view_invoice/{invoice_id}")
                page.run_task(_go())
            except ValueError:
                pay_err.value = "Invalid amount"; page.update()

        def close_dlg(ee):
            dlg.open = False; page.overlay.remove(dlg); page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Record Payment"),
            content=ft.Column([amount_f, method_f, ref_f, pay_err], tight=True, spacing=12),
            actions=[ft.TextButton("Cancel", on_click=close_dlg),
                     ft.Button("Save", on_click=do_pay, style=ft.ButtonStyle(bgcolor=PRIMARY, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10)))],
            actions_alignment=ft.MainAxisAlignment.END,
            open=True,
        )
        page.overlay.append(dlg)
        page.update()

    def confirm_delete():
        def do_delete(e):
            dlg.open = False; page.overlay.remove(dlg); page.update()
            page.db.delete_invoice(invoice_id)
            navigate("/invoices")
        dlg = ft.AlertDialog(
            title=ft.Text("Delete Invoice", color="#DC2626", weight=ft.FontWeight.BOLD),
            content=ft.Text("This will also delete the associated delivery note and all payments. This cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: (setattr(dlg, 'open', False), page.overlay.remove(dlg), page.update())),
                ft.FilledButton("Delete", on_click=do_delete, style=ft.ButtonStyle(bgcolor="#DC2626", color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg); dlg.open = True; page.update()

    def edit_template(e):
        from app.views.template_editor import edit_template_view
        edit_template_view(page, navigate, "invoice", back_route=f"/view_invoice/{invoice_id}")

    def mark_sent(e):
        page.db.update_invoice_status(invoice_id, "sent")
        for pmt in payments:
            page.db.conn.execute("UPDATE payments SET status='waiting' WHERE id=?", (pmt.id,))
        page.db.conn.commit()
        navigate(f"/view_invoice/{invoice_id}")

    inv_items_list = page.db.get_invoice_items(invoice_id)
    items_col = ft.Column(spacing=6)
    for item in inv_items_list:
        items_col.controls.append(ft.Row([
            ft.Text(f"{item.product_name}", expand=2, size=13),
            ft.Text(f"x{item.quantity}", expand=1, size=13),
            ft.Text(f"{item.unit_price:,.0f}", expand=1, size=13),
            ft.Text(f"{item.quantity * item.unit_price:,.0f}", expand=1, size=13, weight=ft.FontWeight.BOLD),
        ], spacing=4))

    pay_col = ft.Column(spacing=6)
    for p in payments:
        pay_col.controls.append(ft.Row([
            ft.Text(f"{p.date[:10]}", size=12, color="#6B7280"),
            ft.Text(f"{p.amount:,.2f}", size=13, weight=ft.FontWeight.BOLD, color="#059669"),
            ft.Text(p.method, size=12, color="#6B7280"),
            ft.IconButton(ft.Icons.DELETE, icon_color="#DC2626", icon_size=16,
                          on_click=lambda e, pid=p.id: (page.db.delete_payment(pid), page.db.recalc_invoice_status(invoice_id), navigate(f"/view_invoice/{invoice_id}"))),
        ], spacing=8))

    remaining = inv.total_ht - paid_total
    page.controls.clear()
    page.bgcolor = BACKGROUND
    page.add(page_layout(page, navigate, f"{inv.invoice_number}", back_route="/invoices",
        content=ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text("Customer:", weight=ft.FontWeight.BOLD, size=14, color="#374151"), ft.Text(cname, size=14, color="#374151")], spacing=8),
                        ft.Row([ft.Text("Status:", weight=ft.FontWeight.BOLD, size=14, color="#374151"), status_badge(inv.status)], spacing=8),
                        ft.Row([ft.Text("Total:", weight=ft.FontWeight.BOLD, size=16, color=PRIMARY), ft.Text(f"{inv.total_ht:,.2f}", size=16, weight=ft.FontWeight.BOLD, color=PRIMARY)], spacing=8),
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
                primary_button("Generate PDF", on_click=gen_pdf),
                ft.Container(height=8),
                primary_button("Mark as Sent", on_click=mark_sent,
                               disabled=inv.status != "draft"),
                ft.Container(height=8),
                ft.Container(height=8),
                ft.Button("Delete Invoice", icon=ft.Icons.DELETE, on_click=lambda e: confirm_delete(),
                          style=ft.ButtonStyle(bgcolor="#DC2626", color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10))),
                ft.TextButton("Edit Template", icon=ft.Icons.EDIT, on_click=edit_template, style=ft.ButtonStyle(color=PRIMARY)),
            ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=16, expand=True,
        )))
    page.update()


def invoice_pdf_view(page, navigate, invoice_id):
    inv = page.db.get_invoice(invoice_id)
    if not inv: navigate("/invoices"); return
    pdf_path = inv.pdf_path
    if not pdf_path or not os.path.exists(pdf_path):
        page.snack_bar = ft.SnackBar(ft.Text("Generate the PDF first."), open=True)
        navigate(f"/view_invoice/{invoice_id}"); return

    img_b64 = None
    try:
        import fitz
        doc = fitz.open(pdf_path)
        pix = doc[0].get_pixmap()
        img_bytes = pix.tobytes("png")
        img_b64 = base64.b64encode(img_bytes).decode()
        doc.close()
    except Exception:
        pass

    def open_pdf(e):
        os.startfile(pdf_path)

    def save_pdf(e):
        import shutil
        from datetime import datetime
        import ctypes
        from ctypes import wintypes
        save_name = f"invoice_{inv.invoice_number}_{datetime.now().strftime('%Y%m%d')}.pdf"
        buf = ctypes.create_unicode_buffer(260)
        ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
        downloads = buf.value
        save_path = os.path.join(downloads, save_name)
        shutil.copy2(pdf_path, save_path)
        page.snack_bar = ft.SnackBar(ft.Text(f"Saved to Downloads: {save_name}"), open=True)
        page.update()

    def share_gmail(e):
        webbrowser.open(f"mailto:?subject=Invoice {inv.invoice_number}&body=Invoice attached - saved at: {pdf_path}")
        page.snack_bar = ft.SnackBar(ft.Text(f"PDF path copied: {pdf_path}"), open=True)
        page.update()

    def share_whatsapp(e):
        webbrowser.open("https://web.whatsapp.com/")
        page.snack_bar = ft.SnackBar(ft.Text(f"Send file from: {pdf_path}"), open=True)
        page.update()

    rows = [ft.Text(f"Invoice {inv.invoice_number}", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY)]
    if img_b64:
        rows.append(ft.Container(
            content=ft.Image(src=f"data:image/png;base64,{img_b64}", fit=ft.BoxFit.CONTAIN, width=400),
            bgcolor=ft.Colors.WHITE, padding=8, border_radius=12,
            shadow=ft.BoxShadow(blur_radius=6, color="rgba(0,0,0,0.06)", offset=ft.Offset(0, 2)),
        ))
    else:
        rows.append(ft.Container(
            content=ft.Text(f"PDF: {pdf_path}", size=12, color="#6B7280"),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=12,
            shadow=ft.BoxShadow(blur_radius=6, color="rgba(0,0,0,0.06)", offset=ft.Offset(0, 2)),
        ))
    share_btn_style = ft.ButtonStyle(
        bgcolor=PRIMARY, color=ft.Colors.WHITE,
        shape=ft.RoundedRectangleBorder(radius=10), elevation=2,
    )
    rows.append(ft.Container(height=16))
    rows.append(ft.Row([
        ft.Button("Open PDF", icon=ft.Icons.OPEN_IN_NEW, on_click=open_pdf, width=170, height=48,
                  style=share_btn_style),
        ft.PopupMenuButton(
            content=ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.SHARE, size=18, color=ft.Colors.WHITE), ft.Text("Share", size=14, color=ft.Colors.WHITE)], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                width=170, height=48, bgcolor=PRIMARY, border_radius=10,
                shadow=ft.BoxShadow(blur_radius=4, color="rgba(0,0,0,0.15)", offset=ft.Offset(0, 2)),
            ),
            items=[
                ft.PopupMenuItem(icon=ft.Icons.SAVE, content=ft.Text("Save to Downloads"), on_click=save_pdf),
                ft.PopupMenuItem(icon=ft.Icons.EMAIL, content=ft.Text("Gmail"), on_click=share_gmail),
                ft.PopupMenuItem(icon=ft.Icons.CHAT, content=ft.Text("WhatsApp"), on_click=share_whatsapp),
            ],
        ),
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=12))

    page.controls.clear()
    page.bgcolor = BACKGROUND
    page.add(page_layout(page, navigate, f"PDF - {inv.invoice_number}", back_route=f"/view_invoice/{invoice_id}",
        content=ft.Container(content=ft.Column(rows, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=16, expand=True)))
    page.update()
