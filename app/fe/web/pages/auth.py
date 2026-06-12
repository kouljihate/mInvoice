from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import __version__
from app.fe.web.utils import get_db, tr
from app.shared.models import Company, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db(auth_bp)
    company = db.get_company()
    if company and company.name:
        pass
    else:
        first_user = db.get_first_user()
        if not first_user:
            db.close()
            return redirect(url_for('auth.setup'))
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = db.login(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.full_name
            session['lang'] = 'en'
            db.close()
            return redirect(url_for('dashboard.dashboard'))
        db.close()
        return render_template('login.html', error=True, version=__version__)
    db.close()
    return render_template('login.html', error=False, version=__version__)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    db = get_db(auth_bp)
    if db.get_company() and db.get_company().name and db.get_first_user():
        db.close()
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        company = Company(
            name=request.form.get('name', ''),
            address=request.form.get('address', ''),
            city=request.form.get('city', ''),
            postal_code=request.form.get('postal_code', ''),
            phone=request.form.get('phone', ''),
            email=request.form.get('email', ''),
            website=request.form.get('website', ''),
            tax_id=request.form.get('tax_id', ''),
            ice=request.form.get('ice', ''),
            rc=request.form.get('rc', ''),
            if_tax=request.form.get('if_tax', ''),
            tp=request.form.get('tp', ''),
            cnss=request.form.get('cnss', ''),
            bank_account=request.form.get('bank_account', ''),
            slogan=request.form.get('slogan', ''),
            currency=request.form.get('currency', 'MAD'),
        )
        db.save_company(company)
        user = User(
            username=request.form.get('username', 'admin'),
            password=request.form.get('password', 'admin'),
            full_name=request.form.get('full_name', 'Admin'),
        )
        db.insert_user(user)
        db.create_default_invoice_template()
        existing = {s.section_key: s for s in db.get_template_sections("invoice")}
        section_keys = [
            "header_company_info", "header_customer_info", "body_title",
            "body_attention", "body_items_table", "body_note1", "body_note2",
            "footer_left", "footer_right",
        ]
        for key in section_keys:
            if key in existing:
                existing[key].is_visible = request.form.get(f"section_{key}") == "on"
                db.save_template_section(existing[key])
        db.close()
        flash('Company setup complete! Please login.', 'success')
        return redirect(url_for('auth.login'))
    db.close()
    return render_template('setup.html')
