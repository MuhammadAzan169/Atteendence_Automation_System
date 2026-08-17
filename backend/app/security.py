"""Password hashing and stateless auth tokens.

Uses only libraries that already ship with Flask (Werkzeug + itsdangerous),
so there is nothing extra to install.
"""

from functools import wraps

from flask import g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from .config import Config
from .db import execute, query_one

_serializer = URLSafeTimedSerializer(Config.SECRET_KEY, salt="attendance-auth")

# Prefixes Werkzeug uses for its hashes; anything else is a legacy
# plaintext password from the original single-file version of the app.
_HASH_PREFIXES = ("pbkdf2:", "scrypt:", "argon2", "sha256$")


def hash_password(password):
    return generate_password_hash(password)


def verify_password(username, stored, provided):
    """Check a password, transparently upgrading legacy plaintext rows."""
    if stored.startswith(_HASH_PREFIXES):
        return check_password_hash(stored, provided)

    if stored == provided:
        execute(
            "UPDATE employees SET password = ? WHERE username = ?",
            (hash_password(provided), username),
        )
        return True

    return False


def create_token(username, role):
    return _serializer.dumps({"username": username, "role": role})


def read_token(token):
    try:
        return _serializer.loads(
            token, max_age=Config.TOKEN_TTL_HOURS * 3600
        )
    except (BadSignature, SignatureExpired):
        return None


def _extract_token():
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[7:].strip()
    # Download links (Excel/PDF) open in a new tab and cannot set headers.
    return request.args.get("token")


def _current_user():
    token = _extract_token()
    if not token:
        return None

    data = read_token(token)
    if not data:
        return None

    return query_one(
        """
        SELECT id, username, full_name, department, role
        FROM employees
        WHERE username = ?
        """,
        (data["username"],),
    )


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = _current_user()
        if not user:
            return jsonify({"error": "Authentication required."}), 401
        g.user = user
        return view(*args, **kwargs)

    return wrapper


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        if g.user["role"] != "admin":
            return jsonify({"error": "Administrator access required."}), 403
        return view(*args, **kwargs)

    return wrapper
