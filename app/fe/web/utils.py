from functools import wraps
from flask import session, redirect, url_for, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def get_db(_app=None):
    from app.shared.db import Database
    return Database()

def tr(lang, key, **kwargs):
    from app.shared.utils import tr_static
    return tr_static(lang or 'en', key, **kwargs)
