from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.fe.web.utils import login_required, get_db, tr
from app.shared.models import Product

products_bp = Blueprint('products', __name__)

@products_bp.route('/products')
@login_required
def list_products():
    db = get_db(products_bp)
    q = request.args.get('q', '')
    products = db.search_products(q) if q else db.get_all_products()
    company = db.get_company()
    lang = session.get('lang', 'en')
    db.close()
    return render_template('products/list.html', products=products, q=q, company=company, lang=lang, tr=lambda k: tr(lang, k))

@products_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    db = get_db(products_bp)
    lang = session.get('lang', 'en')
    if request.method == 'POST':
        try:
            p = Product(
                name=request.form.get('name', ''),
                description=request.form.get('description', ''),
                reference=request.form.get('reference', ''),
                unit_price=float(request.form.get('unit_price', 0)),
                quantity=int(request.form.get('quantity', 0)),
                alert_stock=int(request.form.get('alert_stock', 0)),
                unit=request.form.get('unit', 'piece'),
                package_type=request.form.get('package_type', ''),
            )
        except ValueError:
            flash('Invalid number format', 'danger')
            db.close()
            return render_template('products/form.html', product=None, company=db.get_company(), lang=lang, tr=lambda k: tr(lang, k))
        db.insert_product(p)
        db.close()
        flash('Product saved', 'success')
        return redirect(url_for('products.list_products'))
    company = db.get_company()
    db.close()
    return render_template('products/form.html', product=None, company=company, lang=lang, tr=lambda k: tr(lang, k))

@products_bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    db = get_db(products_bp)
    lang = session.get('lang', 'en')
    if request.method == 'POST':
        try:
            p = Product(
                id=id,
                name=request.form.get('name', ''),
                description=request.form.get('description', ''),
                reference=request.form.get('reference', ''),
                unit_price=float(request.form.get('unit_price', 0)),
                quantity=int(request.form.get('quantity', 0)),
                alert_stock=int(request.form.get('alert_stock', 0)),
                unit=request.form.get('unit', 'piece'),
                package_type=request.form.get('package_type', ''),
            )
        except ValueError:
            flash('Invalid number format', 'danger')
            db.close()
            return render_template('products/form.html', product=db.get_product(id), company=db.get_company(), lang=lang, tr=lambda k: tr(lang, k))
        db.update_product(p)
        db.close()
        flash('Product updated', 'success')
        return redirect(url_for('products.list_products'))
    product = db.get_product(id)
    company = db.get_company()
    db.close()
    return render_template('products/form.html', product=product, company=company, lang=lang, tr=lambda k: tr(lang, k))

@products_bp.route('/products/<int:id>/delete')
@login_required
def delete_product(id):
    db = get_db(products_bp)
    db.delete_product(id)
    db.close()
    flash('Product deleted', 'success')
    return redirect(url_for('products.list_products'))
