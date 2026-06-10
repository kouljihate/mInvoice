import flet as ft, os, shutil, csv, json
from app.shared.utils import tr_static
from app.fe.mobile.widgets.ui_helpers import card, status_badge, page_layout
from app.fe.mobile.widgets.theme import PRIMARY, BACKGROUND, TEXT_SECONDARY


def customers_view(page, navigate):
    search_f = ft.TextField(
        hint_text=tr_static(page.session.store.get("lang", "en"), "search"), prefix_icon=ft.Icons.SEARCH, width=400,
        border_radius=8, border_color="#E5E7EB", focused_border_color=PRIMARY,
        on_change=lambda e: load(e.control.value),
    )

    def load(query=""):
        customers = page.db.search_customers(query) if query else page.db.get_all_customers()
        rows.controls.clear()
        if not customers:
            rows.controls.append(ft.Text(tr_static(page.session.store.get("lang", "en"), "no_customers"), color="#6B7280"))
        else:
            for c in customers:
                avatar = ft.Container(
                    content=ft.Text(c.name[0].upper(), size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=PRIMARY, padding=14, border_radius=12, width=56, height=56, alignment=ft.Alignment(0, 0),
                )
                if c.photo_path and os.path.exists(c.photo_path):
                    avatar = ft.Image(src=c.photo_path, width=56, height=56, fit=ft.BoxFit.COVER, border_radius=12)
                rows.controls.append(card(
                    ft.Row([
                        avatar,
                        ft.Column([
                            ft.Row([
                                ft.Text(c.name, weight=ft.FontWeight.BOLD, size=15, color="#1A1A2E", expand=True),
                                status_badge(tr_static(page.session.store.get("lang", "en"), "type_company") if c.customer_type == "company" else tr_static(page.session.store.get("lang", "en"), "type_private")),
                            ], spacing=4),
                            ft.Text(c.address, size=11, color=TEXT_SECONDARY),
                            ft.Row([
                                ft.Text(c.phone, size=11, color="#374151"),
                                ft.Text("|", size=11, color=TEXT_SECONDARY),
                                ft.Text(c.email, size=11, color="#374151"),
                            ], spacing=4),
                        ], expand=True, spacing=1),
                        ft.IconButton(ft.Icons.EDIT, icon_color="#2563EB", icon_size=20,
                                      on_click=lambda e, cid=c.id: navigate(f"/edit_customer/{cid}")),
                        ft.IconButton(ft.Icons.DELETE, icon_color="#DC2626", icon_size=20,
                                      on_click=lambda e, cid=c.id: delete(cid)),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ))
        page.update()

    def delete(cid):
        page.db.delete_customer(cid); load()

    async def pick_bulk():
        files = await bulk_fp.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["json", "csv"])
        if not files or not files[0].path:
            return
        fpath = files[0].path
        ext = os.path.splitext(fpath)[1].lower()
        from app.shared.models import Customer
        imported = 0
        errors = []

        def check_record(record, source=""):
            if not isinstance(record, dict):
                errors.append(f"{source}: expected an object, got {type(record).__name__}")
                return None
            if not record.get("name"):
                errors.append(f"{source}: missing required 'name' field")
                return None
            return Customer(
                name=str(record["name"]),
                customer_type=str(record.get("customer_type", "private")),
                address=str(record.get("address", "")),
                phone=str(record.get("phone", "")),
                email=str(record.get("email", "")),
                tax_id=str(record.get("tax_id", "")),
                rc=str(record.get("rc", "")),
                if_tax=str(record.get("if_tax", "")),
                cnss=str(record.get("cnss", "")),
                photo_path=str(record.get("photo_path", "")),
            )

        try:
            if ext == ".json":
                with open(fpath, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    data = [data]
                if not isinstance(data, list):
                    page.snack_bar = ft.SnackBar(ft.Text(tr_static(page.session.store.get("lang", "en"), "invalid_json"))); page.snack_bar.open = True; page.update(); return
                for i, item in enumerate(data):
                    cust = check_record(item, f"Row {i+1}")
                    if cust:
                        try:
                            page.db.insert_customer(cust)
                            imported += 1
                        except Exception as ex:
                            errors.append(f"Row {i+1} ({cust.name}): {ex}")
            elif ext == ".csv":
                with open(fpath, encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    if not reader.fieldnames or "name" not in reader.fieldnames:
                        page.snack_bar = ft.SnackBar(ft.Text(tr_static(page.session.store.get("lang", "en"), "invalid_csv") + " Expected columns: name, customer_type, address, phone, email, tax_id, rc, if_tax, cnss, photo_path")); page.snack_bar.open = True; page.update(); return
                    for i, row in enumerate(reader, 1):
                        cust = check_record(row, f"Row {i}")
                        if cust:
                            try:
                                page.db.insert_customer(cust)
                                imported += 1
                            except Exception as ex:
                                errors.append(f"Row {i} ({cust.name}): {ex}")
        except json.JSONDecodeError as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"{tr_static(page.session.store.get('lang', 'en'), 'file_error')}: {ex}")); page.snack_bar.open = True; page.update(); return
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"{tr_static(page.session.store.get('lang', 'en'), 'file_error')}: {ex}")); page.snack_bar.open = True; page.update(); return

        msg = f"{tr_static(page.session.store.get('lang', 'en'), 'imported')} {imported} {tr_static(page.session.store.get('lang', 'en'), 'customer_s')}"
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
    page.add(page_layout(page, navigate, tr_static(page.session.store.get("lang", "en"), "customers"), back_route="/dashboard",
                actions=[
                    ft.TextButton(tr_static(page.session.store.get("lang", "en"), "bulk"), icon=ft.Icons.UPLOAD_FILE, style=ft.ButtonStyle(color=ft.Colors.WHITE),
                                 on_click=lambda e: page.run_task(pick_bulk)),
                    ft.IconButton(ft.Icons.ADD, icon_color=ft.Colors.WHITE, on_click=lambda e: navigate("/add_customer")),
                ],
                content=ft.Container(
                    content=ft.Column([search_f, rows], spacing=8, scroll=ft.ScrollMode.AUTO),
                    expand=True, padding=16)))
    page.update()
    load()


