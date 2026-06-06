# mInvoice — AI Coding Assistant Prompt

You are working on **mInvoice**, a mobile-friendly desktop invoicing app for Moroccan small businesses, built with **Python + Flet** (Flutter-based UI framework) and **SQLite**.

## Stack
- **UI:** Flet (Python → Flutter widgets, windowed at 420×760)
- **Database:** SQLite via raw SQL + dataclass models (`app/database.py`)
- **PDF:** fpdf2 with company branding, items tables, payment history (`app/pdf_gen.py`)
- **Theming:** Custom color palette (navy primary `#1B2A4A`, gold secondary `#C8A84E`), Comfortaa font (`app/theme.py`)

## Project Structure
```
main.py              # Entry point, routing, page init
seed_data.py         # Generates 100 products + 100 customers (Moroccan-themed)
app/
  __init__.py        # __version__ = "1.0.0"
  database.py        # All models (dataclasses) + Database class with full CRUD
  theme.py           # Colors, fonts, reusable components (top_bar, card, badge, button, field)
  ui_helper.py       # Higher-level UI helpers (appbar, card, badge, button, field)
  pdf_gen.py         # DocTemplate builder + generate_quote_pdf/dn_pdf/invoice_pdf
  static/            # Assets dir for images, etc.
  views/
    login_view.py          # Login with username/password
    setup_view.py          # First-run company + user setup
    dashboard_view.py      # Stats cards, revenue, pending invoices
    products_view.py       # List + CRUD form (product_form_view)
    customers_view.py      # List + CRUD form (customer_form_view)
    quotes_view.py         # List + form + view (quote_form_view, quote_view_view)
    delivery_notes_view.py # List + view (delivery_note_view_view)
    invoices_view.py       # List + view + PDF view (invoice_view_view, invoice_pdf_view)
    payments_view.py       # Payments list
    template_editor.py     # Custom header/footer per doc type
    template_view.py       # Template usage in doc viewing
```

## Data Models (all in `app/database.py`)
- **Company** — name, address, city, postal_code, phone, email, website, tax_id, ice, rc, if_tax, cnss, logo_path, currency (default MAD). Singleton (id=1).
- **User** — id, username, password, full_name
- **Product** — id, name, description, reference, unit_price, quantity (stock), unit, package_type, photo_path
- **Customer** — id, name, address, phone, email, tax_id
- **Quote** — id, quote_number, customer_id, date, valid_until, status (draft/validated/sent/confirmed/cancelled), notes, template, total_ht, total_ttc, pdf_path
- **QuoteItem** — id, quote_id, product_id, product_name, quantity, unit_price, tva_rate (has total_ht/total_ttc computed properties)
- **DeliveryNote** — id, delivery_number, quote_id, customer_id, date, notes, total_ht, total_ttc, pdf_path
- **Invoice** — id, invoice_number, quote_id, delivery_note_id, customer_id, date, due_date, status (unpaid/partial/paid), notes, total_ht, total_tva, total_ttc, pdf_path
- **InvoiceItem** — id, invoice_id, product_id, product_name, quantity, unit_price, tva_rate (has total_ht/total_ttc computed properties)
- **Payment** — id, invoice_id, amount, date, method (cash/check/bank_transfer/card), reference, notes
- **Template** — doc_type (PK), header_text, footer_text

## Key Conventions
- **Routing:** Custom `page.navigate(route)` function in `main.py`. Routes are hardcoded strings (not Flet's built-in router). View functions follow this signature:
  ```python
  def view_name(page, navigate, optional_param=None):
  ```
- **State:** `page.db` holds the `Database` instance. `page.session.store` holds `user_id` and `username`.
- **Page Building:** Each view clears `page.controls` and `page.overlay`, then adds new controls and calls `page.update()`.
- **UI Components:** Use helpers from `app/theme.py` and `app/ui_helper.py` (top_bar/make_appbar, card, status_badge, primary_button, styled_field, section_title).
- **Values:** Prices in float, amounts use 2 decimal places. Currency display uses `company.currency` (default "MAD").
- **PDFs:** Generated to `pdfs/` directory. Path stored in db record. Invoice PDF includes payment history + balance.
- **Stock:** `decrease_stock()` method checks `quantity >= qty` before reducing.

## Running
```bash
pip install -r requirements.txt
python main.py            # Launch app
python seed_data.py       # Populate demo data (clears existing products/customers)
```

## Patterns to Follow
1. Always clear `page.controls` and `page.overlay` at the start of a view.
2. Use `top_bar` or `make_appbar` for navigation headers.
3. Wrap content in a `ft.Container` or `ft.Column` with scrolling for mobile-friendly layout.
4. Use `card()` for list items, `status_badge()` for status display.
5. Database operations go through `page.db` methods.
6. When adding new routes, add them in `main.py navigate()` function.
7. Keep view functions in separate files under `app/views/`.
8. Follow Moroccan business context (ICE, RC, IF, CNSS tax fields, MAD currency).
