from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Company:
    id: int = 0
    name: str = ""
    address: str = ""
    city: str = ""
    postal_code: str = ""
    phone: str = ""
    email: str = ""
    website: str = ""
    tax_id: str = ""
    ice: str = ""
    rc: str = ""
    if_tax: str = ""
    tp: str = ""
    cnss: str = ""
    logo_path: str = ""
    bank_account: str = ""
    slogan: str = ""
    currency: str = "MAD"


@dataclass
class User:
    id: int = 0
    username: str = ""
    password: str = ""
    full_name: str = ""


@dataclass
class Product:
    id: int = 0
    name: str = ""
    description: str = ""
    reference: str = ""
    unit_price: float = 0.0
    quantity: int = 0
    alert_stock: int = 0
    unit: str = "piece"
    package_type: str = ""
    photo_path: str = ""


@dataclass
class Customer:
    id: int = 0
    name: str = ""
    customer_type: str = "private"
    address: str = ""
    phone: str = ""
    email: str = ""
    tax_id: str = ""
    rc: str = ""
    if_tax: str = ""
    cnss: str = ""
    photo_path: str = ""


@dataclass
class Quote:
    id: int = 0
    quote_number: str = ""
    customer_id: int = 0
    customer_name: str = ""
    date: str = ""
    valid_until: str = ""
    status: str = "draft"
    notes: str = ""
    template: str = "default"
    total_ht: float = 0.0
    total_ttc: float = 0.0
    pdf_path: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class QuoteItem:
    id: int = 0
    quote_id: int = 0
    product_id: int = 0
    product_name: str = ""
    quantity: int = 0
    unit_price: float = 0.0
    tva_rate: float = 0.0

    @property
    def total_ht(self):
        return self.quantity * self.unit_price

    @property
    def total_ttc(self):
        return self.total_ht * (1 + self.tva_rate / 100)


@dataclass
class DeliveryNote:
    id: int = 0
    delivery_number: str = ""
    quote_id: int = 0
    customer_id: int = 0
    customer_name: str = ""
    date: str = ""
    notes: str = ""
    total_ht: float = 0.0
    total_ttc: float = 0.0
    pdf_path: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Invoice:
    id: int = 0
    invoice_number: str = ""
    quote_id: int = 0
    delivery_note_id: int = 0
    customer_id: int = 0
    customer_name: str = ""
    date: str = ""
    due_date: str = ""
    status: str = "draft"
    notes: str = ""
    note1: str = ""
    note2: str = ""
    total_ht: float = 0.0
    total_tva: float = 0.0
    total_ttc: float = 0.0
    pdf_path: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class InvoiceItem:
    id: int = 0
    invoice_id: int = 0
    product_id: int = 0
    product_name: str = ""
    quantity: int = 0
    unit_price: float = 0.0
    tva_rate: float = 0.0

    @property
    def total_ht(self):
        return self.quantity * self.unit_price

    @property
    def total_ttc(self):
        return self.total_ht * (1 + self.tva_rate / 100)


@dataclass
class Template:
    doc_type: str = ""
    header_text: str = ""
    footer_text: str = ""


@dataclass
class TemplateSection:
    id: int = 0
    doc_type: str = "invoice"
    section_key: str = ""
    section_name: str = ""
    parent_group: str = ""
    position: int = 0
    is_visible: bool = True
    content_type: str = "fields"
    fields_config: str = "[]"
    custom_text: str = ""
    font_size: float = 10.0
    font_style: str = "normal"
    text_align: str = "left"


@dataclass
class Payment:
    id: int = 0
    payment_number: str = ""
    invoice_id: int = 0
    amount: float = 0.0
    date: str = ""
    method: str = "cash"
    reference: str = ""
    notes: str = ""
    status: str = "draft"
    created_at: str = ""
    updated_at: str = ""


DEFAULT_INVOICE_SECTIONS = [
    ("header_company_info", "Company Info (Logo+Name+Address+Email+ICE)", "header", 1, "fields", '["logo","name","address","email","ice"]', "", 9, "normal", "left"),
    ("header_customer_info", "Customer Info (Name+Address)", "header", 2, "fields", '["name","address"]', "", 9, "normal", "left"),
    ("body_title", "Title: INVOICE + Number + Date", "body", 3, "text", "[]", "INVOICE {number} - {date}", 14, "bold", "center"),
    ("body_attention", "Attention To", "body", 4, "fields", '["attention"]', "", 10, "normal", "left"),
    ("body_items_table", "Items Table (SKU+Item+Qty+Price+Package+Total)", "body", 5, "table", '["sku","name","qty","price","package","total"]', "", 9, "normal", "left"),
    ("body_note1", "Note 1 (entered during creation)", "body", 6, "text", "[]", "{note1}", 9, "normal", "left"),
    ("body_note2", "Note 2 (entered during creation)", "body", 7, "text", "[]", "{note2}", 9, "normal", "left"),
    ("footer_left", "Footer Left (Name+Address+Phone+Email)", "footer", 8, "fields", '["name","address","phone","email"]', "", 8, "normal", "left"),
    ("footer_right", "Footer Right (IF+TP+RC)", "footer", 9, "fields", '["if_tax","tp","rc"]', "", 8, "normal", "right"),
]
