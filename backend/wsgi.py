"""WSGI entry point used by Gunicorn in production (Render / Docker)."""

from app import create_app

application = create_app()
app = application

if __name__ == "__main__":
    from app.config import Config

    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
