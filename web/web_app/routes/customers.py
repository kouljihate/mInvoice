from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..utils import login_required, get_db, tr
from app.database import Customer

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customers')
@login_required
def list_customers():
    db = get_db(customers_bp)
    q = request.args.get('q', '')
    customers = db.search_customers(q) if q else db.get_all_customers()
    company = db.get_company()
    lang = session.get('lang', 'en')
    db.close()
    return render_template('customers/list.html', customers=customers, q=q, company=company, lang=lang, tr=lambda k: tr(lang, k))

@customers_bp.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    db = get_db(customers_bp)
    lang = session.get('lang', 'en')
    if request.method == 'POST':
        c = Customer(
            name=request.form.get('name', ''),
            customer_type=request.form.get('customer_type', 'private'),
            address=request.form.get('address', ''),
            phone=request.form.get('phone', ''),
            email=request.form.get('email', ''),
            tax_id=request.form.get('tax_id', ''),
            rc=request.form.get('rc', ''),
            if_tax=request.form.get('if_tax', ''),
            cnss=request.form.get('cnss', ''),
        )
        db.insert_customer(c)
        db.close()
        flash('Customer saved', 'success')
        return redirect(url_for('customers.list_customers'))
    company = db.get_company()
    db.close()
    return render_template('customers/form.html', customer=None, company=company, lang=lang, tr=lambda k: tr(lang, k))

@customers_bp.route('/customers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    db = get_db(customers_bp)
    lang = session.get('lang', 'en')
    if request.method == 'POST':
        c = Customer(
            id=id,
            name=request.form.get('name', ''),
            customer_type=request.form.get('customer_type', 'private'),
            address=request.form.get('address', ''),
            phone=request.form.get('phone', ''),
            email=request.form.get('email', ''),
            tax_id=request.form.get('tax_id', ''),
            rc=request.form.get('rc', ''),
            if_tax=request.form.get('if_tax', ''),
            cnss=request.form.get('cnss', ''),
        )
        db.update_customer(c)
        db.close()
        flash('Customer updated', 'success')
        return redirect(url_for('customers.list_customers'))
    customer = db.get_customer(id)
    company = db.get_company()
    db.close()
    return render_template('customers/form.html', customer=customer, company=company, lang=lang, tr=lambda k: tr(lang, k))

@customers_bp.route('/customers/<int:id>/delete')
@login_required
def delete_customer(id):
    db = get_db(customers_bp)
    db.delete_customer(id)
    db.close()
    flash('Customer deleted', 'success')
    return redirect(url_for('customers.list_customers'))
