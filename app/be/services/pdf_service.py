import os
import json
from datetime import datetime
from fpdf import FPDF

PDF_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pdfs")
FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")
def ensure_pdf_dir():
    os.makedirs(PDF_DIR, exist_ok=True)


def _ensure_fonts():
    os.makedirs(FONTS_DIR, exist_ok=True)
    regular = os.path.join(FONTS_DIR, "Comfortaa-Regular.ttf")
    bold = os.path.join(FONTS_DIR, "Comfortaa-Bold.ttf")
    if os.path.exists(regular) and os.path.exists(bold):
        return True
    try:
        import urllib.request
        url = "https://github.com/google/fonts/raw/main/ofl/comfortaa/Comfortaa%5Bwght%5D.ttf"
        if not os.path.exists(regular):
            urllib.request.urlretrieve(url, regular)
        if not os.path.exists(bold):
            import shutil
            shutil.copy2(regular, bold)
        return True
    except Exception:
        return False


def _try_add_fonts(pdf):
    _ensure_fonts()
    comfortaa_regular = os.path.join(FONTS_DIR, "Comfortaa-Regular.ttf")
    comfortaa_bold = os.path.join(FONTS_DIR, "Comfortaa-Bold.ttf")
    if os.path.exists(comfortaa_regular) and os.path.exists(comfortaa_bold):
        pdf.add_font("Comfortaa", "", comfortaa_regular, uni=True)
        pdf.add_font("Comfortaa", "B", comfortaa_bold, uni=True)
        return True
    return False


def _use_font(pdf, style="", size=10):
    if hasattr(pdf, "_comfortaa_loaded") and pdf._comfortaa_loaded:
        pdf.set_font("Comfortaa", style, size)
    else:
        pdf.set_font("Helvetica", style, size)


