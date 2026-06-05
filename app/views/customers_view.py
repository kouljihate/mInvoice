import flet as ft
from app.ui_helper import make_appbar, card
from app.theme import PRIMARY, BACKGROUND


def customers_view(page, navigate):
    def load():
        customers = page.db.get_all_customers()
        rows.controls.clear()
        if not customers:
            rows.controls.append(ft.Text("No customers yet. Tap + to add.", color="#6B7280"))
        else:
            for c in customers:
                rows.controls.append(card(
                    ft.Row([
                        ft.Container(
                            content=ft.Text(c.name[0].upper(), size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            bgcolor=PRIMARY, padding=12, border_radius=10, width=44, height=44, alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column([
                            ft.Text(c.name, weight=ft.FontWeight.BOLD, size=15, color="#1A1A2E"),
                            ft.Text(c.phone if c.phone else c.email, size=12, color="#6B7280"),
                        ], expand=True, spacing=2),
                        ft.IconButton(ft.Icons.EDIT, icon_color="#2563EB", icon_size=20,
                                      on_click=lambda e, cid=c.id: navigate(f"/edit_customer/{cid}")),
                        ft.IconButton(ft.Icons.DELETE, icon_color="#DC2626", icon_size=20,
                                      on_click=lambda e, cid=c.id: delete(cid)),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ))
        page.update()

    def delete(cid):
        page.db.delete_customer(cid); load()

    rows = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    page.controls.clear()
    page.bgcolor = BACKGROUND
    page.add(ft.Column([
        make_appbar(page, navigate, "Customers", back_route="/dashboard",
                    actions=[ft.IconButton(ft.Icons.ADD, icon_color=ft.Colors.WHITE, on_click=lambda e: navigate("/add_customer"))]),
        ft.Container(content=rows, expand=True, padding=16),
    ], expand=True, spacing=0))
    page.update()
    load()


def customer_form_view(page, navigate, customer_id=None):
    name_f = ft.TextField(label="Customer Name *", width=400, border_radius=8, focused_border_color=PRIMARY)
    addr_f = ft.TextField(label="Address", width=400, multiline=True, min_lines=2, border_radius=8, focused_border_color=PRIMARY)
    phone_f = ft.TextField(label="Phone", width=400, border_radius=8, focused_border_color=PRIMARY)
    email_f = ft.TextField(label="Email", width=400, border_radius=8, focused_border_color=PRIMARY)
    tax_f = ft.TextField(label="Tax ID", width=400, border_radius=8, focused_border_color=PRIMARY)
    error_txt = ft.Text("", color=ft.Colors.RED, size=13)

    if customer_id:
        c = page.db.get_customer(customer_id)
        if c:
            name_f.value = c.name; addr_f.value = c.address; phone_f.value = c.phone
            email_f.value = c.email; tax_f.value = c.tax_id

    def save(e):
        if not name_f.value: error_txt.value = "Customer name is required"; page.update(); return
        from app.database import Customer
        cust = Customer(id=customer_id or 0, name=name_f.value, address=addr_f.value,
                        phone=phone_f.value, email=email_f.value, tax_id=tax_f.value)
        if customer_id: page.db.update_customer(cust)
        else: page.db.insert_customer(cust)
        navigate("/customers")

    title = "Edit Customer" if customer_id else "Add Customer"
    page.controls.clear()
    page.bgcolor = BACKGROUND
    page.add(ft.Column([
        make_appbar(page, navigate, title, back_route="/customers"),
        ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text("Customer Details", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY),
                        name_f, addr_f, phone_f, email_f, tax_f, error_txt,
                        ft.Container(height=12),
                        ft.Button("Save", width=400, height=48, on_click=save,
                            style=ft.ButtonStyle(bgcolor=PRIMARY, color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=10), elevation=2)),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.Colors.WHITE, padding=24, border_radius=16,
                    shadow=ft.BoxShadow(blur_radius=8, color="rgba(0,0,0,0.04)", offset=ft.Offset(0, 2)),
                ),
            ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=16, expand=True,
        ),
    ], expand=True, spacing=0))
    page.update()
