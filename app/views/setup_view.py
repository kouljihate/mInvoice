import flet as ft, shutil, os
from app.database import Company, User, TemplateSection
from app.theme import PRIMARY, TEXT_SECONDARY


def setup_view(page, navigate):
    fields = {}
    labels = [
        ("co_name", "Company Name *"), ("co_addr", "Address"), ("co_city", "City"),
        ("co_cp", "Postal Code"), ("co_phone", "Phone"), ("co_email", "Email"),
        ("co_web", "Website"), ("co_ice", "ICE"), ("co_tax", "IF (Tax ID)"),
        ("co_tp", "TP"), ("co_rc", "RC"), ("co_cnss", "CNSS"),
    ]
    for key, label in labels:
        fields[key] = ft.TextField(label=label, width=400, border_radius=8,
                                   focused_border_color=PRIMARY)

    fields["co_currency"] = ft.Dropdown(label="Currency", value="MAD", width=400, options=[
        ft.dropdown.Option("MAD", "MAD - Moroccan Dirham"), ft.dropdown.Option("EUR", "EUR - Euro"),
        ft.dropdown.Option("USD", "USD - Dollar"),
    ])

    logo_path = ft.TextField(label="Logo Path (optional)", width=400, border_radius=8, focused_border_color=PRIMARY)

    adm_user = ft.TextField(label="Admin Username *", width=400, border_radius=8, focused_border_color=PRIMARY)
    adm_pass = ft.TextField(label="Admin Password *", password=True, can_reveal_password=True, width=400, border_radius=8, focused_border_color=PRIMARY)
    adm_name = ft.TextField(label="Admin Full Name *", width=400, border_radius=8, focused_border_color=PRIMARY)

    section_toggles = {}
    section_keys = [
        ("header_company_info", "Company Info (Logo+Name+Address+Email+ICE)"),
        ("header_customer_info", "Customer Info (Name+Address)"),
        ("body_title", "Title: INVOICE + Number + Date"),
        ("body_attention", "Attention To"),
        ("body_items_table", "Items Table"),
        ("body_note1", "Note 1"),
        ("body_note2", "Note 2"),
        ("footer_left", "Footer Left (Name+Address+Phone+Email)"),
        ("footer_right", "Footer Right (IF+TP+RC)"),
    ]
    for key, label in section_keys:
        section_toggles[key] = ft.Switch(label=label, value=True, active_color=PRIMARY)

    error_txt = ft.Text("", color=ft.Colors.RED, size=13)

    def do_save(e):
        try:
            if not fields["co_name"].value or not adm_user.value or not adm_pass.value:
                error_txt.value = "Company name, admin username and password are required"; page.update(); return
            logo_dest = ""
            if logo_path.value:
                p = logo_path.value.strip()
                if p:
                    if os.path.isfile(p):
                        d = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "assets")
                        os.makedirs(d, exist_ok=True)
                        logo_dest = os.path.join(d, f"logo{os.path.splitext(p)[1]}")
                        try: shutil.copy2(p, logo_dest)
                        except Exception as ex: error_txt.value = f"Logo error: {ex}"; page.update(); return
                    else:
                        error_txt.value = "Logo file not found"; page.update(); return
            page.db.save_company(Company(
                name=fields["co_name"].value, address=fields["co_addr"].value,
                city=fields["co_city"].value, postal_code=fields["co_cp"].value,
                phone=fields["co_phone"].value, email=fields["co_email"].value,
                website=fields["co_web"].value, tax_id=fields["co_tax"].value,
                ice=fields["co_ice"].value, rc=fields["co_rc"].value,
                if_tax=fields["co_tax"].value, tp=fields["co_tp"].value,
                cnss=fields["co_cnss"].value,
                logo_path=logo_dest, currency=fields["co_currency"].value
            ))
            page.db.insert_user(User(username=adm_user.value, password=adm_pass.value, full_name=adm_name.value))
            page.db.create_default_invoice_template()
            existing = {s.section_key: s for s in page.db.get_template_sections("invoice")}
            for key, sw in section_toggles.items():
                if key in existing:
                    existing[key].is_visible = sw.value
                    page.db.save_template_section(existing[key])
            navigate("/login")
        except Exception as ex:
            import traceback
            traceback.print_exc()
            error_txt.value = f"Error: {ex}"
            page.update()

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
            ft.Text("Welcome to mobile Invoicing", size=22, weight=ft.FontWeight.BOLD, color=PRIMARY),
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
                    fields["co_ice"], fields["co_tax"], fields["co_tp"], fields["co_rc"], fields["co_cnss"],
                    ft.Divider(height=12, color="transparent"),
                    fields["co_currency"],
                    ft.Divider(height=12, color="transparent"),
                    ft.Text("Admin Account", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY),
                    adm_name, adm_user, adm_pass,
                    ft.Divider(height=16, color="transparent"),
                    ft.Text("Invoice Template Sections", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY),
                    ft.Text("Enable or disable invoice layout sections:", size=12, color=TEXT_SECONDARY),
                    ft.Container(height=4),
                    *[section_toggles[k] for k, _ in section_keys],
                    ft.Column([
                        logo_path,
                        error_txt,
                        ft.Container(height=8),
                        ft.Button("Save & Continue", width=200, height=48, on_click=do_save,
                            style=ft.ButtonStyle(bgcolor=PRIMARY, color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=10), elevation=2)),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ]),
                bgcolor=ft.Colors.WHITE, padding=24, border_radius=16,
                shadow=ft.BoxShadow(blur_radius=12, color="rgba(0,0,0,0.06)", offset=ft.Offset(0, 2)),
            ),
        ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20, expand=True,
    ))
    page.update()
