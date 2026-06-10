from flask import Blueprint, render_template, request, redirect, url_for, session, send_file
from ..utils import login_required, get_db, tr

delivery_notes_bp = Blueprint('delivery_notes', __name__)

@delivery_notes_bp.route('/delivery_notes')
@login_required
def list_delivery_notes():
    db = get_db(delivery_notes_bp)
    dns = db.get_all_delivery_notes()
    company = db.get_company()
    lang = session.get('lang', 'en')
    db.close()
    return render_template('delivery_notes/list.html', delivery_notes=dns, company=company, lang=lang, tr=lambda k: tr(lang, k))

@delivery_notes_bp.route('/delivery_notes/<int:id>')
@login_required
def view_delivery_note(id):
    db = get_db(delivery_notes_bp)
    dn = db.get_delivery_note(id)
    items = []
    if dn and dn.quote_id:
        items = db.get_quote_items(dn.quote_id)
    company = db.get_company()
    lang = session.get('lang', 'en')
    db.close()
    return render_template('delivery_notes/view.html', dn=dn, items=items, company=company, lang=lang, tr=lambda k: tr(lang, k))

@delivery_notes_bp.route('/delivery_notes/<int:id>/pdf')
@login_required
def dn_pdf(id):
    from app.pdf_gen import generate_dn_pdf
    db = get_db(delivery_notes_bp)
    dn = db.get_delivery_note(id)
    items = db.get_quote_items(dn.quote_id) if dn and dn.quote_id else []
    company = db.get_company()
    path = generate_dn_pdf(company, dn, items)
    db.close()
    return send_file(path, as_attachment=True, download_name=f'dn_{dn.delivery_number}.pdf')

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/payments')
@login_required
def list_payments():
    db = get_db(payments_bp)
    payments = db.get_all_payments()
    company = db.get_company()
    lang = session.get('lang', 'en')
    db.close()
    return render_template('payments/list.html', payments=payments, company=company, lang=lang, tr=lambda k: tr(lang, k))

@payments_bp.route('/payments/<int:id>/delete')
@login_required
def delete_payment(id):
    db = get_db(payments_bp)
    db.delete_payment(id)
    db.close()
    return redirect(url_for('payments.list_payments'))
