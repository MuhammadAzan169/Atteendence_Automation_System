"""Application factory for the Attendance Automation System API."""

import os
from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from .config import Config
from .db import init_db
from .routes import admin, attendance, auth, employees, qr, reports

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    origins = (
        "*"
        if Config.CORS_ORIGINS.strip() == "*"
        else [o.strip() for o in Config.CORS_ORIGINS.split(",") if o.strip()]
    )
    CORS(app, resources={r"/api/*": {"origins": origins}})

    init_db()

    for module in (auth, attendance, employees, admin, reports, qr):
        app.register_blueprint(module.bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "attendance-api"})

    _register_frontend(app)
    _register_errors(app)

    return app


def _register_frontend(app):
    """Optionally serve frontend/ so the whole app runs from one process."""
    if not Config.SERVE_FRONTEND or not FRONTEND_DIR.exists():
        return

    @app.get("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.get("/<path:filename>")
    def static_files(filename):
        target = FRONTEND_DIR / filename
        if target.is_file():
            return send_from_directory(FRONTEND_DIR, filename)
        # Allow extension-less URLs like /dashboard
        if (FRONTEND_DIR / f"{filename}.html").is_file():
            return send_from_directory(FRONTEND_DIR, f"{filename}.html")
        return jsonify({"error": "Not found."}), 404


def _register_errors(app):
    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Not found."}), 404

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({"error": "Internal server error."}), 500
