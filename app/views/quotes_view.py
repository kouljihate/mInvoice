import flet as ft
from app.ui_helper import make_appbar, card, status_badge, primary_button
from app.theme import PRIMARY, BACKGROUND


def quotes_view(page, navigate):
    def load():
        quotes = page.db.get_all_quotes()
        rows.controls.clear()
        if not quotes:
            rows.controls.append(ft.Text("No quotes yet. Tap + to add.", color="#6B7280"))
        else:
            for q in quotes:
                cname = page.db.get_customer(q.customer_id).name if q.customer_id else "N/A"
                rows.controls.append(card(
                    ft.Row([
                        ft.Column([
                            ft.Text(f"#{q.id}", weight=ft.FontWeight.BOLD, size=15, color="#1A1A2E"),
                            ft.Text(cname, size=12, color="#6B7280"),
                        ], expand=True, spacing=2),
                        ft.Column([
                            ft.Text(f"{q.total_ht:,.2f}", size=14, weight=ft.FontWeight.BOLD, color="#1A1A2E"),
                            status_badge(q.status),
                        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=4),
                        ft.IconButton(ft.Icons.REMOVE_RED_EYE, icon_color="#2563EB", icon_size=20,
                                      on_click=lambda e, qid=q.id: navigate(f"/view_quote/{qid}")),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ))
        page.update()

    rows = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    page.controls.clear()
    page.bgcolor = BACKGROUND
    page.add(ft.Column([
        make_appbar(page, navigate, "Quotes", back_route="/dashboard",
                    actions=[ft.IconButton(ft.Icons.ADD, icon_color=ft.Colors.WHITE, on_click=lambda e: navigate("/add_quote"))]),
        ft.Container(content=rows, expand=True, padding=16),
    ], expand=True, spacing=0))
    page.update()
    load()


def quote_form_view(page, navigate, quote_id=None):
    title = "Edit Quote" if quote_id else "New Quote"
    customers = page.db.get_all_customers()
    cust_opts = [ft.dropdown.Option("0", "Walk-in / Unknown")]
    for c in customers: cust_opts.append(ft.dropdown.Option(str(c.id), c.name))
    cust_dd = ft.Dropdown(label="Customer", width=400, options=cust_opts, value="0",
                          border_radius=8, focused_border_color=PRIMARY)

    items_controls = ft.Column(spacing=6)

    def add_item_row(ref="", desc="", qty=1, up=0, pid=0, sqty=0):
        r = ft.TextField(value=ref, hint_text="Ref", expand=2, border_radius=8, border=ft.InputBorder.UNDERLINE, text_size=13)
        d = ft.TextField(value=desc, hint_text="Description", expand=3, border_radius=8, border=ft.InputBorder.UNDERLINE, text_size=13)
        q = ft.TextField(value=str(qty), hint_text="Qty", expand=1, keyboard_type=ft.KeyboardType.NUMBER, border_radius=8, border=ft.InputBorder.UNDERLINE, text_size=13, width=50)
        p = ft.TextField(value=str(up), hint_text="Price", expand=2, keyboard_type=ft.KeyboardType.NUMBER, border_radius=8, border=ft.InputBorder.UNDERLINE, text_size=13)
        err = ft.Text("", size=11, color=ft.Colors.RED)
        del_btn = ft.IconButton(ft.Icons.DELETE, icon_size=18, icon_color="#DC2626",
                                on_click=lambda e: remove_item(r, d, q, p, err, del_btn))
        row_data = {"product_id": pid, "stock_qty": sqty}

        def on_ref_change(e):
            nonlocal row_data
            val = r.value.strip()
            if len(val) >= 3:
                results = page.db.search_products(val)
                if results:
                    prod = results[0]
                    d.value = prod.name
                    p.value = str(prod.unit_price)
                    q.value = "1"
                    row_data["product_id"] = prod.id
                    row_data["stock_qty"] = prod.quantity
                    err.value = ""
                    page.update()
                elif len(results) == 0:
                    row_data["product_id"] = 0
                    row_data["stock_qty"] = 0
            else:
                row_data["product_id"] = 0
                row_data["stock_qty"] = 0

        def on_qty_change(e):
            nonlocal row_data
            if row_data["product_id"] and row_data["stock_qty"] > 0:
                try:
                    qty_val = int(q.value or 0)
                    if qty_val > row_data["stock_qty"]:
                        err.value = f"Only {row_data['stock_qty']} in stock"
                    else:
                        err.value = ""
                except ValueError:
                    err.value = "Invalid qty"
            page.update()

        r.on_change = on_ref_change
        q.on_change = on_qty_change

        row = ft.Row([r, d, q, p, del_btn], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        row.data = row_data
        items_controls.controls.append(ft.Column([row, err], spacing=1))

    def remove_item(r, d, q, p, err, del_btn):
        for ctrl in items_controls.controls:
            if isinstance(ctrl, ft.Column) and len(ctrl.controls) == 2:
                row_ctrl, err_ctrl = ctrl.controls
                if isinstance(row_ctrl, ft.Row) and del_btn in row_ctrl.controls:
                    items_controls.controls.remove(ctrl)
                    break
        page.update()

    def add_from_stock(e):
        products = page.db.get_all_products()
        if not products:
            page.snack_bar = ft.SnackBar(ft.Text("No products available")); page.snack_bar.open = True; page.update(); return
        for p in products:
            add_item_row(p.reference, p.name, 1, p.unit_price, p.id, p.quantity)
        page.update()

    error_txt = ft.Text("", color=ft.Colors.RED, size=13)

    if quote_id:
        q = page.db.get_quote(quote_id)
        if q:
            cust_dd.value = str(q.customer_id or "0")
            items = page.db.get_quote_items(quote_id)
            for item in items:
                prod = page.db.get_product(item.product_id) if item.product_id else None
                add_item_row(item.product_name if not prod else prod.reference,
                             item.product_name, item.quantity, item.unit_price,
                             item.product_id, prod.quantity if prod else 0)

    def save(e):
        if not items_controls.controls:
            error_txt.value = "Add at least one item"; page.update(); return
        items = []
        has_error = False
        for ctrl in items_controls.controls:
            if not isinstance(ctrl, ft.Column) or len(ctrl.controls) != 2:
                continue
            row_ctrl, err_ctrl = ctrl.controls
            if not isinstance(row_ctrl, ft.Row):
                continue
            fields = [c for c in row_ctrl.controls if isinstance(c, ft.TextField)]
            if len(fields) < 4:
                continue
            ref_w, desc_w, qty_w, price_w = fields[:4]
            row_data = getattr(row_ctrl, "data", {})
            if desc_w.value:
                if row_data.get("product_id") and row_data.get("stock_qty", 0) > 0:
                    try:
                        if int(qty_w.value or 0) > row_data["stock_qty"]:
                            err_ctrl.value = f"Only {row_data['stock_qty']} in stock"
                            has_error = True
                    except ValueError:
                        pass
                from app.database import QuoteItem
                items.append(QuoteItem(
                    product_id=row_data.get("product_id", 0),
                    product_name=desc_w.value,
                    quantity=int(qty_w.value or 1),
                    unit_price=float(price_w.value or 0),
                    tva_rate=0.0
                ))
        if has_error:
            error_txt.value = "Fix stock errors before saving"; page.update(); return
        if not items:
            error_txt.value = "Add at least one item with a description"; page.update(); return
        total_ht = sum(i.quantity * i.unit_price for i in items)
        from app.database import Quote
        quote = Quote(id=quote_id or 0,
                      customer_id=int(cust_dd.value) if cust_dd.value != "0" else 0,
                      total_ht=total_ht, total_ttc=total_ht, status="draft")
        if quote_id:
            page.db.update_quote(quote)
            page.db.delete_quote_items(quote_id)
            for item in items:
                item.quote_id = quote_id
            page.db.insert_quote_items(items)
        else:
            new_id = page.db.insert_quote(quote)
            for item in items:
                item.quote_id = new_id
            page.db.insert_quote_items(items)
        navigate("/quotes")

    page.controls.clear()
    page.bgcolor = BACKGROUND
    page.add(ft.Column([
        make_appbar(page, navigate, title, back_route="/quotes"),
        ft.Container(
            content=ft.Column([
                cust_dd,
                ft.Divider(height=8, color="transparent"),
                ft.Row([
                    ft.Text("Items", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY),
                    ft.TextButton("+ From Stock", on_click=add_from_stock, style=ft.ButtonStyle(color=PRIMARY)),
                ], spacing=8),
                items_controls,
                ft.TextButton("+ Add Item", icon=ft.Icons.ADD, on_click=lambda e: (add_item_row(), page.update()),
                              style=ft.ButtonStyle(color=PRIMARY)),
                error_txt,
                ft.Container(height=12),
                primary_button("Save Quote", on_click=save),
            ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=16, expand=True,
        ),
    ], expand=True, spacing=0))
    page.update()
    if not items_controls.controls:
        add_item_row()
        page.update()


def quote_view_view(page, navigate, quote_id):
    q = page.db.get_quote(quote_id)
    if not q: navigate("/quotes"); return
    cname = page.db.get_customer(q.customer_id).name if q.customer_id else "Walk-in / Unknown"

    items = page.db.get_quote_items(quote_id)
    items_col = ft.Column(spacing=6)
    for item in items:
        items_col.controls.append(ft.Row([
            ft.Text(f"{item.product_name}", expand=2, size=13),
            ft.Text(f"x{item.quantity}", expand=1, size=13),
            ft.Text(f"{item.unit_price:,.0f}", expand=1, size=13),
            ft.Text(f"{item.quantity * item.unit_price:,.0f}", expand=1, size=13, weight=ft.FontWeight.BOLD),
        ], spacing=4))

    total_ht = sum(it.quantity * it.unit_price for it in items)
    from datetime import date as date_mod
    today = date_mod.today().isoformat()

    def do_validate(e):
        dn = page.db.get_dn_by_quote(quote_id)
        inv = page.db.get_invoice_by_quote(quote_id)
        if dn or inv:
            page.snack_bar = ft.SnackBar(ft.Text("Already validated")); page.snack_bar.open = True; page.update(); return

        last_dn = page.db.get_last_dn_id()
        last_inv = page.db.get_last_invoice_id()
        dn_num = f"BL-{last_dn + 1:05d}"
        inv_num = f"INV-{last_inv + 1:05d}"

        from app.database import DeliveryNote, Invoice, InvoiceItem

        dn_obj = DeliveryNote(
            delivery_number=dn_num, quote_id=quote_id,
            customer_id=q.customer_id, date=today,
            total_ht=total_ht, total_ttc=total_ht
        )
        dn_id = page.db.insert_delivery_note(dn_obj)

        inv_obj = Invoice(
            invoice_number=inv_num, quote_id=quote_id,
            delivery_note_id=dn_id, customer_id=q.customer_id,
            date=today, due_date=today, status="unpaid",
            total_ht=total_ht, total_tva=0.0, total_ttc=total_ht
        )
        inv_id = page.db.insert_invoice(inv_obj)

        inv_items = []
        for item in items:
            inv_items.append(InvoiceItem(
                invoice_id=inv_id, product_id=item.product_id,
                product_name=item.product_name, quantity=item.quantity,
                unit_price=item.unit_price, tva_rate=item.tva_rate
            ))
            if item.product_id:
                page.db.decrease_stock(item.product_id, item.quantity)

        if inv_items:
            page.db.insert_invoice_items(inv_items)

        page.db.update_quote_status(quote_id, "validated")
        page.snack_bar = ft.SnackBar(ft.Text(f"Validated → {dn_num} & {inv_num}"))
        page.snack_bar.open = True
        navigate(f"/view_quote/{quote_id}")

    page.controls.clear()
    page.bgcolor = BACKGROUND
    page.add(ft.Column([
        make_appbar(page, navigate, f"Quote #{q.id}", back_route="/quotes"),
        ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text("Customer:", weight=ft.FontWeight.BOLD, size=14, color="#374151"), ft.Text(cname, size=14, color="#374151")], spacing=8),
                        ft.Row([ft.Text("Status:", weight=ft.FontWeight.BOLD, size=14, color="#374151"), status_badge(q.status)], spacing=8),
                        ft.Row([ft.Text("Total:", weight=ft.FontWeight.BOLD, size=16, color=PRIMARY), ft.Text(f"{total_ht:,.2f}", size=16, weight=ft.FontWeight.BOLD, color=PRIMARY)], spacing=8),
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
                primary_button("Validate (→ BL + Invoice)", on_click=do_validate, disabled=q.status != "draft"),
            ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=16, expand=True,
        ),
    ], expand=True, spacing=0))
    page.update()
