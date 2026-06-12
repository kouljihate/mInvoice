# mInvoice

A dual-interface invoicing application for Moroccan small-to-medium businesses. Manage products, customers, quotes (devis), delivery notes (bons de livraison), invoices, and payments — with PDF generation, multi-language support (EN/FR/AR), and Moroccan tax compliance (ICE, IF, RC, CNSS, TP).

**Version 2.0.0**

## Interfaces

| Mode | Framework | Platform |
|------|-----------|----------|
| **Mobile** | [Flet](https://flet.dev/) (Python → Flutter) | Desktop / Android |
| **Web** | [Flask](https://flask.palletsprojects.com/) + Jinja2 + Bootswatch | Browser |

## Features

- **Dashboard** — Revenue analytics, overdue tracking, stock alerts, top products/customers, sales trends
- **Products** — CRUD, bulk import (JSON/CSV), stock tracking with low-stock alerts
- **Customers** — CRUD, bulk import, support for individuals & companies with Moroccan tax fields
- **Quotes** — Line-item editor, stock-aware quantity validation, auto-convert to delivery note + invoice
- **Delivery Notes** — Auto-generated from quotes, PDF export
- **Invoices** — Full CRUD, payment recording (cash/check/bank transfer/card), auto-status, PDF with payment history & QR code
- **Payments** — List all payments, edit status, auto-update invoice status
- **PDF Generation** — Professional PDFs via fpdf2 with customizable templates (section visibility, fonts, alignment)
- **Multi-language** — English, French, Arabic with live switching
- **First-run Setup Wizard** — Company info, Moroccan tax IDs, admin account, template preferences

## Quick Start

### Prerequisites

- Python **3.14+**

### Setup

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

pip install -r requirements.txt
```

Configure `.env` (or set environment variables):

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `mInvoice-dev-key-change-in-production` | Flask secret key |
| `DEBUG` | `true` | Enable debug mode |
| `FLASK_PORT` | `5000` | Web server port |
| `FLASK_HOST` | `0.0.0.0` | Web server host |

### Run

```bash
# Web app (Flask) — http://localhost:5000
python run.py web

# Mobile/Desktop app (Flet)
python run.py mobile
```

### First Run

1. Open the app — the setup wizard appears
2. Enter company details, Moroccan tax info, and admin credentials
3. Configure invoice template visibility
4. Log in and start managing products, customers, quotes, and invoices

## Utilities

```bash
# Seed sample data (100 products + 100 customers)
python tools/seed_data.py

# Delete all documents (quotes, invoices, delivery notes, payments)
python tools/reset_docs.py
```

## Project Structure

```
mInvoice/
├── run.py                  # Entry point
├── requirements.txt
├── .env
├── app/
│   ├── shared/             # Models, database, constants, validators, i18n
│   ├── be/                 # Backend services (routes, PDF generation)
│   └── fe/
│       ├── mobile/         # Flet app (screens/, widgets/)
│       └── web/            # Flask app (pages/, templates/, static/)
├── api/                    # REST API client & auth
├── config/                 # Settings & environment config
├── data/                   # SQLite databases, translations, sample data
├── tools/                  # Utility scripts
├── tests/                  # Tests
├── build/apk/              # Pre-built Android APK
└── pdfs/                   # Generated PDF output
```

## Build Android APK

A pre-built APK is at `build/apk/mInvoice.apk`. To rebuild:

```bash
flet build apk --project-dir app/fe/mobile
```

## Tech Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.14+ |
| Mobile | Flet 0.85+ |
| Web | Flask 3.1+, Jinja2, Bootswatch, htmx |
| PDF | fpdf2 2.8+, PyMuPDF (preview) |
| QR | qrcode 8+ |
| Database | SQLite3 |
| i18n | Custom JSON translations (EN/FR/AR) |

## License

MIT

---

Built by [@koul](https://github.com/kouljihate)
