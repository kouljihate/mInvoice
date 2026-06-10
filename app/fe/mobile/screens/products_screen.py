import flet as ft, shutil, os, csv, json
from app.fe.mobile.widgets.ui_helpers import card, page_layout
from app.fe.mobile.widgets.theme import PRIMARY, BACKGROUND, WARNING
from app.shared.utils import tr_static


def products_view(page, navigate):
    search_f = ft.TextField(
        hint_text=tr_static(page.session.store.get("lang", "en"), "search"), prefix_icon=ft.Icons.SEARCH, width=400,
        border_radius=8, border_color="#E5E7EB", focused_border_color=PRIMARY,
        on_change=lambda e: load(e.control.value),
    )

    def load(query=""):
        products = page.db.search_products(query) if query else page.db.get_all_products()
        rows.controls.clear()
        if not products:
            rows.controls.append(ft.Text(tr_static(page.session.store.get("lang", "en"), "no_products"), color="#6B7280"))
        else:
            for p in products:
                photo = ft.Container(width=44, height=44, bgcolor="#E5E7EB", border_radius=8)
                if p.photo_path and os.path.exists(p.photo_path):
                    photo = ft.Image(src=p.photo_path, width=44, height=44, fit=ft.BoxFit.COVER, border_radius=8)
                pkg = f" | {p.package_type}" if p.package_type else ""
                low_stock = p.alert_stock > 0 and p.quantity <= p.alert_stock
                rows.controls.append(card(
                    ft.Row([
                        photo,
                        ft.Column([
                            ft.Row([
                                ft.Text(p.name, weight=ft.FontWeight.BOLD, size=15, color="#1A1A2E", expand=True),
                                ft.Container(
                                    content=ft.Text("!" , size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                    bgcolor=WARNING, width=22, height=22, border_radius=11,
                                    alignment=ft.alignment.Alignment(0, 0),
                                ) if low_stock else ft.Container(),
                            ], spacing=4),
                            ft.Text(f"{tr_static(page.session.store.get('lang', 'en'), 'ref')}: {p.reference}{pkg}", size=11, color="#6B7280"),
                            ft.Text(f"{tr_static(page.session.store.get('lang', 'en'), 'stock')}: {p.quantity} {p.unit} | {p.unit_price:,.0f} MAD/{p.unit}", size=12,
                                    color=WARNING if low_stock else "#374151"),
                        ], expand=True, spacing=2),
                        ft.IconButton(ft.Icons.EDIT, icon_color="#2563EB", icon_size=20, on_click=lambda e, pid=p.id: navigate(f"/edit_product/{pid}")),
                        ft.IconButton(ft.Icons.DELETE, icon_color="#DC2626", icon_size=20, on_click=lambda e, pid=p.id: delete(pid)),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ))
        page.update()

    def delete(pid):
        page.db.delete_product(pid); load()

    async def pick_bulk():
        files = await bulk_fp.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["json", "csv"])
        if not files or not files[0].path:
            return
        fpath = files[0].path
        ext = os.path.splitext(fpath)[1].lower()
        from app.shared.models import Product
        imported = 0
        errors = []
        try:
            if ext == ".json":
                with open(fpath, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    data = [data]
                for item in data:
                    try:
                        prod = Product(
                            name=str(item.get("name", "")),
                            description=str(item.get("description", "")),
                            reference=str(item.get("reference", "")),
                            unit_price=float(item.get("unit_price", item.get("price", 0))),
                            quantity=int(item.get("quantity", item.get("qty", 0))),
                            alert_stock=int(item.get("alert_stock", 0)),
                            unit=str(item.get("unit", "piece")),
                            package_type=str(item.get("package_type", item.get("package", ""))),
                            photo_path=str(item.get("photo_path", "")),
                        )
                        if prod.name:
                            page.db.insert_product(prod)
                            imported += 1
                    except Exception as ex:
                        errors.append(f"Row {item.get('name', '?'):.20s}: {ex}")
            elif ext == ".csv":
                with open(fpath, encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            prod = Product(
                                name=str(row.get("name", "")),
                                description=str(row.get("description", "")),
                                reference=str(row.get("reference", "")),
                                unit_price=float(row.get("unit_price", row.get("price", 0))),
                                quantity=int(row.get("quantity", row.get("qty", 0))),
                                alert_stock=int(row.get("alert_stock", 0)),
                                unit=str(row.get("unit", "piece")),
                                package_type=str(row.get("package_type", row.get("package", ""))),
                                photo_path=str(row.get("photo_path", "")),
                            )
                            if prod.name:
                                page.db.insert_product(prod)
                                imported += 1
                        except Exception as ex:
                            errors.append(f"Row {reader.line_num}: {ex}")
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"File error: {ex}")); page.snack_bar.open = True; page.update(); return

        msg = f"Imported {imported} product(s)"
        if errors:
            short = errors[:3]
            msg += ". First errors: " + "; ".join(short)
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()
        load()

    bulk_fp = ft.FilePicker()
    rows = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    page.controls.clear()
    page.bgcolor = BACKGROUND
    page.add(page_layout(page, navigate, "Products", back_route="/dashboard",
        actions=[
            ft.TextButton("Bulk", icon=ft.Icons.UPLOAD_FILE, style=ft.ButtonStyle(color=ft.Colors.WHITE),
                         on_click=lambda e: page.run_task(pick_bulk)),
            ft.IconButton(ft.Icons.ADD, icon_color=ft.Colors.WHITE, on_click=lambda e: navigate("/add_product")),
        ],
        content=ft.Container(
            content=ft.Column([search_f, rows], spacing=8, scroll=ft.ScrollMode.AUTO),
            expand=True, padding=16)))
    page.update()
    load()


def product_form_view(page, navigate, product_id=None):
    name_f = ft.TextField(label="Product Name *", width=400, border_radius=8, focused_border_color=PRIMARY)
    desc_f = ft.TextField(label="Description", width=400, multiline=True, min_lines=2, border_radius=8, focused_border_color=PRIMARY)
    ref_f = ft.TextField(label="Reference", width=400, border_radius=8, focused_border_color=PRIMARY)
    price_f = ft.TextField(label="Unit Price", width=400, keyboard_type=ft.KeyboardType.NUMBER, border_radius=8, focused_border_color=PRIMARY)
    qty_f = ft.TextField(label="Quantity", expand=True, keyboard_type=ft.KeyboardType.NUMBER, border_radius=8, focused_border_color=PRIMARY)
    alert_f = ft.TextField(label="Alert Stock", expand=True, keyboard_type=ft.KeyboardType.NUMBER, hint_text="0 = disabled", border_radius=8, focused_border_color=PRIMARY)
    unit_f = ft.TextField(label="Unit", value="piece", expand=True, border_radius=8, focused_border_color=PRIMARY)
    pkg_f = ft.TextField(label="Package Type", width=400, hint_text="e.g. Box, Bag, Carton", border_radius=8, focused_border_color=PRIMARY)
    photo_text = ft.Text("No photo", size=12, color="#6B7280")
    photo_val = ft.Text("")
    photo_preview = ft.Container(width=80, height=80, bgcolor="#E5E7EB", border_radius=10)
    saved_photo = ""

    async def pick_photo():
        files = await fp.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)
        if files and files[0].path:
            photo_val.value = files[0].path
            photo_text.value = os.path.basename(files[0].path); photo_text.color = "#2E7D32"
            photo_preview.content = ft.Image(src=files[0].path, width=80, height=80, fit=ft.BoxFit.COVER)
            photo_preview.bgcolor = None; page.update()

    fp = ft.FilePicker()
    error_txt = ft.Text("", color=ft.Colors.RED, size=13)

    if product_id:
        p = page.db.get_product(product_id)
        if p:
            name_f.value = p.name; desc_f.value = p.description; ref_f.value = p.reference
            price_f.value = str(p.unit_price) if p.unit_price else ""
            qty_f.value = str(p.quantity); alert_f.value = str(p.alert_stock) if p.alert_stock else ""
            unit_f.value = p.unit; pkg_f.value = p.package_type
            saved_photo = p.photo_path
            if p.photo_path and os.path.exists(p.photo_path):
                photo_text.value = os.path.basename(p.photo_path); photo_text.color = "#2E7D32"
                photo_preview.content = ft.Image(src=p.photo_path, width=80, height=80, fit=ft.BoxFit.COVER)
                photo_preview.bgcolor = None

    def save(e):
        nonlocal saved_photo
        if not name_f.value: error_txt.value = "Product name is required"; page.update(); return
        dest = saved_photo
        if photo_val.value:
            d = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "assets")
            os.makedirs(d, exist_ok=True)
            dest = os.path.join(d, f"prod_{product_id or 'new'}{os.path.splitext(photo_val.value)[1]}")
            try: shutil.copy2(photo_val.value, dest)
            except Exception as ex: error_txt.value = f"Photo error: {ex}"; page.update(); return
        from app.shared.models import Product
        prod = Product(id=product_id or 0, name=name_f.value, description=desc_f.value,
                       reference=ref_f.value, unit_price=float(price_f.value or 0),
                       quantity=int(qty_f.value or 0),
                       alert_stock=int(alert_f.value or 0),
                       unit=unit_f.value,
                       package_type=pkg_f.value, photo_path=dest)
        if product_id: page.db.update_product(prod)
        else: page.db.insert_product(prod)
        navigate("/products")

    title = "Edit Product" if product_id else "Add Product"
    page.controls.clear()
    page.bgcolor = BACKGROUND
    page.add(page_layout(page, navigate, title, back_route="/products",
        content=ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Container(content=photo_preview, alignment=ft.alignment.Alignment(0, 0), padding=ft.Padding(top=0, bottom=10, left=0, right=0)),
                        ft.Text("Product Details", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY),
                        name_f, desc_f, ref_f, price_f, ft.Row([qty_f, alert_f, unit_f], spacing=8), pkg_f,
                        ft.Divider(height=16, color="transparent"),
                        ft.Row([
                            ft.Text("Photo", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY, expand=True),
                            ft.Button("Select Photo", icon=ft.Icons.IMAGE, on_click=lambda e: page.run_task(pick_photo)),
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Container(height=16),
                        ft.Button("Save", width=400, height=48, on_click=save,
                            style=ft.ButtonStyle(bgcolor=PRIMARY, color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=10), elevation=2)),
                    ]),
                    bgcolor=ft.Colors.WHITE, padding=24, border_radius=16,
                    shadow=ft.BoxShadow(blur_radius=8, color="rgba(0,0,0,0.04)", offset=ft.Offset(0, 2)),
                ),
            ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=16, expand=True,
        )))
    page.update()