class DocTemplate:
    def __init__(self, company=None):
        self.company = company
        self.header = ""
        self.footer = ""
        self.title = ""
        self.columns = []
        self.notes_label = "Notes:"

    def _init_pdf(self):
        pdf = FPDF()
        pdf._comfortaa_loaded = _try_add_fonts(pdf)
        return pdf

    def build(self, items, total_ht, total_ttc, notes=""):
        pdf = self._init_pdf()
        pdf.add_page()

        if self.company:
            c = self.company
            col_left = 10
            _use_font(pdf, "B", 14)
            pdf.set_xy(col_left, 10)
            pdf.cell(0, 8, c.name)

            if c.logo_path and os.path.exists(c.logo_path):
                try:
                    pdf.image(c.logo_path, x=160, y=8, w=40)
                except Exception:
                    pass

            _use_font(pdf, "", 8)
            y = 20
            if c.address:
                addr = c.address
                if c.city: addr += f", {c.city}"
                if c.postal_code: addr += f" {c.postal_code}"
                pdf.set_xy(col_left, y); pdf.cell(0, 4, addr); y += 4
            if c.phone:
                pdf.set_xy(col_left, y); pdf.cell(0, 4, f"Tel: {c.phone}"); y += 4
            if c.email:
                pdf.set_xy(col_left, y); pdf.cell(0, 4, f"Email: {c.email}"); y += 4
            if c.website:
                pdf.set_xy(col_left, y); pdf.cell(0, 4, f"Web: {c.website}"); y += 4
            if c.ice:
                pdf.set_xy(col_left, y); pdf.cell(0, 4, f"ICE: {c.ice}"); y += 4
            if c.rc:
                pdf.set_xy(col_left, y); pdf.cell(0, 4, f"RC: {c.rc}"); y += 4
            if c.if_tax or c.tax_id:
                tid = c.if_tax or c.tax_id
                pdf.set_xy(col_left, y); pdf.cell(0, 4, f"IF: {tid}"); y += 4
            if c.cnss:
                pdf.set_xy(col_left, y); pdf.cell(0, 4, f"CNSS: {c.cnss}"); y += 4

        pdf.set_y(max(y + 5, 55))

        if self.header:
            _use_font(pdf, "", 10)
            pdf.multi_cell(0, 5, self.header)
            pdf.ln(3)

        _use_font(pdf, "B", 14)
        pdf.cell(0, 10, self.title, new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)

        col_w = [10, 70, 20, 30, 30, 30]
        headers = ["#", "Product", "Qty", "Unit Price", "Total HT", "Total TTC"]
        if self.columns:
            headers = self.columns

        _use_font(pdf, "B", 9)
        pdf.set_fill_color(41, 101, 191)
        pdf.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            pdf.cell(col_w[i], 8, h, border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_text_color(0, 0, 0)
        _use_font(pdf, "", 9)
        for idx, item in enumerate(items):
            row = [
                str(idx + 1),
                item.product_name[:40],
                str(item.quantity),
                f"{item.unit_price:.2f}",
                f"{item.total_ht:.2f}",
                f"{item.total_ttc:.2f}"
            ]
            for i, val in enumerate(row):
                pdf.cell(col_w[i], 7, val, border=1, align="C" if i != 1 else "L")
            pdf.ln()

        pdf.ln(5)
        _use_font(pdf, "B", 10)
        pdf.cell(0, 7, f"Total HT: {total_ht:.2f}", new_x="LMARGIN", new_y="NEXT", align="R")
        pdf.cell(0, 7, f"Total TTC: {total_ttc:.2f}", new_x="LMARGIN", new_y="NEXT", align="R")

        if notes:
            pdf.ln(5)
            _use_font(pdf, "B", 10)
            pdf.cell(0, 7, f"{self.notes_label} {notes}", new_x="LMARGIN", new_y="NEXT")

        if self.footer:
            pdf.ln(10)
            _use_font(pdf, "I", 8)
            pdf.multi_cell(0, 5, self.footer)

        return pdf


def generate_quote_pdf(company, quote, items):
    ensure_pdf_dir()
    tpl = DocTemplate(company)
    tpl.title = f"DEVIS - {quote.quote_number}"
    tpl.notes_label = "Notes:"
    tpl.header = f"Client ID: {quote.customer_id}\nDate: {quote.date}\nValid until: {quote.valid_until}"
    pdf = tpl.build(items, quote.total_ht, quote.total_ttc, quote.notes)
    path = os.path.join(PDF_DIR, f"quote_{quote.quote_number}.pdf")
    pdf.output(path)
    return path


def generate_dn_pdf(company, dn, items):
    ensure_pdf_dir()
    tpl = DocTemplate(company)
    tpl.title = f"BON DE LIVRAISON - {dn.delivery_number}"
    tpl.notes_label = "Notes:"
    tpl.header = f"Client ID: {dn.customer_id}\nDate: {dn.date}"
    pdf = tpl.build(items, dn.total_ht, dn.total_ttc, dn.notes)
    path = os.path.join(PDF_DIR, f"bl_{dn.delivery_number}.pdf")
    pdf.output(path)
    return path


_FIELD_RESOLVERS = {"name", "address", "phone", "email", "ice", "if_tax", "tp", "rc", "cnss", "website", "logo"}


def _resolve_field(field, company, customer):
    if field == "logo":
        return ""
    if company and field in _FIELD_RESOLVERS:
        return getattr(company, field, "")
    if customer and field in ("name", "address", "contact"):
        if field == "contact":
            return getattr(customer, "contact", getattr(customer, "email", ""))
        return getattr(customer, field, "")
    return ""


def _render_section(pdf, section, company=None, customer=None, invoice=None, items=None, note1="", note2=""):
    if not section.is_visible:
        return pdf.get_y()

    skey = section.section_key
    _use_font(pdf, section.font_style, section.font_size)

    x = pdf.l_margin if section.text_align != "right" else pdf.w - pdf.r_margin - 60
    align = {"left": "L", "center": "C", "right": "R"}.get(section.text_align, "L")

    if skey == "header_company_info":
        fields = json.loads(section.fields_config)
        pdf.ln(2)
        for f in fields:
            if f == "logo" and company and company.logo_path and os.path.exists(company.logo_path):
                try:
                    pdf.image(company.logo_path, x=x, y=pdf.get_y(), w=30)
                    pdf.ln(12)
                except Exception:
                    pass
            else:
                val = _resolve_field(f, company, customer)
                if val:
                    pdf.set_x(x)
                    pdf.cell(0, 5, str(val), new_x="LMARGIN", new_y="NEXT", align=align)

    elif skey == "header_customer_info":
        pdf.ln(4)
        _use_font(pdf, "B", section.font_size)
        pdf.cell(0, 5, "Client:", new_x="LMARGIN", new_y="NEXT")
        _use_font(pdf, section.font_style, section.font_size)
        fields = json.loads(section.fields_config)
        for f in fields:
            val = _resolve_field(f, company, customer)
            if val:
                pdf.set_x(x)
                pdf.cell(0, 5, str(val), new_x="LMARGIN", new_y="NEXT", align=align)

    elif skey == "body_title":
        pdf.ln(6)
        text = section.custom_text
        if invoice:
            text = text.replace("{number}", invoice.invoice_number).replace("{date}", invoice.date)
        _use_font(pdf, section.font_style, section.font_size)
        pdf.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT", align=align)
        pdf.ln(2)

    elif skey == "body_attention":
        pdf.ln(2)
        cname = customer.name if customer else ""
        _use_font(pdf, section.font_style, section.font_size)
        pdf.cell(0, 5, f"Attention to: {cname}", new_x="LMARGIN", new_y="NEXT", align=align)

    elif skey == "body_items_table":
        pdf.ln(4)
        col_headers = ["SKU", "Item", "Qty", "Unit Price", "Package", "Total"]
        col_widths = [20, 60, 12, 25, 20, 25]
        _use_font(pdf, "B", section.font_size)
        pdf.set_fill_color(27, 42, 74)
        pdf.set_text_color(255, 255, 255)
        for i, h in enumerate(col_headers):
            pdf.cell(col_widths[i], 7, h, border=1, align="C", fill=True)
        pdf.ln()
        pdf.set_text_color(0, 0, 0)
        _use_font(pdf, section.font_style, section.font_size)
        for idx, item in enumerate(items or []):
            sku = getattr(item, "product_id", "")
            row = [
                str(sku) if sku else "",
                item.product_name[:35],
                str(item.quantity),
                f"{item.unit_price:.2f}",
                "",
                f"{item.quantity * item.unit_price:.2f}",
            ]
            for i, val in enumerate(row):
                pdf.cell(col_widths[i], 6, val, border=1, align="C" if i != 1 else "L")
            pdf.ln()

        total_ht = sum(it.quantity * it.unit_price for it in (items or []))
        tva = total_ht * 0.20
        total_ttc = total_ht + tva
        pdf.ln(4)
        _use_font(pdf, "", section.font_size)
        pdf.cell(0, 6, f"Subtotal (HT): {total_ht:.2f}", new_x="LMARGIN", new_y="NEXT", align="R")
        pdf.cell(0, 6, f"Tax (20%): {tva:.2f}", new_x="LMARGIN", new_y="NEXT", align="R")
        _use_font(pdf, "B", section.font_size + 1)
        pdf.cell(0, 7, f"Total TTC: {total_ttc:.2f}", new_x="LMARGIN", new_y="NEXT", align="R")

    elif skey == "body_note1":
        pdf.ln(3)
        text = section.custom_text.replace("{note1}", note1)
        _use_font(pdf, section.font_style, section.font_size)
        pdf.multi_cell(0, 5, text, align=align)

    elif skey == "body_note2":
        pdf.ln(2)
        text = section.custom_text.replace("{note2}", note2)
        _use_font(pdf, section.font_style, section.font_size)
        pdf.multi_cell(0, 5, text, align=align)

    elif skey == "footer_left":
        pdf.ln(4)
        fields = json.loads(section.fields_config)
        _use_font(pdf, section.font_style, section.font_size)
        for f in fields:
            val = _resolve_field(f, company, customer)
            if val:
                pdf.set_x(x)
                pdf.cell(60, 4, str(val), new_x="LMARGIN", new_y="NEXT", align="L")

    elif skey == "footer_right":
        pdf.ln(4)
        fields = json.loads(section.fields_config)
        _use_font(pdf, section.font_style, section.font_size)
        rx = pdf.w - pdf.r_margin - 60
        for f in fields:
            val = _resolve_field(f, company, customer)
            if val:
                pdf.set_x(rx)
                pdf.cell(60, 4, str(val), new_x="LMARGIN", new_y="NEXT", align="R")

    return pdf.get_y()


def generate_invoice_pdf(company, invoice, items, payments=None, total_paid=0, db=None):
    ensure_pdf_dir()
    from app.database import DEFAULT_INVOICE_SECTIONS

    pdf = FPDF()
    pdf._comfortaa_loaded = _try_add_fonts(pdf)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    customer = None
    if invoice.customer_id and db:
        customer = db.get_customer(invoice.customer_id)

    sections = None
    if db:
        sections = db.get_template_sections("invoice")

    if not sections:
        from app.database import TemplateSection
        sections = []
        for key, name, group, pos, ctype, fields, text, fsize, fstyle, align in DEFAULT_INVOICE_SECTIONS:
            sections.append(TemplateSection(
                doc_type="invoice", section_key=key, section_name=name,
                parent_group=group, position=pos, is_visible=True,
                content_type=ctype, fields_config=fields, custom_text=text,
                font_size=fsize, font_style=fstyle, text_align=align,
            ))

    note1 = ""
    note2 = ""
    if invoice.notes:
        parts = invoice.notes.split("\n---\n", 1)
        note1 = parts[0]
        if len(parts) > 1:
            note2 = parts[1]

    for sec in sections:
        _render_section(pdf, sec, company, customer, invoice, items, note1, note2)

    if payments:
        pdf.ln(6)
        _use_font(pdf, "B", 10)
        pdf.cell(0, 7, "Payment History:", new_x="LMARGIN", new_y="NEXT")
        _use_font(pdf, "", 9)
        for p in payments:
            pdf.cell(0, 6, f"{p.date} - {p.amount:.2f} ({p.method})", new_x="LMARGIN", new_y="NEXT")
        _use_font(pdf, "B", 10)
        pdf.cell(0, 7, f"Total Paid: {total_paid:.2f}", new_x="LMARGIN", new_y="NEXT")
        balance = invoice.total_ttc - total_paid
        pdf.cell(0, 7, f"Balance Due: {balance:.2f}", new_x="LMARGIN", new_y="NEXT")

    path = os.path.join(PDF_DIR, f"invoice_{invoice.invoice_number}.pdf")
    pdf.output(path)
    return path
