#!/usr/bin/env python3
import sys

def run_mobile():
    from app.fe.mobile.main import main
    import flet as ft
    ft.run(main, assets_dir="app/fe/mobile/assets")

def run_web():
    from app.fe.web.main import create_app
    from config.settings import DEBUG, FLASK_HOST, FLASK_PORT
    app = create_app()
    app.run(debug=DEBUG, host=FLASK_HOST, port=FLASK_PORT)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "web"
    if mode == "mobile":
        run_mobile()
    elif mode == "web":
        run_web()
    else:
        print("Usage: python run.py [web|mobile]")
        sys.exit(1)
