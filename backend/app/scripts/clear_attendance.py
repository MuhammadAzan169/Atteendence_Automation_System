"""Delete every attendance record (employees are kept).

Usage (from backend/):  python -m app.scripts.clear_attendance
"""

from ..db import execute

if __name__ == "__main__":
    deleted = execute("DELETE FROM attendance")
    print(f"Deleted {deleted} attendance record(s).")
