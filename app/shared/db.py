import sqlite3, os, re
from datetime import datetime
from typing import List
from app.shared.constants import DB_DIR
from app.shared.models import Company, User, Product, Customer, Quote, QuoteItem, DeliveryNote, Invoice, InvoiceItem, Template, TemplateSection, Payment, DEFAULT_INVOICE_SECTIONS


def _slugify(text):
    return re.sub(r'[^a-z0-9_]', '_', text.lower()).strip('_')


class Database:
    def __init__(self, db_path=None):
        os.makedirs(DB_DIR, exist_ok=True)
        if db_path:
            self.db_path = db_path
        else:
            dbs = [f for f in os.listdir(DB_DIR) if f.endswith(".db") and not f.endswith(".bak")]
            if dbs:
                self.db_path = os.path.join(DB_DIR, dbs[0])
            else:
                self.db_path = os.path.join(DB_DIR, "minvoice.db")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        c.executescript("""
            CREATE TABLE IF NOT EXISTS company (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                name TEXT NOT NULL DEFAULT '', address TEXT DEFAULT '', city TEXT DEFAULT '',
                postal_code TEXT DEFAULT '', phone TEXT DEFAULT '', email TEXT DEFAULT '',
                website TEXT DEFAULT '', tax_id TEXT DEFAULT '', ice TEXT DEFAULT '',
                rc TEXT DEFAULT '', if_tax TEXT DEFAULT '', cnss TEXT DEFAULT '',
                logo_path TEXT DEFAULT '', currency TEXT DEFAULT 'MAD'
            );
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL, full_name TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
                description TEXT DEFAULT '', reference TEXT DEFAULT '',
                unit_price REAL DEFAULT 0.0, quantity INTEGER DEFAULT 0,
                unit TEXT DEFAULT 'piece', package_type TEXT DEFAULT '', photo_path TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
                address TEXT DEFAULT '', phone TEXT DEFAULT '', email TEXT DEFAULT '',
                tax_id TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, quote_number TEXT NOT NULL DEFAULT '',
                customer_id INTEGER NOT NULL, date TEXT DEFAULT '', valid_until TEXT DEFAULT '',
                status TEXT DEFAULT 'draft', notes TEXT DEFAULT '', template TEXT DEFAULT 'default',
                total_ht REAL DEFAULT 0.0, total_ttc REAL DEFAULT 0.0,
                pdf_path TEXT DEFAULT '', created_at TEXT DEFAULT '', updated_at TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS quote_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT, quote_id INTEGER NOT NULL,
                product_id INTEGER DEFAULT 0, product_name TEXT DEFAULT '',
                quantity INTEGER DEFAULT 0, unit_price REAL DEFAULT 0.0, tva_rate REAL DEFAULT 0.0
            );
            CREATE TABLE IF NOT EXISTS delivery_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, delivery_number TEXT NOT NULL DEFAULT '',
                quote_id INTEGER NOT NULL, customer_id INTEGER NOT NULL, date TEXT DEFAULT '',
                notes TEXT DEFAULT '', total_ht REAL DEFAULT 0.0, total_ttc REAL DEFAULT 0.0,
                pdf_path TEXT DEFAULT '', created_at TEXT DEFAULT '', updated_at TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_number TEXT NOT NULL DEFAULT '',
                quote_id INTEGER NOT NULL, delivery_note_id INTEGER DEFAULT 0,
                customer_id INTEGER NOT NULL, date TEXT DEFAULT '', due_date TEXT DEFAULT '',
                status TEXT DEFAULT 'draft', notes TEXT DEFAULT '',
                total_ht REAL DEFAULT 0.0, total_tva REAL DEFAULT 0.0, total_ttc REAL DEFAULT 0.0,
                pdf_path TEXT DEFAULT '', created_at TEXT DEFAULT '', updated_at TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_id INTEGER NOT NULL,
                product_id INTEGER DEFAULT 0, product_name TEXT DEFAULT '',
                quantity INTEGER DEFAULT 0, unit_price REAL DEFAULT 0.0, tva_rate REAL DEFAULT 0.0
            );
            CREATE TABLE IF NOT EXISTS templates (
                doc_type TEXT PRIMARY KEY, header_text TEXT DEFAULT '', footer_text TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT, payment_number TEXT NOT NULL DEFAULT '',
                invoice_id INTEGER NOT NULL, amount REAL DEFAULT 0.0, date TEXT DEFAULT '',
                method TEXT DEFAULT 'cash', reference TEXT DEFAULT '', notes TEXT DEFAULT '',
                status TEXT DEFAULT 'draft', created_at TEXT DEFAULT '', updated_at TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS template_sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT, doc_type TEXT NOT NULL DEFAULT 'invoice',
                section_key TEXT NOT NULL, section_name TEXT NOT NULL DEFAULT '',
                parent_group TEXT NOT NULL DEFAULT '', position INTEGER NOT NULL DEFAULT 0,
                is_visible INTEGER NOT NULL DEFAULT 1, content_type TEXT NOT NULL DEFAULT 'fields',
                fields_config TEXT NOT NULL DEFAULT '[]', custom_text TEXT NOT NULL DEFAULT '',
                font_size REAL NOT NULL DEFAULT 10.0, font_style TEXT NOT NULL DEFAULT 'normal',
                text_align TEXT NOT NULL DEFAULT 'left', UNIQUE(doc_type, section_key)
            );
        """)
        self.conn.commit()
        self._migrate_all()

    def _migrate_all(self):
        c = self.conn.cursor()
        for table, cols in {
            "company": ["city", "postal_code", "ice", "rc", "if_tax", "tp", "cnss", "logo_path"],
        }.items():
            for col in cols:
                try: c.execute(f"ALTER TABLE {table} ADD COLUMN {col} TEXT DEFAULT ''")
                except sqlite3.OperationalError: pass
        for col in ["package_type", "photo_path", "alert_stock"]:
            dtype = "INTEGER DEFAULT 0" if col == "alert_stock" else "TEXT DEFAULT ''"
            try: c.execute(f"ALTER TABLE products ADD COLUMN {col} {dtype}")
            except sqlite3.OperationalError: pass
        for col in ["customer_type", "rc", "if_tax", "cnss", "photo_path"]:
            try: c.execute(f"ALTER TABLE customers ADD COLUMN {col} TEXT DEFAULT ''")
            except sqlite3.OperationalError: pass
        for col in ["status"]:
            try: c.execute(f"ALTER TABLE payments ADD COLUMN {col} TEXT DEFAULT 'draft'")
            except sqlite3.OperationalError: pass
        for tbl in ["quotes", "delivery_notes", "invoices"]:
            for col in ["created_at", "updated_at"]:
                try: c.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} TEXT DEFAULT ''")
                except sqlite3.OperationalError: pass
        for col in ["payment_number", "created_at", "updated_at"]:
            try: c.execute(f"ALTER TABLE payments ADD COLUMN {col} TEXT DEFAULT ''")
            except sqlite3.OperationalError: pass
        self.conn.commit()

    def _next_doc_number(self, prefix):
        tables = {"Q": "quotes", "I": "invoices", "DN": "delivery_notes", "P": "payments"}
        c = self.conn.cursor()
        c.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {tables[prefix]}")
        seq = c.fetchone()[0]
        today = datetime.now().strftime("%d%m%y")
        return f"{prefix}{today}-{seq:04d}"

    def _row_to_company(self, row):
        if not row: return None
        return Company(name=row["name"], address=row["address"],
            city=row["city"] if "city" in row.keys() else "",
            postal_code=row["postal_code"] if "postal_code" in row.keys() else "",
            phone=row["phone"], email=row["email"], website=row["website"],
            tax_id=row["tax_id"],
            ice=row["ice"] if "ice" in row.keys() else "",
            rc=row["rc"] if "rc" in row.keys() else "",
            if_tax=row["if_tax"] if "if_tax" in row.keys() else "",
            tp=row["tp"] if "tp" in row.keys() else "",
            cnss=row["cnss"] if "cnss" in row.keys() else "",
            logo_path=row["logo_path"] if "logo_path" in row.keys() else "",
            currency=row["currency"])

    def _row_to_product(self, row):
        if not row: return None
        return Product(id=row["id"], name=row["name"], description=row["description"],
            reference=row["reference"], unit_price=row["unit_price"], quantity=row["quantity"],
            alert_stock=row["alert_stock"] if "alert_stock" in row.keys() else 0,
            unit=row["unit"],
            package_type=row["package_type"] if "package_type" in row.keys() else "",
            photo_path=row["photo_path"] if "photo_path" in row.keys() else "")

    def _row_to_customer(self, row):
        if not row: return None
        return Customer(id=row["id"], name=row["name"],
            customer_type=row["customer_type"] if "customer_type" in row.keys() else "private",
            address=row["address"], phone=row["phone"], email=row["email"], tax_id=row["tax_id"],
            rc=row["rc"] if "rc" in row.keys() else "",
            if_tax=row["if_tax"] if "if_tax" in row.keys() else "",
            cnss=row["cnss"] if "cnss" in row.keys() else "",
            photo_path=row["photo_path"] if "photo_path" in row.keys() else "")

    def _row_to_quote(self, row):
        if not row: return None
        return Quote(id=row["id"], quote_number=row["quote_number"],
            customer_id=row["customer_id"], date=row["date"],
            valid_until=row["valid_until"], status=row["status"],
            notes=row["notes"], template=row["template"],
            total_ht=row["total_ht"], total_ttc=row["total_ttc"], pdf_path=row["pdf_path"],
            created_at=row["created_at"] if "created_at" in row.keys() else "",
            updated_at=row["updated_at"] if "updated_at" in row.keys() else "")

    def _row_to_quote_item(self, row):
        if not row: return None
        return QuoteItem(id=row["id"], quote_id=row["quote_id"],
            product_id=row["product_id"], product_name=row["product_name"],
            quantity=row["quantity"], unit_price=row["unit_price"], tva_rate=row["tva_rate"])

    def _row_to_dn(self, row):
        if not row: return None
        return DeliveryNote(id=row["id"], delivery_number=row["delivery_number"],
            quote_id=row["quote_id"], customer_id=row["customer_id"],
            date=row["date"], notes=row["notes"],
            total_ht=row["total_ht"], total_ttc=row["total_ttc"], pdf_path=row["pdf_path"],
            created_at=row["created_at"] if "created_at" in row.keys() else "",
            updated_at=row["updated_at"] if "updated_at" in row.keys() else "")

    def _row_to_invoice(self, row):
        if not row: return None
        return Invoice(id=row["id"], invoice_number=row["invoice_number"],
            quote_id=row["quote_id"], delivery_note_id=row["delivery_note_id"],
            customer_id=row["customer_id"], date=row["date"], due_date=row["due_date"],
            status=row["status"], notes=row["notes"],
            total_ht=row["total_ht"], total_tva=row["total_tva"], total_ttc=row["total_ttc"],
            pdf_path=row["pdf_path"],
            created_at=row["created_at"] if "created_at" in row.keys() else "",
            updated_at=row["updated_at"] if "updated_at" in row.keys() else "")

    def _row_to_payment(self, row):
        if not row: return None
        return Payment(id=row["id"],
            payment_number=row["payment_number"] if "payment_number" in row.keys() else "",
            invoice_id=row["invoice_id"], amount=row["amount"], date=row["date"],
            method=row["method"], reference=row["reference"], notes=row["notes"],
            status=row["status"] if "status" in row.keys() else "draft",
            created_at=row["created_at"] if "created_at" in row.keys() else "",
            updated_at=row["updated_at"] if "updated_at" in row.keys() else "")

    # --- COMPANY ---
    def get_company(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM company WHERE id = 1")
        return self._row_to_company(c.fetchone())

    def _rename_db(self, company_name):
        target = os.path.join(DB_DIR, _slugify(company_name) + ".db")
        if target == self.db_path: return
        self.conn.close()
        if os.path.exists(target): os.remove(target)
        os.rename(self.db_path, target)
        self.db_path = target
        self.conn = sqlite3.connect(target)
        self.conn.row_factory = sqlite3.Row

    def save_company(self, company: Company):
        c = self.conn.cursor()
        c.execute("""INSERT OR REPLACE INTO company (id, name, address, city, postal_code,
            phone, email, website, tax_id, ice, rc, if_tax, tp, cnss, logo_path, currency)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (company.name, company.address, company.city, company.postal_code,
             company.phone, company.email, company.website, company.tax_id,
             company.ice, company.rc, company.if_tax, company.tp, company.cnss,
             company.logo_path, company.currency))
        self.conn.commit()
        bootstrap = os.path.join(DB_DIR, "minvoice.db")
        if self.db_path == bootstrap:
            self._rename_db(company.name)

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

    def delete_invoice(self, id):
        inv = self.get_invoice(id)
        if not inv: return
        c = self.conn.cursor()
        c.execute("DELETE FROM payments WHERE invoice_id = ?", (id,))
        c.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (id,))
        if inv.delivery_note_id:
            c.execute("DELETE FROM delivery_notes WHERE id = ?", (inv.delivery_note_id,))
        c.execute("DELETE FROM invoices WHERE id = ?", (id,))
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
        return [InvoiceItem(id=row["id"], invoice_id=row["invoice_id"],
            product_id=row["product_id"], product_name=row["product_name"],
            quantity=row["quantity"], unit_price=row["unit_price"], tva_rate=row["tva_rate"])
            for row in c.fetchall()]

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

    # --- TEMPLATE SECTIONS ---
    def _row_to_template_section(self, row):
        if not row: return None
        return TemplateSection(id=row["id"], doc_type=row["doc_type"],
            section_key=row["section_key"], section_name=row["section_name"],
            parent_group=row["parent_group"], position=row["position"],
            is_visible=bool(row["is_visible"]), content_type=row["content_type"],
            fields_config=row["fields_config"], custom_text=row["custom_text"],
            font_size=row["font_size"], font_style=row["font_style"], text_align=row["text_align"])

    def get_template_sections(self, doc_type="invoice"):
        c = self.conn.cursor()
        c.execute("SELECT * FROM template_sections WHERE doc_type = ? ORDER BY position", (doc_type,))
        return [self._row_to_template_section(row) for row in c.fetchall()]

    def save_template_section(self, sec: TemplateSection):
        c = self.conn.cursor()
        c.execute("""INSERT OR REPLACE INTO template_sections
            (doc_type, section_key, section_name, parent_group, position,
             is_visible, content_type, fields_config, custom_text, font_size, font_style, text_align)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (sec.doc_type, sec.section_key, sec.section_name, sec.parent_group,
             sec.position, int(sec.is_visible), sec.content_type, sec.fields_config,
             sec.custom_text, sec.font_size, sec.font_style, sec.text_align))
        self.conn.commit()

    def delete_template_section(self, section_id):
        c = self.conn.cursor()
        c.execute("DELETE FROM template_sections WHERE id = ?", (section_id,))
        self.conn.commit()

    def create_default_invoice_template(self):
        existing = self.get_template_sections("invoice")
        if existing: return
        for key, name, group, pos, ctype, fields, text, fsize, fstyle, align in DEFAULT_INVOICE_SECTIONS:
            self.save_template_section(TemplateSection(
                doc_type="invoice", section_key=key, section_name=name,
                parent_group=group, position=pos, is_visible=True,
                content_type=ctype, fields_config=fields, custom_text=text,
                font_size=fsize, font_style=fstyle, text_align=align))

    # --- PAYMENTS ---
    def get_payments(self, invoice_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM payments WHERE invoice_id = ? ORDER BY date DESC", (invoice_id,))
        return [self._row_to_payment(row) for row in c.fetchall()]

    def get_all_payments(self):
        c = self.conn.cursor()
        c.execute("""SELECT p.*, i.invoice_number FROM payments p
            LEFT JOIN invoices i ON p.invoice_id = i.id ORDER BY p.date DESC""")
        return [self._row_to_payment(row) for row in c.fetchall()]

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

    def get_dashboard_data(self):
        c = self.conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        month_start = datetime.now().strftime("%Y-%m-01")

        sales_month = c.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE date >= ?", (month_start,)).fetchone()[0]
        invoiced_month = c.execute("SELECT COALESCE(SUM(total_ttc),0) FROM invoices WHERE date >= ?", (month_start,)).fetchone()[0]
        paid_month = sales_month

        c.execute("""SELECT COALESCE(SUM(i.total_ttc - COALESCE(p.paid,0)),0) FROM invoices i
            LEFT JOIN (SELECT invoice_id, SUM(amount) as paid FROM payments GROUP BY invoice_id) p ON i.id = p.invoice_id
            WHERE i.status != 'completed' AND i.status != 'draft'""")
        outstanding = c.fetchone()[0]

        overdue_count = c.execute("SELECT COUNT(*) FROM invoices WHERE due_date < ? AND due_date != '' AND status IN ('sent','partial')", (today,)).fetchone()[0]

        c.execute("""SELECT COALESCE(SUM(i.total_ttc - COALESCE(p.paid,0)),0) FROM invoices i
            LEFT JOIN (SELECT invoice_id, SUM(amount) as paid FROM payments GROUP BY invoice_id) p ON i.id = p.invoice_id
            WHERE i.due_date < ? AND i.due_date != '' AND i.status IN ('sent','partial')""", (today,))
        overdue_amount = c.fetchone()[0]

        stock_value = c.execute("SELECT COALESCE(SUM(unit_price * quantity),0) FROM products").fetchone()[0]
        low_stock = c.execute("SELECT COUNT(*) FROM products WHERE alert_stock > 0 AND quantity <= alert_stock").fetchone()[0]
        out_of_stock = c.execute("SELECT COUNT(*) FROM products WHERE quantity <= 0").fetchone()[0]
        new_customers = c.execute("SELECT COUNT(*) FROM customers WHERE id NOT IN (SELECT DISTINCT customer_id FROM invoices)").fetchone()[0]
        below_reorder = c.execute("SELECT COUNT(*) FROM products WHERE alert_stock > 0 AND quantity < alert_stock").fetchone()[0]

        fast_moving = c.execute("""SELECT product_name, SUM(quantity) as total_sold FROM invoice_items
            GROUP BY product_id ORDER BY total_sold DESC LIMIT 5""").fetchall()
        fast_moving = [dict(r) for r in fast_moving]

        draft_inv = c.execute("SELECT COUNT(*) FROM invoices WHERE status = 'draft'").fetchone()[0]
        sent_inv = c.execute("SELECT COUNT(*) FROM invoices WHERE status = 'sent'").fetchone()[0]
        paid_inv = c.execute("SELECT COUNT(*) FROM invoices WHERE status = 'completed'").fetchone()[0]
        partial_inv = c.execute("SELECT COUNT(*) FROM invoices WHERE status = 'partial'").fetchone()[0]

        active_customers = c.execute("SELECT COUNT(DISTINCT customer_id) FROM invoices").fetchone()[0]
        top_customers = c.execute("""SELECT c.name, COALESCE(SUM(i.total_ttc),0) as revenue
            FROM customers c JOIN invoices i ON c.id = i.customer_id
            GROUP BY c.id ORDER BY revenue DESC LIMIT 5""").fetchall()
        top_customers = [dict(r) for r in top_customers]
        overdue_customers = c.execute("""SELECT COUNT(DISTINCT i.customer_id) FROM invoices i
            WHERE i.due_date < ? AND i.due_date != '' AND i.status IN ('sent','partial')""", (today,)).fetchone()[0]

        top_products = c.execute("""SELECT product_name, SUM(quantity * unit_price) as revenue
            FROM invoice_items GROUP BY product_id ORDER BY revenue DESC LIMIT 10""").fetchall()
        top_products = [dict(r) for r in top_products]

        draft_quotes = c.execute("SELECT COUNT(*) FROM quotes WHERE status = 'draft'").fetchone()[0]
        validated_quotes = c.execute("SELECT COUNT(*) FROM quotes WHERE status = 'validated'").fetchone()[0]
        sent_quotes = c.execute("SELECT COUNT(*) FROM quotes WHERE status = 'sent'").fetchone()[0]
        confirmed_quotes = c.execute("SELECT COUNT(*) FROM quotes WHERE status = 'confirmed'").fetchone()[0]
        quotes_month = c.execute("SELECT COUNT(*) FROM quotes WHERE date >= ?", (month_start,)).fetchone()[0]
        quotes_amount_month = c.execute("SELECT COALESCE(SUM(total_ttc),0) FROM quotes WHERE date >= ?", (month_start,)).fetchone()[0]
        quotes_converted = c.execute("SELECT COUNT(*) FROM quotes WHERE status = 'confirmed' AND id IN (SELECT DISTINCT quote_id FROM invoices)").fetchone()[0]

        total_products = c.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        total_customers = c.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        total_invoices = c.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
        total_quotes = c.execute("SELECT COUNT(*) FROM quotes").fetchone()[0]
        total_payments = c.execute("SELECT COUNT(*) FROM payments").fetchone()[0]

        sales_trend = c.execute("""SELECT strftime('%m', date) as m, strftime('%Y', date) as y, SUM(amount) as total
            FROM payments WHERE date >= date('now', '-6 months')
            GROUP BY y, m ORDER BY y, m""").fetchall()
        sales_trend = [dict(r) for r in sales_trend]

        return dict(
            sales_month=sales_month, invoiced_month=invoiced_month, paid_month=paid_month,
            outstanding=outstanding, overdue_count=overdue_count, overdue_amount=overdue_amount,
            stock_value=stock_value, low_stock=low_stock, out_of_stock=out_of_stock,
            new_customers=new_customers, below_reorder=below_reorder, fast_moving=fast_moving,
            draft_inv=draft_inv, sent_inv=sent_inv, paid_inv=paid_inv, partial_inv=partial_inv,
            active_customers=active_customers, top_customers=top_customers,
            overdue_customers=overdue_customers, top_products=top_products,
            status_breakdown={"draft": draft_inv, "sent": sent_inv, "partial": partial_inv, "paid": paid_inv},
            draft_quotes=draft_quotes, validated_quotes=validated_quotes,
            sent_quotes=sent_quotes, confirmed_quotes=confirmed_quotes,
            quotes_month=quotes_month, quotes_amount_month=quotes_amount_month,
            quotes_converted=quotes_converted,
            total_products=total_products, total_customers=total_customers,
            total_invoices=total_invoices, total_quotes=total_quotes, total_payments=total_payments,
            sales_trend=sales_trend)

    def close(self):
        self.conn.close()
