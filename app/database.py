import sqlite3
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "minvoice.db")


@dataclass
class Company:
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
    cnss: str = ""
    logo_path: str = ""
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


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        c.executescript("""
            CREATE TABLE IF NOT EXISTS company (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                name TEXT NOT NULL DEFAULT '',
                address TEXT DEFAULT '',
                city TEXT DEFAULT '',
                postal_code TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                website TEXT DEFAULT '',
                tax_id TEXT DEFAULT '',
                ice TEXT DEFAULT '',
                rc TEXT DEFAULT '',
                if_tax TEXT DEFAULT '',
                cnss TEXT DEFAULT '',
                logo_path TEXT DEFAULT '',
                currency TEXT DEFAULT 'MAD'
            );
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                reference TEXT DEFAULT '',
                unit_price REAL DEFAULT 0.0,
                quantity INTEGER DEFAULT 0,
                unit TEXT DEFAULT 'piece',
                package_type TEXT DEFAULT '',
                photo_path TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                tax_id TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_number TEXT NOT NULL DEFAULT '',
                customer_id INTEGER NOT NULL,
                date TEXT DEFAULT '',
                valid_until TEXT DEFAULT '',
                status TEXT DEFAULT 'draft',
                notes TEXT DEFAULT '',
                template TEXT DEFAULT 'default',
                total_ht REAL DEFAULT 0.0,
                total_ttc REAL DEFAULT 0.0,
                pdf_path TEXT DEFAULT '',
                created_at TEXT DEFAULT '',
                updated_at TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS quote_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id INTEGER NOT NULL,
                product_id INTEGER DEFAULT 0,
                product_name TEXT DEFAULT '',
                quantity INTEGER DEFAULT 0,
                unit_price REAL DEFAULT 0.0,
                tva_rate REAL DEFAULT 0.0
            );
            CREATE TABLE IF NOT EXISTS delivery_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                delivery_number TEXT NOT NULL DEFAULT '',
                quote_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                date TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                total_ht REAL DEFAULT 0.0,
                total_ttc REAL DEFAULT 0.0,
                pdf_path TEXT DEFAULT '',
                created_at TEXT DEFAULT '',
                updated_at TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT NOT NULL DEFAULT '',
                quote_id INTEGER NOT NULL,
                delivery_note_id INTEGER DEFAULT 0,
                customer_id INTEGER NOT NULL,
                date TEXT DEFAULT '',
                due_date TEXT DEFAULT '',
                status TEXT DEFAULT 'draft',
                notes TEXT DEFAULT '',
                total_ht REAL DEFAULT 0.0,
                total_tva REAL DEFAULT 0.0,
                total_ttc REAL DEFAULT 0.0,
                pdf_path TEXT DEFAULT '',
                created_at TEXT DEFAULT '',
                updated_at TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                product_id INTEGER DEFAULT 0,
                product_name TEXT DEFAULT '',
                quantity INTEGER DEFAULT 0,
                unit_price REAL DEFAULT 0.0,
                tva_rate REAL DEFAULT 0.0
            );
            CREATE TABLE IF NOT EXISTS templates (
                doc_type TEXT PRIMARY KEY,
                header_text TEXT DEFAULT '',
                footer_text TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payment_number TEXT NOT NULL DEFAULT '',
                invoice_id INTEGER NOT NULL,
                amount REAL DEFAULT 0.0,
                date TEXT DEFAULT '',
                method TEXT DEFAULT 'cash',
                reference TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                status TEXT DEFAULT 'draft',
                created_at TEXT DEFAULT '',
                updated_at TEXT DEFAULT ''
            );
        """)
        self.conn.commit()
        self._migrate_company()
        self._migrate_products()
        self._migrate_customers()
        self._migrate_payments()
        self._migrate_timestamps()

    def _migrate_company(self):
        c = self.conn.cursor()
        new_cols = ["city", "postal_code", "ice", "rc", "if_tax", "cnss", "logo_path"]
        for col in new_cols:
            try:
                c.execute(f"ALTER TABLE company ADD COLUMN {col} TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass
        self.conn.commit()

    def _row_to_company(self, row):
        if not row:
            return None
        return Company(
            name=row["name"], address=row["address"],
            city=row["city"] if "city" in row.keys() else "",
            postal_code=row["postal_code"] if "postal_code" in row.keys() else "",
            phone=row["phone"], email=row["email"],
            website=row["website"], tax_id=row["tax_id"],
            ice=row["ice"] if "ice" in row.keys() else "",
            rc=row["rc"] if "rc" in row.keys() else "",
            if_tax=row["if_tax"] if "if_tax" in row.keys() else "",
            cnss=row["cnss"] if "cnss" in row.keys() else "",
            logo_path=row["logo_path"] if "logo_path" in row.keys() else "",
            currency=row["currency"]
        )

    def _migrate_products(self):
        c = self.conn.cursor()
        for col in ["package_type", "photo_path", "alert_stock"]:
            try:
                dtype = "INTEGER DEFAULT 0" if col == "alert_stock" else "TEXT DEFAULT ''"
                c.execute(f"ALTER TABLE products ADD COLUMN {col} {dtype}")
            except sqlite3.OperationalError:
                pass
        self.conn.commit()

    def _migrate_customers(self):
        c = self.conn.cursor()
        for col in ["customer_type", "rc", "if_tax", "cnss", "photo_path"]:
            try:
                c.execute(f"ALTER TABLE customers ADD COLUMN {col} TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass
        self.conn.commit()

    def _migrate_payments(self):
        c = self.conn.cursor()
        for col in ["status"]:
            try:
                c.execute(f"ALTER TABLE payments ADD COLUMN {col} TEXT DEFAULT 'draft'")
            except sqlite3.OperationalError:
                pass
        self.conn.commit()

    def _migrate_timestamps(self):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        for table, cols in {"quotes": ["created_at", "updated_at"],
                            "delivery_notes": ["created_at", "updated_at"],
                            "invoices": ["created_at", "updated_at"],
                            "payments": ["payment_number", "created_at", "updated_at"]}.items():
            for col in cols:
                try:
                    c.execute(f"ALTER TABLE {table} ADD COLUMN {col} TEXT DEFAULT ''")
                except sqlite3.OperationalError:
                    pass
        self.conn.commit()

    def _next_doc_number(self, prefix):
        tables = {"Q": "quotes", "I": "invoices", "DN": "delivery_notes", "P": "payments"}
        c = self.conn.cursor()
        c.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {tables[prefix]}")
        seq = c.fetchone()[0]
        today = datetime.now().strftime("%d%m%y")
        return f"{prefix}{today}-{seq:04d}"

    def _row_to_product(self, row):
        if not row:
            return None
        return Product(id=row["id"], name=row["name"], description=row["description"],
                       reference=row["reference"], unit_price=row["unit_price"],
                       quantity=row["quantity"],
                       alert_stock=row["alert_stock"] if "alert_stock" in row.keys() else 0,
                       unit=row["unit"],
                       package_type=row["package_type"] if "package_type" in row.keys() else "",
                       photo_path=row["photo_path"] if "photo_path" in row.keys() else "")

    def _row_to_customer(self, row):
        if not row:
            return None
        return Customer(id=row["id"], name=row["name"],
                        customer_type=row["customer_type"] if "customer_type" in row.keys() else "private",
                        address=row["address"], phone=row["phone"], email=row["email"],
                        tax_id=row["tax_id"],
                        rc=row["rc"] if "rc" in row.keys() else "",
                        if_tax=row["if_tax"] if "if_tax" in row.keys() else "",
                        cnss=row["cnss"] if "cnss" in row.keys() else "",
                        photo_path=row["photo_path"] if "photo_path" in row.keys() else "")

    def _row_to_quote(self, row):
        if not row:
            return None
        return Quote(id=row["id"], quote_number=row["quote_number"],
                     customer_id=row["customer_id"], date=row["date"],
                     valid_until=row["valid_until"], status=row["status"],
                     notes=row["notes"], template=row["template"],
                     total_ht=row["total_ht"], total_ttc=row["total_ttc"],
                     pdf_path=row["pdf_path"],
                     created_at=row["created_at"] if "created_at" in row.keys() else "",
                     updated_at=row["updated_at"] if "updated_at" in row.keys() else "")

    def _row_to_quote_item(self, row):
        if not row:
            return None
        return QuoteItem(id=row["id"], quote_id=row["quote_id"],
                         product_id=row["product_id"], product_name=row["product_name"],
                         quantity=row["quantity"], unit_price=row["unit_price"],
                         tva_rate=row["tva_rate"])

    def _row_to_dn(self, row):
        if not row:
            return None
        return DeliveryNote(id=row["id"], delivery_number=row["delivery_number"],
                            quote_id=row["quote_id"], customer_id=row["customer_id"],
                            date=row["date"], notes=row["notes"],
                            total_ht=row["total_ht"], total_ttc=row["total_ttc"],
                            pdf_path=row["pdf_path"],
                            created_at=row["created_at"] if "created_at" in row.keys() else "",
                            updated_at=row["updated_at"] if "updated_at" in row.keys() else "")

    def _row_to_invoice(self, row):
        if not row:
            return None
        return Invoice(id=row["id"], invoice_number=row["invoice_number"],
                       quote_id=row["quote_id"], delivery_note_id=row["delivery_note_id"],
                       customer_id=row["customer_id"], date=row["date"],
                       due_date=row["due_date"], status=row["status"],
                       notes=row["notes"], total_ht=row["total_ht"],
                       total_tva=row["total_tva"], total_ttc=row["total_ttc"],
                       pdf_path=row["pdf_path"],
                       created_at=row["created_at"] if "created_at" in row.keys() else "",
                       updated_at=row["updated_at"] if "updated_at" in row.keys() else "")

    def _row_to_payment(self, row):
        if not row:
            return None
        return Payment(id=row["id"],
                       payment_number=row["payment_number"] if "payment_number" in row.keys() else "",
                       invoice_id=row["invoice_id"],
                       amount=row["amount"], date=row["date"],
                       method=row["method"], reference=row["reference"],
                       notes=row["notes"],
                       status=row["status"] if "status" in row.keys() else "draft",
                       created_at=row["created_at"] if "created_at" in row.keys() else "",
                       updated_at=row["updated_at"] if "updated_at" in row.keys() else "")

    # --- COMPANY ---
    def get_company(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM company WHERE id = 1")
        return self._row_to_company(c.fetchone())

    def save_company(self, company: Company):
        c = self.conn.cursor()
        c.execute("""INSERT OR REPLACE INTO company (id, name, address, city, postal_code,
                     phone, email, website, tax_id, ice, rc, if_tax, cnss, logo_path, currency)
                     VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (company.name, company.address, company.city, company.postal_code,
                   company.phone, company.email, company.website, company.tax_id,
                   company.ice, company.rc, company.if_tax, company.cnss,
                   company.logo_path, company.currency))
        self.conn.commit()

    # --- USERS ---
    def login(self, username, password):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        row = c.fetchone()
        if row:
            return User(id=row["id"], username=row["username"],
                        password=row["password"], full_name=row["full_name"])
        return None

    def get_first_user(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users LIMIT 1")
        row = c.fetchone()
        if row:
            return User(id=row["id"], username=row["username"],
                        password=row["password"], full_name=row["full_name"])
        return None

    def insert_user(self, user: User):
        c = self.conn.cursor()
        c.execute("INSERT INTO users (username, password, full_name) VALUES (?, ?, ?)",
                  (user.username, user.password, user.full_name))
        self.conn.commit()

    # --- PRODUCTS ---
    def get_all_products(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM products ORDER BY name")
        return [self._row_to_product(row) for row in c.fetchall()]

    def get_product(self, id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM products WHERE id = ?", (id,))
        return self._row_to_product(c.fetchone())

    def search_products(self, query):
        c = self.conn.cursor()
        c.execute("SELECT * FROM products WHERE name LIKE ? OR reference LIKE ?",
                  (f"%{query}%", f"%{query}%"))
        return [self._row_to_product(row) for row in c.fetchall()]

    def insert_product(self, p: Product):
        c = self.conn.cursor()
        c.execute("""INSERT INTO products (name, description, reference, unit_price, quantity, alert_stock, unit, package_type, photo_path)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (p.name, p.description, p.reference, p.unit_price, p.quantity, p.alert_stock, p.unit, p.package_type, p.photo_path))
        self.conn.commit()
        return c.lastrowid

    def update_product(self, p: Product):
        c = self.conn.cursor()
        c.execute("""UPDATE products SET name=?, description=?, reference=?,
                     unit_price=?, quantity=?, alert_stock=?, unit=?, package_type=?, photo_path=? WHERE id=?""",
                  (p.name, p.description, p.reference, p.unit_price, p.quantity, p.alert_stock, p.unit, p.package_type, p.photo_path, p.id))
        self.conn.commit()

    def delete_product(self, id):
        c = self.conn.cursor()
        c.execute("DELETE FROM products WHERE id = ?", (id,))
        self.conn.commit()

    def decrease_stock(self, product_id, qty):
        c = self.conn.cursor()
        c.execute("UPDATE products SET quantity = quantity - ? WHERE id = ? AND quantity >= ?",
                  (qty, product_id, qty))
        self.conn.commit()
        return c.rowcount > 0

    # --- CUSTOMERS ---
    def get_all_customers(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM customers ORDER BY name")
        return [self._row_to_customer(row) for row in c.fetchall()]

    def get_customer(self, id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM customers WHERE id = ?", (id,))
        return self._row_to_customer(c.fetchone())

    def search_customers(self, query):
        c = self.conn.cursor()
        c.execute("SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ?",
                  (f"%{query}%", f"%{query}%"))
        return [self._row_to_customer(row) for row in c.fetchall()]

    def insert_customer(self, cust: Customer):
        c = self.conn.cursor()
        c.execute("""INSERT INTO customers (name, customer_type, address, phone, email, tax_id, rc, if_tax, cnss, photo_path)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (cust.name, cust.customer_type, cust.address, cust.phone, cust.email,
                   cust.tax_id, cust.rc, cust.if_tax, cust.cnss, cust.photo_path))
        self.conn.commit()
        return c.lastrowid

    def update_customer(self, cust: Customer):
        c = self.conn.cursor()
        c.execute("""UPDATE customers SET name=?, customer_type=?, address=?, phone=?, email=?,
                     tax_id=?, rc=?, if_tax=?, cnss=?, photo_path=? WHERE id=?""",
                  (cust.name, cust.customer_type, cust.address, cust.phone, cust.email,
                   cust.tax_id, cust.rc, cust.if_tax, cust.cnss, cust.photo_path, cust.id))
        self.conn.commit()

    def delete_customer(self, id):
        c = self.conn.cursor()
        c.execute("DELETE FROM customers WHERE id = ?", (id,))
        self.conn.commit()

    # --- QUOTES ---
    def get_all_quotes(self):
        c = self.conn.cursor()
        c.execute("SELECT q.*, c.name as customer_name FROM quotes q LEFT JOIN customers c ON q.customer_id = c.id ORDER BY q.id DESC")
        return [self._row_to_quote(row) for row in c.fetchall()]

    def get_quote(self, id):
        c = self.conn.cursor()
        c.execute("SELECT q.*, c.name as customer_name FROM quotes q LEFT JOIN customers c ON q.customer_id = c.id WHERE q.id = ?", (id,))
        row = c.fetchone()
        if row:
            q = self._row_to_quote(row)
            q.customer_name = row["customer_name"] or ""
            return q
        return None

    def get_quotes_by_status(self, status):
        c = self.conn.cursor()
        c.execute("SELECT q.*, c.name as customer_name FROM quotes q LEFT JOIN customers c ON q.customer_id = c.id WHERE q.status = ? ORDER BY q.id DESC", (status,))
        return [self._row_to_quote(row) for row in c.fetchall()]

    def insert_quote(self, q: Quote):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        qnum = q.quote_number or self._next_doc_number("Q")
        c.execute("""INSERT INTO quotes (quote_number, customer_id, date, valid_until, status, notes, template, total_ht, total_ttc, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (qnum, q.customer_id, q.date, q.valid_until,
                   q.status, q.notes, q.template, q.total_ht, q.total_ttc, now, now))
        self.conn.commit()
        return c.lastrowid

    def update_quote(self, q: Quote):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        c.execute("""UPDATE quotes SET customer_id=?, date=?, valid_until=?, status=?,
                     notes=?, template=?, total_ht=?, total_ttc=?, updated_at=? WHERE id=?""",
                  (q.customer_id, q.date, q.valid_until, q.status,
                   q.notes, q.template, q.total_ht, q.total_ttc, now, q.id))
        self.conn.commit()

    def update_quote_status(self, id, status):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        c.execute("UPDATE quotes SET status = ?, updated_at = ? WHERE id = ?", (status, now, id))
        self.conn.commit()

    def update_quote_pdf(self, id, path):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        c.execute("UPDATE quotes SET pdf_path = ?, updated_at = ? WHERE id = ?", (path, now, id))
        self.conn.commit()

    def delete_quote(self, id):
        c = self.conn.cursor()
        c.execute("DELETE FROM quote_items WHERE quote_id = ?", (id,))
        c.execute("DELETE FROM quotes WHERE id = ?", (id,))
        self.conn.commit()

    def get_last_quote_id(self):
        c = self.conn.cursor()
        c.execute("SELECT MAX(id) FROM quotes")
        return c.fetchone()[0] or 0

    # --- QUOTE ITEMS ---
    def get_quote_items(self, quote_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM quote_items WHERE quote_id = ?", (quote_id,))
        return [self._row_to_quote_item(row) for row in c.fetchall()]

    def insert_quote_items(self, items: List[QuoteItem]):
        c = self.conn.cursor()
        for item in items:
            c.execute("""INSERT INTO quote_items (quote_id, product_id, product_name, quantity, unit_price, tva_rate)
                         VALUES (?, ?, ?, ?, ?, ?)""",
                      (item.quote_id, item.product_id, item.product_name,
                       item.quantity, item.unit_price, item.tva_rate))
        self.conn.commit()

    def delete_quote_items(self, quote_id):
        c = self.conn.cursor()
        c.execute("DELETE FROM quote_items WHERE quote_id = ?", (quote_id,))
        self.conn.commit()

    # --- DELIVERY NOTES ---
    def get_all_delivery_notes(self):
        c = self.conn.cursor()
        c.execute("""SELECT d.*, c.name as customer_name FROM delivery_notes d
                     LEFT JOIN customers c ON d.customer_id = c.id ORDER BY d.id DESC""")
        return [self._row_to_dn(row) for row in c.fetchall()]

    def get_delivery_note(self, id):
        c = self.conn.cursor()
        c.execute("""SELECT d.*, c.name as customer_name FROM delivery_notes d
                     LEFT JOIN customers c ON d.customer_id = c.id WHERE d.id = ?""", (id,))
        row = c.fetchone()
        if row:
            dn = self._row_to_dn(row)
            dn.customer_name = row["customer_name"] or ""
            return dn
        return None

    def get_dn_by_quote(self, quote_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM delivery_notes WHERE quote_id = ? LIMIT 1", (quote_id,))
        return self._row_to_dn(c.fetchone())

    def insert_delivery_note(self, dn: DeliveryNote):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        dnum = dn.delivery_number or self._next_doc_number("DN")
        c.execute("""INSERT INTO delivery_notes (delivery_number, quote_id, customer_id, date, notes, total_ht, total_ttc, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (dnum, dn.quote_id, dn.customer_id,
                   dn.date, dn.notes, dn.total_ht, dn.total_ttc, now, now))
        self.conn.commit()
        return c.lastrowid

    def update_delivery_note(self, dn: DeliveryNote):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        c.execute("""UPDATE delivery_notes SET delivery_number=?, quote_id=?, customer_id=?,
                     date=?, notes=?, total_ht=?, total_ttc=?, updated_at=? WHERE id=?""",
                  (dn.delivery_number, dn.quote_id, dn.customer_id,
                   dn.date, dn.notes, dn.total_ht, dn.total_ttc, now, dn.id))
        self.conn.commit()

    def update_dn_pdf(self, id, path):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        c.execute("UPDATE delivery_notes SET pdf_path = ?, updated_at = ? WHERE id = ?", (path, now, id))
        self.conn.commit()

    def get_last_dn_id(self):
        c = self.conn.cursor()
        c.execute("SELECT MAX(id) FROM delivery_notes")
        return c.fetchone()[0] or 0

    # --- INVOICES ---
    def get_all_invoices(self):
        c = self.conn.cursor()
        c.execute("""SELECT i.*, c.name as customer_name FROM invoices i
                     LEFT JOIN customers c ON i.customer_id = c.id ORDER BY i.id DESC""")
        return [self._row_to_invoice(row) for row in c.fetchall()]

    def get_invoice(self, id):
        c = self.conn.cursor()
        c.execute("""SELECT i.*, c.name as customer_name FROM invoices i
                     LEFT JOIN customers c ON i.customer_id = c.id WHERE i.id = ?""", (id,))
        row = c.fetchone()
        if row:
            inv = self._row_to_invoice(row)
            inv.customer_name = row["customer_name"] or ""
            return inv
        return None

    def get_invoice_by_quote(self, quote_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM invoices WHERE quote_id = ? LIMIT 1", (quote_id,))
        return self._row_to_invoice(c.fetchone())

    def get_invoices_by_status(self, status):
        c = self.conn.cursor()
        c.execute("""SELECT i.*, c.name as customer_name FROM invoices i
                     LEFT JOIN customers c ON i.customer_id = c.id WHERE i.status = ? ORDER BY i.id DESC""", (status,))
        return [self._row_to_invoice(row) for row in c.fetchall()]

    def insert_invoice(self, inv: Invoice):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        inum = inv.invoice_number or self._next_doc_number("I")
        c.execute("""INSERT INTO invoices (invoice_number, quote_id, delivery_note_id, customer_id, date, due_date, status, notes, total_ht, total_tva, total_ttc, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (inum, inv.quote_id, inv.delivery_note_id,
                   inv.customer_id, inv.date, inv.due_date, inv.status,
                   inv.notes, inv.total_ht, inv.total_tva, inv.total_ttc, now, now))
        self.conn.commit()
        return c.lastrowid

    def update_invoice(self, inv: Invoice):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        c.execute("""UPDATE invoices SET invoice_number=?, quote_id=?, delivery_note_id=?,
                     customer_id=?, date=?, due_date=?, status=?, notes=?,
                     total_ht=?, total_tva=?, total_ttc=?, updated_at=? WHERE id=?""",
                  (inv.invoice_number, inv.quote_id, inv.delivery_note_id,
                   inv.customer_id, inv.date, inv.due_date, inv.status,
                   inv.notes, inv.total_ht, inv.total_tva, inv.total_ttc, now, inv.id))
        self.conn.commit()

    def update_invoice_status(self, id, status):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        c.execute("UPDATE invoices SET status = ?, updated_at = ? WHERE id = ?", (status, now, id))
        self.conn.commit()

    def update_invoice_pdf(self, id, path):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        c.execute("UPDATE invoices SET pdf_path = ?, updated_at = ? WHERE id = ?", (path, now, id))
        self.conn.commit()

    def recalc_invoice_status(self, invoice_id):
        inv = self.get_invoice(invoice_id)
        if not inv: return
        total_paid = self.get_total_paid(invoice_id)
        if total_paid >= inv.total_ttc and inv.total_ttc > 0:
            new_status = "completed"
        elif total_paid > 0:
            new_status = "partial"
        else:
            new_status = "draft"
        self.update_invoice_status(invoice_id, new_status)

    def get_last_invoice_id(self):
        c = self.conn.cursor()
        c.execute("SELECT MAX(id) FROM invoices")
        return c.fetchone()[0] or 0

    # --- INVOICE ITEMS ---
    def get_invoice_items(self, invoice_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
        rows = c.fetchall()
        items = []
        for row in rows:
            items.append(InvoiceItem(
                id=row["id"], invoice_id=row["invoice_id"],
                product_id=row["product_id"], product_name=row["product_name"],
                quantity=row["quantity"], unit_price=row["unit_price"],
                tva_rate=row["tva_rate"]
            ))
        return items

    def insert_invoice_items(self, items):
        c = self.conn.cursor()
        for item in items:
            c.execute("""INSERT INTO invoice_items (invoice_id, product_id, product_name, quantity, unit_price, tva_rate)
                         VALUES (?, ?, ?, ?, ?, ?)""",
                      (item.invoice_id, item.product_id, item.product_name,
                       item.quantity, item.unit_price, item.tva_rate))
        self.conn.commit()

    def delete_invoice_items(self, invoice_id):
        c = self.conn.cursor()
        c.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
        self.conn.commit()

    # --- TEMPLATES ---
    def get_template(self, doc_type):
        c = self.conn.cursor()
        c.execute("SELECT * FROM templates WHERE doc_type = ?", (doc_type,))
        row = c.fetchone()
        if row:
            return Template(doc_type=row["doc_type"], header_text=row["header_text"], footer_text=row["footer_text"])
        return None

    def save_template(self, doc_type, header_text, footer_text):
        c = self.conn.cursor()
        c.execute("""INSERT OR REPLACE INTO templates (doc_type, header_text, footer_text)
                     VALUES (?, ?, ?)""", (doc_type, header_text, footer_text))
        self.conn.commit()

    # --- PAYMENTS ---
    def get_payments(self, invoice_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM payments WHERE invoice_id = ? ORDER BY date DESC", (invoice_id,))
        return [self._row_to_payment(row) for row in c.fetchall()]

    def get_all_payments(self):
        c = self.conn.cursor()
        c.execute("""SELECT p.*, i.invoice_number FROM payments p
                     LEFT JOIN invoices i ON p.invoice_id = i.id ORDER BY p.date DESC""")
        rows = c.fetchall()
        payments = []
        for row in rows:
            p = self._row_to_payment(row)
            payments.append(p)
        return payments

    def get_total_paid(self, invoice_id):
        c = self.conn.cursor()
        c.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE invoice_id = ?", (invoice_id,))
        return c.fetchone()[0]

    def insert_payment(self, p: Payment):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        pnum = p.payment_number or self._next_doc_number("P")
        c.execute("""INSERT INTO payments (payment_number, invoice_id, amount, date, method, reference, notes, status, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (pnum, p.invoice_id, p.amount, p.date, p.method, p.reference, p.notes, p.status, now, now))
        self.conn.commit()
        return c.lastrowid

    def delete_payment(self, id):
        c = self.conn.cursor()
        c.execute("DELETE FROM payments WHERE id = ?", (id,))
        self.conn.commit()

    def get_low_stock_count(self):
        c = self.conn.cursor()
        return c.execute("SELECT COUNT(*) FROM products WHERE alert_stock > 0 AND quantity <= alert_stock").fetchone()[0]

    # --- MISC ---
    def get_dashboard_stats(self):
        c = self.conn.cursor()
        products = c.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        customers = c.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        quotes = c.execute("SELECT COUNT(*) FROM quotes").fetchone()[0]
        invoices = c.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
        pending = c.execute("SELECT COUNT(*) FROM invoices WHERE status IN ('draft','sent','partial')").fetchone()[0]
        revenue = c.execute("SELECT COALESCE(SUM(amount),0) FROM payments").fetchone()[0]
        delivery_notes = c.execute("SELECT COUNT(*) FROM delivery_notes").fetchone()[0]
        payments = c.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
        low_stock = self.get_low_stock_count()
        return products, customers, quotes, invoices, pending, revenue, delivery_notes, payments, low_stock

    def close(self):
        self.conn.close()