def customer_form_view(page, navigate, customer_id=None):
    type_f = ft.Dropdown(label=tr_static(page.session.store.get("lang", "en"), "customer_type"), width=400, options=[
        ft.dropdown.Option("private", tr_static(page.session.store.get("lang", "en"), "private")),
        ft.dropdown.Option("company", tr_static(page.session.store.get("lang", "en"), "company")),
    ], value="private", border_radius=8, focused_border_color=PRIMARY)
    name_f = ft.TextField(label=tr_static(page.session.store.get("lang", "en"), "customer_name"), width=400, border_radius=8, focused_border_color=PRIMARY)
    addr_f = ft.TextField(label=tr_static(page.session.store.get("lang", "en"), "address"), width=400, multiline=True, min_lines=2, border_radius=8, focused_border_color=PRIMARY)
    phone_f = ft.TextField(label=tr_static(page.session.store.get("lang", "en"), "phone"), width=400, border_radius=8, focused_border_color=PRIMARY)
    email_f = ft.TextField(label=tr_static(page.session.store.get("lang", "en"), "email"), width=400, border_radius=8, focused_border_color=PRIMARY)
    tax_f = ft.TextField(label=tr_static(page.session.store.get("lang", "en"), "ice_tax_id"), width=400, border_radius=8, focused_border_color=PRIMARY)
    rc_f = ft.TextField(label=tr_static(page.session.store.get("lang", "en"), "rc"), width=400, border_radius=8, focused_border_color=PRIMARY)
    if_tax_f = ft.TextField(label=tr_static(page.session.store.get("lang", "en"), "if_tax"), width=400, border_radius=8, focused_border_color=PRIMARY)
    cnss_f = ft.TextField(label=tr_static(page.session.store.get("lang", "en"), "cnss"), width=400, border_radius=8, focused_border_color=PRIMARY)
    photo_text = ft.Text(tr_static(page.session.store.get("lang", "en"), "no_photo"), size=12, color="#6B7280")
    photo_val = ft.Text("")
    photo_preview = ft.Container(width=80, height=80, bgcolor="#E5E7EB", border_radius=10)

    async def pick_photo():
        files = await fp.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)
        if files and files[0].path:
            photo_val.value = files[0].path
            photo_text.value = os.path.basename(files[0].path); photo_text.color = "#2E7D32"
            photo_preview.content = ft.Image(src=files[0].path, width=80, height=80, fit=ft.BoxFit.COVER)
            photo_preview.bgcolor = None; page.update()

    fp = ft.FilePicker()
    error_txt = ft.Text("", color=ft.Colors.RED, size=13)

    if customer_id:
        c = page.db.get_customer(customer_id)
        if c:
            type_f.value = c.customer_type
            name_f.value = c.name; addr_f.value = c.address; phone_f.value = c.phone
            email_f.value = c.email; tax_f.value = c.tax_id
            rc_f.value = c.rc; if_tax_f.value = c.if_tax; cnss_f.value = c.cnss
            if c.photo_path and os.path.exists(c.photo_path):
                photo_text.value = os.path.basename(c.photo_path); photo_text.color = "#2E7D32"
                photo_preview.content = ft.Image(src=c.photo_path, width=80, height=80, fit=ft.BoxFit.COVER)
                photo_preview.bgcolor = None

    def save(e):
        if not name_f.value: error_txt.value = tr_static(page.session.store.get("lang", "en"), "customer_name_required"); page.update(); return
        from app.shared.models import Customer
        dest = photo_val.value
        if photo_val.value:
            d = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "assets")
            os.makedirs(d, exist_ok=True)
            dest = os.path.join(d, f"cust_{customer_id or 'new'}{os.path.splitext(photo_val.value)[1]}")
            try: shutil.copy2(photo_val.value, dest)
            except Exception as ex: error_txt.value = f"{tr_static(page.session.store.get('lang', 'en'), 'photo_error')}: {ex}"; page.update(); return
        cust = Customer(id=customer_id or 0, name=name_f.value,
                        customer_type=type_f.value, address=addr_f.value,
                        phone=phone_f.value, email=email_f.value, tax_id=tax_f.value,
                        rc=rc_f.value, if_tax=if_tax_f.value, cnss=cnss_f.value,
                        photo_path=dest)
        if customer_id: page.db.update_customer(cust)
        else: page.db.insert_customer(cust)
        navigate("/customers")

    title = tr_static(page.session.store.get("lang", "en"), "edit_customer") if customer_id else tr_static(page.session.store.get("lang", "en"), "add_customer")
    page.controls.clear()
    page.bgcolor = BACKGROUND
    page.add(page_layout(page, navigate, title, back_route="/customers",
        content=ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Container(content=photo_preview, alignment=ft.alignment.Alignment(0, 0), padding=ft.Padding(top=0, bottom=10, left=0, right=0)),
                        ft.Text(tr_static(page.session.store.get("lang", "en"), "customer_details"), size=15, weight=ft.FontWeight.BOLD, color=PRIMARY),
                        type_f, name_f, addr_f, phone_f, email_f, tax_f, rc_f, if_tax_f, cnss_f,
                        ft.Divider(height=16, color="transparent"),
                        ft.Row([
                            ft.Text(tr_static(page.session.store.get("lang", "en"), "photo_logo"), size=15, weight=ft.FontWeight.BOLD, color=PRIMARY, expand=True),
                            ft.Button(tr_static(page.session.store.get("lang", "en"), "select"), icon=ft.Icons.IMAGE, on_click=lambda e: page.run_task(pick_photo)),
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        error_txt,
                        ft.Container(height=12),
                        ft.Button(tr_static(page.session.store.get("lang", "en"), "save"), width=400, height=48, on_click=save,
                            style=ft.ButtonStyle(bgcolor=PRIMARY, color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=10), elevation=2)),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.Colors.WHITE, padding=24, border_radius=16,
                    shadow=ft.BoxShadow(blur_radius=8, color="rgba(0,0,0,0.04)", offset=ft.Offset(0, 2)),
                ),
            ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=16, expand=True,
        )))
    page.update()
