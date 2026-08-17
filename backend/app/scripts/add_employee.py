"""Add an employee from the command line.

Usage (from backend/):
    python -m app.scripts.add_employee <username> <password> "<full name>" \
        "<department>" [role]
"""

import sys

from ..db import execute, init_db, query_one
from ..security import hash_password


def main(argv):
    if len(argv) < 5:
        print(__doc__)
        return 1

    username, password, full_name, department = argv[1:5]
    role = argv[5] if len(argv) > 5 else "employee"

    init_db()

    if query_one("SELECT id FROM employees WHERE username = ?", (username,)):
        print(f"Username '{username}' already exists.")
        return 1

    execute(
        """
        INSERT INTO employees (username, password, full_name, department, role)
        VALUES (?, ?, ?, ?, ?)
        """,
        (username, hash_password(password), full_name, department, role),
    )

    print(f"Employee '{username}' added successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
