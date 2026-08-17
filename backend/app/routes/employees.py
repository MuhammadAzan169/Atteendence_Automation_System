"""Admin-only employee management."""

from flask import Blueprint, g, jsonify, request

from ..db import execute, query_all, query_one
from ..security import admin_required, hash_password

bp = Blueprint("employees", __name__, url_prefix="/api/employees")


@bp.get("")
@admin_required
def list_employees():
    employees = query_all(
        """
        SELECT id, username, full_name, department, role
        FROM employees
        ORDER BY id
        """
    )
    return jsonify({"employees": employees})


@bp.post("")
@admin_required
def create_employee():
    payload = request.get_json(silent=True) or {}

    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    full_name = (payload.get("full_name") or "").strip()
    department = (payload.get("department") or "").strip()
    role = payload.get("role") or "employee"

    if not (username and password and full_name and department):
        return jsonify({"error": "All fields are required."}), 400

    if role not in ("employee", "admin"):
        return jsonify({"error": "Role must be 'employee' or 'admin'."}), 400

    if query_one("SELECT id FROM employees WHERE username = ?", (username,)):
        return jsonify({"error": "That username already exists."}), 409

    execute(
        """
        INSERT INTO employees (username, password, full_name, department, role)
        VALUES (?, ?, ?, ?, ?)
        """,
        (username, hash_password(password), full_name, department, role),
    )

    return jsonify({"message": "Employee added successfully."}), 201


@bp.delete("/<int:employee_id>")
@admin_required
def delete_employee(employee_id):
    employee = query_one(
        "SELECT username FROM employees WHERE id = ?", (employee_id,)
    )

    if not employee:
        return jsonify({"error": "Employee not found."}), 404

    if employee["username"] == g.user["username"]:
        return jsonify({"error": "You cannot delete your own account."}), 400

    execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    execute(
        "DELETE FROM attendance WHERE employee_username = ?",
        (employee["username"],),
    )

    return jsonify({"message": "Employee deleted successfully."})
