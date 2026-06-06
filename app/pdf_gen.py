import os
from datetime import datetime
from fpdf import FPDF

PDF_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pdfs")


def ensure_pdf_dir():
    os.makedirs(PDF_DIR, exist_ok=True)


class DocTemplate:
    def __init__(self, company=None):
        self.company = company
        self.header = ""
        self.footer = ""
        self.title = ""
        self.columns = []
        self.notes_label = "Notes:"

    def build(self, items, total_ht, total_ttc, notes=""):
        pdf = FPDF()
        pdf.add_page()

        # Header with company info
        if self.company:
            c = self.company
            col_left = 10
            col_right = 110
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_xy(col_left, 10)
            pdf.cell(0, 8, c.name)

            # Logo
            if c.logo_path and os.path.exists(c.logo_path):
                try:
                    pdf.image(c.logo_path, x=160, y=8, w=40)
                except Exception:
                    pass

            pdf.set_xy(col_left, 20)
            pdf.set_font("Helvetica", "", 8)
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

        # Custom header text
        if self.header:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, self.header)
            pdf.ln(3)

        # Title
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, self.title, new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)

        # Items table
        col_w = [10, 70, 20, 30, 30, 30]
        headers = ["#", "Product", "Qty", "Unit Price", "Total HT", "Total TTC"]
        if self.columns:
            headers = self.columns

        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(41, 101, 191)
        pdf.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            pdf.cell(col_w[i], 8, h, border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 9)
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

        # Totals
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, f"Total HT: {total_ht:.2f}", new_x="LMARGIN", new_y="NEXT", align="R")
        pdf.cell(0, 7, f"Total TTC: {total_ttc:.2f}", new_x="LMARGIN", new_y="NEXT", align="R")

        # Notes
        if notes:
            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, f"{self.notes_label} {notes}", new_x="LMARGIN", new_y="NEXT")

        # Footer
        if self.footer:
            pdf.ln(10)
            pdf.set_font("Helvetica", "I", 8)
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


def generate_invoice_pdf(company, invoice, items, payments=None, total_paid=0):
    ensure_pdf_dir()
    tpl = DocTemplate(company)
    tpl.title = f"FACTURE - {invoice.invoice_number}"
    tpl.notes_label = "Notes:"
    balance = invoice.total_ttc - total_paid
    status_text = {
        "completed": "PAYEE", "draft": "BROUILLON",
        "sent": "ENVOYEE",
        "partial": f"PAIEMENT PARTIEL - Restant: {balance:.2f}"
    }.get(invoice.status, invoice.status)
    tpl.header = (
        f"Client ID: {invoice.customer_id}\n"
        f"Date: {invoice.date}\n"
        f"Due date: {invoice.due_date}\n"
        f"Status: {status_text}"
    )
    pdf = tpl.build(items, invoice.total_ht, invoice.total_ttc, invoice.notes)

    if payments:
        pdf.ln(10)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, "Payment History:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        for p in payments:
            pdf.cell(0, 6, f"{p.date} - {p.amount:.2f} ({p.method})", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, f"Total Paid: {total_paid:.2f}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, f"Balance Due: {balance:.2f}", new_x="LMARGIN", new_y="NEXT")

    path = os.path.join(PDF_DIR, f"invoice_{invoice.invoice_number}.pdf")
    pdf.output(path)
    return path
