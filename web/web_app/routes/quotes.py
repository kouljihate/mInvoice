from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..utils import login_required, get_db, tr
from app.database import Quote, QuoteItem, DeliveryNote, Invoice, InvoiceItem

quotes_bp = Blueprint('quotes', __name__)

@quotes_bp.route('/quotes')
@login_required
def list_quotes():
    db = get_db(quotes_bp)
    quotes = db.get_all_quotes()
    company = db.get_company()
    lang = session.get('lang', 'en')
    db.close()
    return render_template('quotes/list.html', quotes=quotes, company=company, lang=lang, tr=lambda k: tr(lang, k))

@quotes_bp.route('/quotes/add', methods=['GET', 'POST'])
@login_required
def add_quote():
    db = get_db(quotes_bp)
    lang = session.get('lang', 'en')
    if request.method == 'POST':
        customer_id = request.form.get('customer_id', type=int)
        items_data = request.form.getlist('product_id[]')
        qties = request.form.getlist('qty[]')
        prices = request.form.getlist('price[]')
        product_names = request.form.getlist('product_name[]')
        if not items_data or not customer_id:
            flash('Select a customer and add at least one item', 'danger')
            db.close()
            return redirect(url_for('quotes.add_quote'))
        now = __import__('datetime').datetime.now().strftime('%Y-%m-%d')
        q = Quote(customer_id=customer_id, date=now, status='draft', notes=request.form.get('notes', ''))
        quote_id = db.insert_quote(q)
        items = []
        total_ht = 0.0
        for i, pid in enumerate(items_data):
            pid = int(pid) if pid else 0
            qty = int(qties[i]) if qties[i] else 1
            price = float(prices[i]) if prices[i] else 0
            item = QuoteItem(quote_id=quote_id, product_id=pid,
                           product_name=product_names[i] if i < len(product_names) else '',
                           quantity=qty, unit_price=price, tva_rate=20)
            items.append(item)
            total_ht += item.total_ht
        total_ttc = total_ht * 1.2
        q.id = quote_id
        q.total_ht = total_ht
        q.total_ttc = total_ttc
        db.update_quote(q)
        db.insert_quote_items(items)
        db.close()
        flash('Quote created', 'success')
        return redirect(url_for('quotes.list_quotes'))
    customers = db.get_all_customers()
    products = db.get_all_products()
    company = db.get_company()
    db.close()
    return render_template('quotes/form.html', quote=None, customers=customers, products=products, company=company, lang=lang, tr=lambda k: tr(lang, k))

@quotes_bp.route('/quotes/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_quote(id):
    db = get_db(quotes_bp)
    lang = session.get('lang', 'en')
    quote = db.get_quote(id)
    if not quote:
        db.close()
        return redirect(url_for('quotes.list_quotes'))
    if request.method == 'POST':
        customer_id = request.form.get('customer_id', type=int)
        items_data = request.form.getlist('product_id[]')
        qties = request.form.getlist('qty[]')
        prices = request.form.getlist('price[]')
        product_names = request.form.getlist('product_name[]')
        quote.customer_id = customer_id
        quote.notes = request.form.get('notes', '')
        db.delete_quote_items(id)
        items = []
        total_ht = 0.0
        for i, pid in enumerate(items_data):
            pid = int(pid) if pid else 0
            qty = int(qties[i]) if qties[i] else 1
            price = float(prices[i]) if prices[i] else 0
            item = QuoteItem(quote_id=id, product_id=pid,
                           product_name=product_names[i] if i < len(product_names) else '',
                           quantity=qty, unit_price=price, tva_rate=20)
            items.append(item)
            total_ht += item.total_ht
        quote.total_ht = total_ht
        quote.total_ttc = total_ht * 1.2
        db.update_quote(quote)
        db.insert_quote_items(items)
        db.close()
        flash('Quote updated', 'success')
        return redirect(url_for('quotes.list_quotes'))
    items = db.get_quote_items(id)
    customers = db.get_all_customers()
    products = db.get_all_products()
    company = db.get_company()
    db.close()
    return render_template('quotes/form.html', quote=quote, items=items, customers=customers, products=products, company=company, lang=lang, tr=lambda k: tr(lang, k))

@quotes_bp.route('/quotes/<int:id>')
@login_required
def view_quote(id):
    db = get_db(quotes_bp)
    quote = db.get_quote(id)
    items = db.get_quote_items(id)
    company = db.get_company()
    lang = session.get('lang', 'en')
    db.close()
    return render_template('quotes/view.html', quote=quote, items=items, company=company, lang=lang, tr=lambda k: tr(lang, k))

@quotes_bp.route('/quotes/<int:id>/validate', methods=['GET', 'POST'])
@login_required
def validate_quote(id):
    db = get_db(quotes_bp)
    quote = db.get_quote(id)
    if not quote:
        db.close()
        return redirect(url_for('quotes.list_quotes'))
    quote.status = 'validated'
    db.update_quote_status(id, 'validated')
    items = db.get_quote_items(id)
    now = __import__('datetime').datetime.now().strftime('%Y-%m-%d')
    dn = DeliveryNote(quote_id=id, customer_id=quote.customer_id, date=now,
                      total_ht=quote.total_ht, total_ttc=quote.total_ttc)
    dn_id = db.insert_delivery_note(dn)
    inv = Invoice(quote_id=id, delivery_note_id=dn_id, customer_id=quote.customer_id,
                  date=now, due_date='', status='draft',
                  total_ht=quote.total_ht, total_tva=quote.total_ttc - quote.total_ht,
                  total_ttc=quote.total_ttc)
    inv_id = db.insert_invoice(inv)
    invoice_items = []
    for item in items:
        invoice_items.append(InvoiceItem(
            invoice_id=inv_id, product_id=item.product_id,
            product_name=item.product_name, quantity=item.quantity,
            unit_price=item.unit_price, tva_rate=item.tva_rate
        ))
    if invoice_items:
        db.insert_invoice_items(invoice_items)
    db.close()
    flash(f'Quote validated! Delivery Note #{dn_id} and Invoice #{inv_id} created.', 'success')
    return redirect(url_for('quotes.view_quote', id=id))

@quotes_bp.route('/quotes/<int:id>/delete')
@login_required
def delete_quote(id):
    db = get_db(quotes_bp)
    db.delete_quote(id)
    db.close()
    flash('Quote deleted', 'success')
    return redirect(url_for('quotes.list_quotes'))

@quotes_bp.route('/quotes/<int:id>/pdf')
@login_required
def quote_pdf(id):
    from app.pdf_gen import generate_quote_pdf
    from flask import send_file
    db = get_db(quotes_bp)
    quote = db.get_quote(id)
    items = db.get_quote_items(id)
    company = db.get_company()
    path = generate_quote_pdf(company, quote, items)
    db.close()
    return send_file(path, as_attachment=True, download_name=f'quote_{quote.quote_number}.pdf')
