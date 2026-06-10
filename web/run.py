import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from web_app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
