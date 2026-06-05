import flet as ft, shutil, os
from app.database import Company, User
from app.theme import PRIMARY, TEXT_SECONDARY


def setup_view(page, navigate):
    fields = {}
    labels = [
        ("co_name", "Company Name *"), ("co_addr", "Address"), ("co_city", "City"),
        ("co_cp", "Postal Code"), ("co_phone", "Phone"), ("co_email", "Email"),
        ("co_web", "Website"), ("co_ice", "ICE"), ("co_tax", "IF (Tax ID)"),
        ("co_rc", "RC"), ("co_cnss", "CNSS"),
    ]
    for key, label in labels:
        fields[key] = ft.TextField(label=label, width=400, border_radius=8,
                                   focused_border_color=PRIMARY)

    fields["co_currency"] = ft.Dropdown(label="Currency", value="MAD", width=400, options=[
        ft.dropdown.Option("MAD", "MAD - Moroccan Dirham"), ft.dropdown.Option("EUR", "EUR - Euro"),
        ft.dropdown.Option("USD", "USD - Dollar"), ft.dropdown.Option("XOF", "XOF - CFA"),
    ])

    logo_text = ft.Text("No logo selected", size=12, color=TEXT_SECONDARY)
    logo_path = ft.Text("")

    def pick_result(e: ft.FilePickerResultEvent):
        if e.files and e.files[0].path:
            logo_path.value = e.files[0].path
            logo_text.value = os.path.basename(e.files[0].path); logo_text.color = "#2E7D32"; page.update()

    fp = ft.FilePicker(on_result=pick_result)
    page.overlay.append(fp)

    adm_user = ft.TextField(label="Admin Username *", width=400, border_radius=8, focused_border_color=PRIMARY)
    adm_pass = ft.TextField(label="Admin Password *", password=True, can_reveal_password=True, width=400, border_radius=8, focused_border_color=PRIMARY)
    adm_name = ft.TextField(label="Admin Full Name *", width=400, border_radius=8, focused_border_color=PRIMARY)
    error_txt = ft.Text("", color=ft.Colors.RED, size=13)

    def do_save(e):
        if not fields["co_name"].value or not adm_user.value or not adm_pass.value:
            error_txt.value = "Company name, admin username and password are required"; page.update(); return
        logo_dest = ""
        if logo_path.value:
            d = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "assets")
            os.makedirs(d, exist_ok=True)
            logo_dest = os.path.join(d, f"logo{os.path.splitext(logo_path.value)[1]}")
            try: shutil.copy2(logo_path.value, logo_dest)
            except Exception as ex: error_txt.value = f"Logo error: {ex}"; page.update(); return
        page.db.save_company(Company(
            name=fields["co_name"].value, address=fields["co_addr"].value,
            city=fields["co_city"].value, postal_code=fields["co_cp"].value,
            phone=fields["co_phone"].value, email=fields["co_email"].value,
            website=fields["co_web"].value, tax_id=fields["co_tax"].value,
            ice=fields["co_ice"].value, rc=fields["co_rc"].value,
            if_tax=fields["co_tax"].value, cnss=fields["co_cnss"].value,
            logo_path=logo_dest, currency=fields["co_currency"].value
        ))
        page.db.insert_user(User(username=adm_user.value, password=adm_pass.value, full_name=adm_name.value))
        navigate("/login")

    page.controls.clear()
    page.bgcolor = "#F0F2F5"
    page.add(ft.Container(
        content=ft.Column([
            ft.Container(height=20),
            ft.Container(
                content=ft.Icon(ft.Icons.BUSINESS, size=40, color=ft.Colors.WHITE),
                bgcolor=PRIMARY, padding=16, border_radius=24,
            ),
            ft.Container(height=12),
            ft.Text("Welcome to mInvoice", size=22, weight=ft.FontWeight.BOLD, color=PRIMARY),
            ft.Text("Set up your company", size=13, color=TEXT_SECONDARY),
            ft.Divider(height=20, color="transparent"),
            ft.Container(
                content=ft.Column([
                    ft.Text("Company Information", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY),
                    fields["co_name"], fields["co_addr"],
                    ft.Row([fields["co_city"], fields["co_cp"]], spacing=10),
                    fields["co_phone"], fields["co_email"], fields["co_web"],
                    ft.Divider(height=12, color="transparent"),
                    ft.Text("Moroccan Tax Info", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY),
                    fields["co_ice"], fields["co_tax"], fields["co_rc"], fields["co_cnss"],
                    ft.Row([
                        ft.Button("Select Logo", icon=ft.Icons.IMAGE, on_click=lambda e: fp.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)),
                        ft.Container(width=12),
                        ft.Button("Save & Continue", width=200, height=48, on_click=do_save,
                            style=ft.ButtonStyle(bgcolor=PRIMARY, color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=10), elevation=2)),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                ]),
                bgcolor=ft.Colors.WHITE, padding=24, border_radius=16,
                shadow=ft.BoxShadow(blur_radius=12, color="rgba(0,0,0,0.06)", offset=ft.Offset(0, 2)),
            ),
        ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20, expand=True,
    ))
    page.update()
