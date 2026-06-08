import flet as ft
from app.theme import PRIMARY, PRIMARY_LIGHT, SECONDARY, CARD_BG, TEXT_SECONDARY, WARNING, border_all
from app.i18n import tr


def dashboard_view(page, navigate):
    company = page.db.get_company()
    stats = page.db.get_dashboard_stats()
    products, customers, quotes, invoices, pending, revenue, delivery_notes, payments_count, low_stock = stats

    def logout(e):
        page.session.store.set("user_id", None); navigate("/login")

    def dash_card(title, value, icon, color, route):
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(icon, size=44, color=ft.Colors.WHITE),
                    bgcolor=color, padding=14, border_radius=14,
                ),
                ft.Container(height=8),
                ft.Row([
                    ft.Text(str(value), size=22, weight=ft.FontWeight.BOLD, color="#1A1A2E"),
                    ft.Text(title, size=11, color=TEXT_SECONDARY),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=16, bgcolor=CARD_BG, border_radius=14, ink=True,
            on_click=lambda e: navigate(route), expand=True,
            shadow=ft.BoxShadow(blur_radius=8, color="rgba(0,0,0,0.05)", offset=ft.Offset(0, 2)),
            border=border_all(1, "#E5E7EB"),
        )

    page.controls.clear()
    page.bgcolor = "#F0F2F5"
    page.add(ft.Column([
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(tr(page, "mobile_invoicing"), size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.IconButton(ft.Icons.LOGOUT, icon_color=ft.Colors.WHITE_70, on_click=logout),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(company.name if company else tr(page, "my_company"), size=15, color=ft.Colors.WHITE_70),
                ft.Divider(color="rgba(255,255,255,0.15)", height=20),
                ft.Row([
                    ft.Column([
                        ft.Text(tr(page, "revenue"), size=11, color=ft.Colors.WHITE_54),
                        ft.Text(f"{(company.currency + ' ' if company else '')}{revenue:,.0f}", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ]),
                    ft.Column([
                        ft.Text(tr(page, "pending"), size=11, color=ft.Colors.WHITE_54),
                        ft.Text(f"{pending} {tr(page, 'invoices_count')}", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ], horizontal_alignment=ft.CrossAxisAlignment.END),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=4),
            padding=ft.Padding(left=20, top=16, right=10, bottom=20),
            bgcolor=PRIMARY,
            shadow=ft.BoxShadow(blur_radius=6, color="rgba(0,0,0,0.2)", offset=ft.Offset(0, 3)),
        ),
        ft.Container(
            content=ft.Column([
                ft.Container(height=6),
                ft.Row([dash_card(tr(page, "products"), products, ft.Icons.INVENTORY, "#2563EB", "/products"),
                        dash_card(tr(page, "customers"), customers, ft.Icons.PEOPLE, "#059669", "/customers")], spacing=12),
                ft.Row([dash_card(tr(page, "quotes"), quotes, ft.Icons.DESCRIPTION, "#D97706", "/quotes"),
                        dash_card(tr(page, "invoices"), invoices, ft.Icons.RECEIPT, "#7C3AED", "/invoices")], spacing=12),
                ft.Row([dash_card(tr(page, "bl"), delivery_notes, ft.Icons.LOCAL_SHIPPING, "#0891B2", "/delivery_notes"),
                        dash_card(tr(page, "payments"), payments_count, ft.Icons.PAYMENTS, "#DC2626", "/payments")], spacing=12),
                ft.Row([dash_card(tr(page, "low_stock"), low_stock, ft.Icons.WARNING_AMBER, WARNING, "/products")], spacing=12),
            ], spacing=8),
            padding=ft.Padding(left=16, right=16, top=0, bottom=0), expand=True,
        ),
    ], expand=True, spacing=0))
    page.update()
