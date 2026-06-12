import flet as ft
from app.shared.db import Database
from app.fe.mobile.widgets.theme import apply_theme

from app.fe.mobile.screens.login_screen import login_view
from app.fe.mobile.screens.setup_screen import setup_view
from app.fe.mobile.screens.dashboard_screen import dashboard_view
from app.fe.mobile.screens.products_screen import products_view, product_form_view
from app.fe.mobile.screens.customers_screen import customers_view, customer_form_view
from app.fe.mobile.screens.quotes_screen import quotes_view, quote_form_view, quote_view_view
from app.fe.mobile.screens.delivery_notes_screen import delivery_notes_view, delivery_note_view_view
from app.fe.mobile.screens.invoices_screen import invoices_view, invoice_view_view, invoice_pdf_view
from app.fe.mobile.screens.payments_screen import payments_view


def main(page: ft.Page):
    page.title = "Mobile Invoice"
    page.theme_mode = ft.ThemeMode.LIGHT
    apply_theme(page)
    page.db = Database()
    page.window.width = 420
    page.window.height = 760

    def navigate(route):
        try:
            page.session.store.set("current_route", route)
            page.controls.clear()
            page.overlay.clear()
            if route in ("/", "/login"):
                company = page.db.get_company()
                first_user = page.db.get_first_user()
                if not company or not first_user:
                    setup_view(page, navigate)
                else:
                    login_view(page, navigate)
            elif page.session.store.get("user_id") is None:
                navigate("/login")
            elif route == "/dashboard":
                dashboard_view(page, navigate)
            elif route == "/products":
                products_view(page, navigate)
            elif route == "/add_product":
                product_form_view(page, navigate)
            elif route.startswith("/edit_product/"):
                product_form_view(page, navigate, product_id=int(route.split("/")[-1]))
            elif route == "/customers":
                customers_view(page, navigate)
            elif route == "/add_customer":
                customer_form_view(page, navigate)
            elif route.startswith("/edit_customer/"):
                customer_form_view(page, navigate, customer_id=int(route.split("/")[-1]))
            elif route == "/quotes":
                quotes_view(page, navigate)
            elif route == "/add_quote":
                quote_form_view(page, navigate)
            elif route.startswith("/edit_quote/"):
                quote_form_view(page, navigate, quote_id=int(route.split("/")[-1]))
            elif route.startswith("/view_quote/"):
                quote_view_view(page, navigate, int(route.split("/")[-1]))
            elif route == "/delivery_notes":
                delivery_notes_view(page, navigate)
            elif route.startswith("/view_delivery_note/"):
                delivery_note_view_view(page, navigate, int(route.split("/")[-1]))
            elif route == "/invoices":
                invoices_view(page, navigate)
            elif route.startswith("/view_invoice/"):
                invoice_view_view(page, navigate, int(route.split("/")[-1]))
            elif route.startswith("/view_invoice_pdf/"):
                invoice_pdf_view(page, navigate, int(route.split("/")[-1]))
            elif route == "/payments":
                payments_view(page, navigate)
            else:
                navigate("/dashboard")
        except Exception as ex:
            import traceback
            page.controls.clear()
            page.add(ft.Text(f"Error: {ex}", color=ft.Colors.RED))
            page.add(ft.Text(traceback.format_exc(), size=10))
            traceback.print_exc()
            page.update()

    page.navigate = navigate
    navigate("/")


if __name__ == "__main__":
    ft.run(main, assets_dir="app/fe/mobile/assets")
