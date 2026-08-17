"""Create the tables and seed the default admin account.

Usage (from backend/):  python -m app.scripts.init_db
"""

from ..db import init_db

if __name__ == "__main__":
    init_db()
    print("Database ready.")
