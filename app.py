"""Attendance Automation System — one-click local launcher.

Run this file (or press Run in your editor) and the whole project starts:
the Flask API from backend/ plus the static pages from frontend/, both on
http://localhost:5000

Deployment splits the two — backend/ goes to Render, frontend/ to Vercel —
but locally a single process is far easier to work with.
"""

import subprocess
import sys
import webbrowser
from pathlib import Path
from threading import Timer

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"


def ensure_dependencies():
    """Install backend requirements on first run so nothing else is needed."""
    try:
        import flask  # noqa: F401
        import flask_cors  # noqa: F401
        import openpyxl  # noqa: F401
        import qrcode  # noqa: F401
        import reportlab  # noqa: F401

        return
    except ImportError:
        pass

    print("Installing backend dependencies (first run only)...\n")
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            str(BACKEND_DIR / "requirements.txt"),
        ]
    )
    print("\nDependencies installed.\n")


def ensure_env_file():
    """Create backend/.env from the example if it is missing."""
    env_file = BACKEND_DIR / ".env"
    example = BACKEND_DIR / ".env.example"

    if not env_file.exists() and example.exists():
        env_file.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Created {env_file.relative_to(ROOT_DIR)} from .env.example")


def main():
    ensure_dependencies()
    ensure_env_file()

    from backend.app import create_app
    from backend.app.config import Config

    application = create_app()

    url = f"http://localhost:{Config.PORT}"

    print("=" * 58)
    print("  Attendance Automation System")
    print("=" * 58)
    print(f"  App ........ {url}")
    print(f"  API ........ {url}/api/health")
    print(f"  Login ...... {Config.ADMIN_USERNAME} / {Config.ADMIN_PASSWORD}")
    print("=" * 58)
    print("  Press CTRL+C to stop.\n")

    # The reloader would open the browser twice.
    if not Config.DEBUG:
        Timer(1.0, lambda: webbrowser.open(url)).start()

    application.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)


if __name__ == "__main__":
    main()
