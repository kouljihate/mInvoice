import os
from flask import Flask, session
from .utils import tr

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'mInvoice-web-dev-key')
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    app.config['DATABASE_PATH'] = os.path.join(root, 'data', 'db')
    app.config['PDF_DIR'] = os.path.join(root, 'pdfs')
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'logos')

    from .routes import register_blueprints
    register_blueprints(app)

    @app.context_processor
    def inject_tr():
        lang = session.get('lang', 'en')
        return dict(tr=lambda k: tr(lang, k))

    return app
