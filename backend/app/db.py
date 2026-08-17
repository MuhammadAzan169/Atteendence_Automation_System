"""Database access layer.

Works with SQLite (default, zero setup) and PostgreSQL (set DATABASE_URL).
Queries are written once with "?" placeholders and translated when running
against Postgres.
"""

import os
import sqlite3
from pathlib import Path

from .config import Config

IS_POSTGRES = Config.DATABASE_URL.startswith(("postgres://", "postgresql://"))

if IS_POSTGRES:
    import psycopg2
    import psycopg2.extras


def _pg_url():
    url = Config.DATABASE_URL
    # psycopg2 does not accept the legacy "postgres://" scheme.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def get_connection():
    if IS_POSTGRES:
        return psycopg2.connect(_pg_url())

    path = Path(Config.SQLITE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    return connection


def _translate(query):
    """Rewrite the shared SQL dialect for the active backend."""
    if not IS_POSTGRES:
        return query
    query = query.replace("?", "%s")
    query = query.replace(
        "INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY"
    )
    return query


def query_all(sql, params=()):
    """Run a SELECT and return a list of plain dicts."""
    connection = get_connection()
    try:
        if IS_POSTGRES:
            cursor = connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )
        else:
            cursor = connection.cursor()
        cursor.execute(_translate(sql), tuple(params))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def query_one(sql, params=()):
    rows = query_all(sql, params)
    return rows[0] if rows else None


def execute(sql, params=()):
    """Run an INSERT/UPDATE/DELETE and commit."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(_translate(sql), tuple(params))
        connection.commit()
        return cursor.rowcount
    finally:
        connection.close()


def init_db():
    """Create tables and seed the default admin. Safe to run repeatedly."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        _translate(
            """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                department TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'employee'
            )
            """
        )
    )

    cursor.execute(
        _translate(
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_username TEXT NOT NULL,
                attendance_date TEXT NOT NULL,
                attendance_time TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
    )

    # Older databases from the pre-split version lack the role column.
    if not IS_POSTGRES:
        columns = [row[1] for row in cursor.execute("PRAGMA table_info(employees)")]
        if "role" not in columns:
            cursor.execute(
                "ALTER TABLE employees ADD COLUMN role TEXT DEFAULT 'employee'"
            )

    connection.commit()
    connection.close()

    _seed_admin()


def _seed_admin():
    from .security import hash_password

    existing = query_one(
        "SELECT id FROM employees WHERE username = ?", (Config.ADMIN_USERNAME,)
    )
    if existing:
        return

    execute(
        """
        INSERT INTO employees (username, password, full_name, department, role)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            Config.ADMIN_USERNAME,
            hash_password(Config.ADMIN_PASSWORD),
            "Admin User",
            "HR",
            "admin",
        ),
    )
    print(f"Seeded admin account: {Config.ADMIN_USERNAME}")
