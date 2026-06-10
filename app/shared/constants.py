import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(DATA_DIR, "db")
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
UPLOAD_DIR = os.path.join(DATA_DIR, "upload")
TRANSLATIONS_DIR = os.path.join(DATA_DIR, "translations")

# Colors
PRIMARY = "#1B2A4A"
PRIMARY_LIGHT = "#2C3E6B"
SECONDARY = "#C8A84E"
SURFACE = "#FFFFFF"
BACKGROUND = "#F0F2F5"
CARD_BG = "#FFFFFF"
ERROR = "#D32F2F"
SUCCESS = "#2E7D32"
WARNING = "#F57C00"
TEXT_PRIMARY = "#1A1A2E"
TEXT_SECONDARY = "#6B7280"
BORDER_COLOR = "#E5E7EB"
DIVIDER_COLOR = "#E5E7EB"

LANG_EN = "en"
LANG_AR = "ar"
LANG_FR = "fr"
LANG_NAMES = {LANG_EN: "EN", LANG_AR: "AR", LANG_FR: "FR"}
