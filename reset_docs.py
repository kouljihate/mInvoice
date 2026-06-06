import sqlite3, os
DB_PATH = os.path.join(os.path.dirname(__file__), "minvoice.db")

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
