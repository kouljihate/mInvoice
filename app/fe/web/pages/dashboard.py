from flask import Blueprint, render_template, session
from app.fe.web.utils import login_required, get_db, tr

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    db = get_db(dashboard_bp)
    data = db.get_dashboard_data()
    company = db.get_company()
    lang = session.get('lang', 'en')
    db.close()
    return render_template('dashboard.html', d=data, company=company, lang=lang, tr=lambda k: tr(lang, k))
