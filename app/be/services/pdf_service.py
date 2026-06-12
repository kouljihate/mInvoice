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


def _try_add_fonts(pdf):
    _ensure_fonts()
    regular = os.path.join(FONTS_DIR, "Comfortaa-Regular.ttf")
    bold = os.path.join(FONTS_DIR, "Comfortaa-Bold.ttf")
    if os.path.exists(regular) and os.path.exists(bold):
        pdf.add_font("Comfortaa", "", regular, uni=True)
        pdf.add_font("Comfortaa", "B", bold, uni=True)


def _use_font(pdf, style="", size=10):
    style_map = {"normal": "", "bold": "B", "italic": "I", "underline": "U"}
    mapped = style_map.get(style.lower() if style else "", style)
    pdf.set_font("Comfortaa", mapped, size)


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
        _try_add_fonts(pdf)
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


def _nombre_en_lettres(n):
    if n == 0:
        return "zéro"
    units = ["", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf",
             "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize",
             "dix-sept", "dix-huit", "dix-neuf"]
    tens = ["", "", "vingt", "trente", "quarante", "cinquante", "soixante",
            "soixante-dix", "quatre-vingt", "quatre-vingt-dix"]
    def _lt1000(num):
        parts = []
        if num >= 100:
            h = num // 100
            parts.append("cent" if h == 1 else f"{units[h]}-cent")
            num %= 100
        if num >= 20:
            t = num // 10
            u = num % 10
            if t < 7 or t == 8:
                base = tens[t]
                if u == 0:
                    parts.append("quatre-vingts" if t == 8 else base)
                elif u == 1:
                    parts.append(f"{base}-et-un" if t > 1 else "onze")
                else:
                    parts.append(f"{base}-{units[u]}")
            elif t == 7:
                parts.append(f"soixante-{units[10 + u]}" if u > 0 else "soixante-dix")
            elif t == 9:
                parts.append(f"quatre-vingt-{units[10 + u]}")
        elif num > 0:
            parts.append(units[num])
        return "-".join(parts).replace("--", "-")
    if n >= 1000000:
        m = n // 1000000
        r = n % 1000000
        s = "un million" if m == 1 else f"{_lt1000(m)} millions"
        return s + (f" {_nombre_en_lettres(r)}" if r > 0 else "")
    if n >= 1000:
        th = n // 1000
        r = n % 1000
        s = "mille" if th == 1 else f"{_lt1000(th)} mille"
        return s + (f" {_lt1000(r)}" if r > 0 else "")
    return _lt1000(n)


