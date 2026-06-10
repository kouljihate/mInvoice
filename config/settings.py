import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(DATA_DIR, "db")
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
UPLOAD_DIR = os.path.join(DATA_DIR, "upload")
TRANSLATIONS_DIR = os.path.join(DATA_DIR, "translations")

SECRET_KEY = os.environ.get("SECRET_KEY", "mInvoice-dev-key-change-in-production")
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))
FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
