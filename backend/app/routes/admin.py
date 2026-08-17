"""Admin dashboard statistics and the full attendance table."""

from datetime import datetime

from flask import Blueprint, jsonify, request

from ..db import query_all, query_one
from ..security import admin_required

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _to_display_date(iso_date):
    """Turn the HTML date input's yyyy-mm-dd into the stored dd-mm-yyyy."""
    parts = iso_date.split("-")
    if len(parts) != 3:
        return None
    return f"{parts[2]}-{parts[1]}-{parts[0]}"


def _filtered_records(search, selected_date):
    query = """
        SELECT id, employee_username, attendance_date, attendance_time, status
        FROM attendance
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND employee_username LIKE ?"
        params.append(f"%{search}%")

    if selected_date:
        formatted = _to_display_date(selected_date)
        if formatted:
            query += " AND attendance_date = ?"
            params.append(formatted)

    query += " ORDER BY id DESC"
    return query_all(query, params)


@bp.get("/attendance")
@admin_required
def attendance():
    records = _filtered_records(
        request.args.get("search", "").strip(),
        request.args.get("date", "").strip(),
    )
    return jsonify({"records": records})


@bp.get("/stats")
@admin_required
def stats():
    today = datetime.now().strftime("%d-%m-%Y")

    total_employees = query_one("SELECT COUNT(*) AS count FROM employees")
    total_attendance = query_one("SELECT COUNT(*) AS count FROM attendance")

    present_today = query_one(
        "SELECT COUNT(*) AS count FROM attendance WHERE attendance_date = ?",
        (today,),
    )
    late_today = query_one(
        """
        SELECT COUNT(*) AS count
        FROM attendance
        WHERE attendance_date = ? AND status = 'Late'
        """,
        (today,),
    )

    return jsonify(
        {
            "total_employees": total_employees["count"],
            "total_attendance": total_attendance["count"],
            "present_today": present_today["count"],
            "late_today": late_today["count"],
        }
    )
