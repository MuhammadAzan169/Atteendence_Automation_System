"""Configuration loaded from environment variables (see backend/.env)."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_dotenv():
    """Minimal .env loader so the project runs with zero extra dependencies."""
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()


def _as_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


class Config:
    # --- Security -----------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    TOKEN_TTL_HOURS = int(os.environ.get("TOKEN_TTL_HOURS", "12"))

    # --- Database -----------------------------------------------------
    # Leave DATABASE_URL empty to use the bundled SQLite file.
    # Set it to a postgres:// URL (e.g. Render's free Postgres) for a
    # database that survives redeploys.
    DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
    SQLITE_PATH = os.environ.get(
        "SQLITE_PATH", str(BASE_DIR / "database" / "attendance.db")
    )

    # --- CORS ---------------------------------------------------------
    # Comma separated list of allowed frontend origins, or "*" for any.
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    # --- App behaviour ------------------------------------------------
    # Attendance later than this counts as "Late".
    LATE_AFTER_HOUR = int(os.environ.get("LATE_AFTER_HOUR", "9"))
    LATE_AFTER_MINUTE = int(os.environ.get("LATE_AFTER_MINUTE", "0"))

    # Public URL of the deployed frontend, encoded into the company QR code.
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5000")

    # Fixed identifier printed inside the company QR code. It is a constant,
    # never a timestamped or signed value, so a printed QR poster stays valid
    # forever. Change it only if you need to invalidate printed posters.
    COMPANY_CODE = os.environ.get("COMPANY_CODE", "AAS-COMPANY-QR-001")

    # Serve the frontend/ folder from Flask too (handy for local one-click run).
    SERVE_FRONTEND = _as_bool(os.environ.get("SERVE_FRONTEND"), True)

    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))
    DEBUG = _as_bool(os.environ.get("FLASK_DEBUG"), False)

    # Seeded admin account created on first run.
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "12345")