def generate_invoice_pdf(company, invoice, items, payments=None, total_paid=0, db=None):
    ensure_pdf_dir()

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    _try_add_fonts(pdf)
    pdf.add_page()

    A4_H = 297
    margin = 15
    footer_margin = 42
    pdf.set_auto_page_break(auto=True, margin=footer_margin)
    pdf.set_left_margin(margin)
    pdf.set_right_margin(margin)
    page_w = pdf.w - margin * 2

    customer = None
    if invoice.customer_id and db:
        customer = db.get_customer(invoice.customer_id)

    header_end_y = 15 + (A4_H - 30) * 0.20
    footer_start_y = 15 + (A4_H - 30) * 0.90

    # ═══════════════════════════════════════════
    # 1. HEADER (top 20%)
    # ═══════════════════════════════════════════

    top_y = 8

    # 1.1 Left: Logo + slogan only
    if company and company.logo_path and os.path.exists(company.logo_path):
        try:
            pdf.image(company.logo_path, x=margin, y=top_y, w=30)
        except Exception:
            pass

    slogan = company.slogan if company and company.slogan else (company.website if company else "")
    if slogan:
        _use_font(pdf, "", 8)
        pdf.set_xy(margin, top_y + 32)
        pdf.cell(page_w * 0.48, 4, slogan, align="L")

    # 1.2 Right: Customer info
    right_col_x = margin + page_w * 0.5
    right_col_w = page_w * 0.48

    if customer:
        _use_font(pdf, "B", 10)
        pdf.set_xy(right_col_x, top_y + 6)
        pdf.cell(right_col_w, 5, customer.name, align="R")

        cr_y = top_y + 13
        _use_font(pdf, "", 7)
        if customer.address:
            pdf.set_xy(right_col_x, cr_y)
            pdf.cell(right_col_w, 3.5, customer.address, align="R")
            cr_y += 3.5
        if customer.customer_type == "company":
            if hasattr(customer, "ice") and customer.ice:
                pdf.set_xy(right_col_x, cr_y)
                pdf.cell(right_col_w, 3.5, f"ICE: {customer.ice}", align="R")
                cr_y += 3.5
        else:
            if customer.email:
                pdf.set_xy(right_col_x, cr_y)
                pdf.cell(right_col_w, 3.5, customer.email, align="R")

    pdf.set_y(header_end_y)

    sy = pdf.get_y()
    pdf.set_draw_color(200, 200, 200)
    pdf.line(margin, sy, margin + page_w, sy)
    pdf.ln(4)

    # ═══════════════════════════════════════════
    # 2. BODY (middle 70%)
    # ═══════════════════════════════════════════

    # 2.1 Invoice number + date at left
    _use_font(pdf, "B", 13)
    pdf.cell(0, 7, f"INVOICE {invoice.invoice_number}", new_x="LMARGIN", new_y="NEXT", align="L")
    _use_font(pdf, "", 8)
    pdf.cell(0, 4, f"Date: {invoice.date}", new_x="LMARGIN", new_y="NEXT", align="L")
    if invoice.due_date:
        pdf.cell(0, 4, f"Due Date: {invoice.due_date}", new_x="LMARGIN", new_y="NEXT", align="L")

    # 2.2 Attention To (same area, on same row as invoice)
    if customer:
        attn_x = margin + page_w * 0.5
        contact = customer.name
        _use_font(pdf, "B", 8)
        pdf.set_xy(attn_x, pdf.get_y() - 15)
        pdf.cell(page_w * 0.48, 4, f"Attention To: {contact}", align="R")
        pdf.set_y(pdf.get_y() + 15)

    pdf.ln(2)

    # 2.3 Items table
    col_ref = 18
    col_desig = 60
    col_qty = 14
    col_price = 24
    col_pkg = 22
    col_total = page_w - col_ref - col_desig - col_qty - col_price - col_pkg
    col_widths = [col_ref, col_desig, col_qty, col_price, col_pkg, col_total]
    headers = ["Ref", "Designation", "Qty", "Unit Price", "Pkg Size", "Total HT"]

    _use_font(pdf, "B", 7)
    pdf.set_fill_color(27, 42, 74)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 6, h, border=1, align="C", fill=True)
    pdf.ln()
    pdf.set_text_color(0, 0, 0)

    _use_font(pdf, "", 7)
    for idx, item in enumerate(items or []):
        ref = ""
        pkg = ""
        if db and item.product_id:
            product = db.get_product(item.product_id)
            if product:
                ref = product.reference
                pkg = product.package_type

        row = [
            ref[:12],
            item.product_name[:34],
            str(item.quantity),
            f"{item.unit_price:.2f} MAD",
            pkg[:10],
            f"{item.quantity * item.unit_price:.2f} MAD",
        ]
        for i, val in enumerate(row):
            pdf.cell(col_widths[i], 5, val, border=1, align="C" if i != 1 else "L")
        pdf.ln()

    # 2.4 Total HT
    label_x = margin + page_w * 0.55
    val_w = page_w * 0.22

    pdf.set_x(label_x)
    _use_font(pdf, "", 8)
    pdf.cell(val_w, 5, "Total HT:", align="R")
    pdf.cell(val_w, 5, f"{invoice.total_ht:.2f} MAD", align="R", new_x="LMARGIN", new_y="NEXT")

    # 2.5 Total TTC
    pdf.set_x(label_x)
    _use_font(pdf, "B", 10)
    pdf.cell(val_w, 6, "Total TTC:", align="R")
    pdf.cell(val_w, 6, f"{invoice.total_ttc:.2f} MAD", align="R", new_x="LMARGIN", new_y="NEXT")

    # 2.6 Arrêté
    pdf.ln(2)
    total_int = int(round(invoice.total_ttc))
    cents = round((invoice.total_ttc - total_int) * 100)
    words = _nombre_en_lettres(total_int)
    if cents > 0:
        words += f" et {cents}/100"
    _use_font(pdf, "I", 8)
    pdf.cell(0, 5, f"Arrêté à la somme de : {words} ({invoice.total_ttc:.2f} MAD)", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(1)

    # 2.7 Note1 + 2.8 Note2
    pdf.ln(2)
    if invoice.note1:
        _use_font(pdf, "", 7)
        pdf.multi_cell(0, 3.5, invoice.note1)
    if invoice.note2:
        pdf.ln(1)
        _use_font(pdf, "", 7)
        pdf.multi_cell(0, 3.5, invoice.note2)

    # ═══════════════════════════════════════════
    # 3. FOOTER (bottom 10%) — 3-column layout (left/center/right)
    # ═══════════════════════════════════════════

    cy = pdf.get_y()
    if cy < footer_start_y - 5:
        pdf.set_y(footer_start_y)
    elif cy > A4_H - footer_margin:
        pdf.add_page()

    fy = pdf.get_y()
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.5)
    pdf.line(margin, fy, margin + page_w, fy)
    pdf.ln(4)

    col_w = page_w / 3

    # Left column: name + address + email + phone
    _use_font(pdf, "", 7)
    lx = margin
    if company:
        left_lines = []
        if company.name:
            left_lines.append(company.name)
        if company.address:
            addr = company.address
            if company.city:
                addr += f", {company.city}"
            if company.postal_code:
                addr += f" {company.postal_code}"
            left_lines.append(addr)
        if company.email:
            left_lines.append(f"Email: {company.email}")
        if company.phone:
            left_lines.append(f"Tel: {company.phone}")
        y = pdf.get_y()
        for line in left_lines:
            pdf.set_xy(lx, y)
            pdf.cell(col_w, 3.5, line, align="L")
            y += 3.5
        pdf.set_y(y)

    # Center column: bank account
    cx = margin + col_w
    if company and company.bank_account:
        y = pdf.get_y()
        pdf.set_xy(cx, y)
        pdf.cell(col_w, 3.5, f"Bank: {company.bank_account}", align="C")
        pdf.set_y(y + 3.5)

    # Right column: IF + RC + TP + ICE
    rx = margin + col_w * 2
    if company:
        right_lines = []
        if company.if_tax:
            right_lines.append(f"IF: {company.if_tax}")
        if company.rc:
            right_lines.append(f"RC: {company.rc}")
        if company.tp:
            right_lines.append(f"TP: {company.tp}")
        if company.ice:
            right_lines.append(f"ICE: {company.ice}")
        y = pdf.get_y()
        for line in right_lines:
            pdf.set_xy(rx, y)
            pdf.cell(col_w, 3.5, line, align="R")
            y += 3.5
        pdf.set_y(y)

    path = os.path.join(PDF_DIR, f"invoice_{invoice.invoice_number}.pdf")
    pdf.output(path)
    return path
