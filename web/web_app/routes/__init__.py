from .auth import auth_bp
from .dashboard import dashboard_bp
from .customers import customers_bp
from .products import products_bp
from .quotes import quotes_bp
from .invoices import invoices_bp
from .delivery_notes import delivery_notes_bp, payments_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(quotes_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(delivery_notes_bp)
    app.register_blueprint(payments_bp)
