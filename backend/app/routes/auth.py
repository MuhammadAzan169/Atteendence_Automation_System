"""Login / session endpoints."""

from flask import Blueprint, g, jsonify, request

from ..db import query_one
from ..security import create_token, login_required, verify_password

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    employee = query_one(
        """
        SELECT username, password, full_name, department, role
        FROM employees
        WHERE username = ?
        """,
        (username,),
    )

    if not employee or not verify_password(
        username, employee["password"], password
    ):
        return jsonify({"error": "Invalid username or password."}), 401

    role = employee["role"] or "employee"

    return jsonify(
        {
            "token": create_token(username, role),
            "user": {
                "username": employee["username"],
                "full_name": employee["full_name"],
                "department": employee["department"],
                "role": role,
            },
        }
    )


@bp.get("/me")
@login_required
def me():
    return jsonify(
        {
            "username": g.user["username"],
            "full_name": g.user["full_name"],
            "department": g.user["department"],
            "role": g.user["role"],
        }
    )
