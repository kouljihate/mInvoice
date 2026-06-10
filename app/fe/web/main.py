import os
from flask import Flask, session
from config.settings import DB_DIR, PDF_DIR, SECRET_KEY, DEBUG, FLASK_HOST, FLASK_PORT
from app.shared.utils import tr_static
from app.fe.web.pages import register_blueprints

def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config['DATABASE_PATH'] = DB_DIR
    app.config['PDF_DIR'] = PDF_DIR
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'logos')

    register_blueprints(app)

    @app.context_processor
    def inject_tr():
        lang = session.get('lang', 'en')
        return dict(tr=lambda k: tr_static(lang, k))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=DEBUG, host=FLASK_HOST, port=FLASK_PORT)
