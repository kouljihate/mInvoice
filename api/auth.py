from functools import wraps
from flask import request, jsonify, session


def api_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if token == session.get("api_token"):
                return f(*args, **kwargs)
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


def generate_token():
    import secrets
    return secrets.token_hex(32)
