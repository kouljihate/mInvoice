import sqlite3, os

DB_DIR = os.path.join(os.path.dirname(__file__), "data", "db")
dbs = [f for f in os.listdir(DB_DIR) if f.endswith(".db") and not f.endswith(".bak")]
if not dbs:
    print("No database found in data/db/")
    input("Press Enter to exit...")
    exit(1)

DB_PATH = os.path.join(DB_DIR, dbs[0])
print(f"Using database: {dbs[0]}")

try:
    conn = sqlite3.connect(DB_PATH, timeout=5)
    c = conn.cursor()
    c.execute("DELETE FROM quote_items")
    c.execute("DELETE FROM invoice_items")
    c.execute("DELETE FROM payments")
    c.execute("DELETE FROM quotes")
    c.execute("DELETE FROM delivery_notes")
    c.execute("DELETE FROM invoices")
    conn.commit()
    conn.close()
    print("All documents deleted successfully.")
except sqlite3.OperationalError as e:
    print(f"Error: {e}")
    print("Make sure the app is closed before running this script.")
    input("Press Enter to exit...")
