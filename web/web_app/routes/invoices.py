from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..utils import login_required, get_db, tr
from app.database import Payment

invoices_bp = Blueprint('invoices', __name__)

@invoices_bp.route('/invoices')
@login_required
def list_invoices():
    db = get_db(invoices_bp)
    invoices = db.get_all_invoices()
    company = db.get_company()
    lang = session.get('lang', 'en')
    db.close()
    return render_template('invoices/list.html', invoices=invoices, company=company, lang=lang, tr=lambda k: tr(lang, k))

@invoices_bp.route('/invoices/<int:id>')
@login_required
def view_invoice(id):
    db = get_db(invoices_bp)
    invoice = db.get_invoice(id)
    items = db.get_invoice_items(id)
    payments = db.get_payments(id)
    total_paid = db.get_total_paid(id)
    company = db.get_company()
    lang = session.get('lang', 'en')
    db.close()
    return render_template('invoices/view.html', invoice=invoice, items=items, payments=payments,
                         total_paid=total_paid, company=company, lang=lang, tr=lambda k: tr(lang, k))

@invoices_bp.route('/invoices/<int:id>/pay', methods=['POST'])
@login_required
def pay_invoice(id):
    db = get_db(invoices_bp)
    amount = float(request.form.get('amount', 0))
    method = request.form.get('method', 'cash')
    if amount > 0:
        p = Payment(
            invoice_id=id,
            amount=amount,
            method=method,
            date=request.form.get('date', ''),
            reference=request.form.get('reference', ''),
            notes=request.form.get('notes', ''),
            status='completed',
        )
        db.insert_payment(p)
        db.recalc_invoice_status(id)
        flash('Payment recorded', 'success')
    db.close()
    return redirect(url_for('invoices.view_invoice', id=id))

@invoices_bp.route('/invoices/<int:id>/status')
@login_required
def update_invoice_status(id):
    status = request.args.get('status', 'draft')
    db = get_db(invoices_bp)
    db.update_invoice_status(id, status)
    flash(f'Status updated to {status}', 'success')
    db.close()
    return redirect(url_for('invoices.view_invoice', id=id))

@invoices_bp.route('/invoices/<int:id>/delete')
@login_required
def delete_invoice(id):
    db = get_db(invoices_bp)
    db.delete_invoice(id)
    db.close()
    flash('Invoice deleted', 'success')
    return redirect(url_for('invoices.list_invoices'))

@invoices_bp.route('/invoices/<int:id>/pdf')
@login_required
def invoice_pdf(id):
    from app.pdf_gen import generate_invoice_pdf
    from flask import send_file
    db = get_db(invoices_bp)
    invoice = db.get_invoice(id)
    items = db.get_invoice_items(id)
    payments = db.get_payments(id)
    total_paid = db.get_total_paid(id)
    company = db.get_company()
    path = generate_invoice_pdf(company, invoice, items, payments, total_paid, db)
    db.close()
    return send_file(path, as_attachment=True, download_name=f'invoice_{invoice.invoice_number}.pdf')
