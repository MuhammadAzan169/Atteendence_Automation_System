"""Marking attendance and reading a user's own history."""

from datetime import datetime

from flask import Blueprint, g, jsonify

from ..config import Config
from ..db import execute, query_all, query_one
from ..security import login_required

bp = Blueprint("attendance", __name__, url_prefix="/api/attendance")

DATE_FORMAT = "%d-%m-%Y"
TIME_FORMAT = "%I:%M:%S %p"


def _status_for(now):
    late = (now.hour, now.minute) > (
        Config.LATE_AFTER_HOUR,
        Config.LATE_AFTER_MINUTE,
    )
    return "Late" if late else "Present"


@bp.post("/mark")
@login_required
def mark():
    username = g.user["username"]
    now = datetime.now()
    current_date = now.strftime(DATE_FORMAT)
    current_time = now.strftime(TIME_FORMAT)

    existing = query_one(
        """
        SELECT attendance_time, status
        FROM attendance
        WHERE employee_username = ? AND attendance_date = ?
        """,
        (username, current_date),
    )

    if existing:
        return jsonify(
            {
                "already_marked": True,
                "date": current_date,
                "time": existing["attendance_time"],
                "status": existing["status"],
                "message": "Attendance for today was already recorded.",
            }
        )

    status = _status_for(now)

    execute(
        """
        INSERT INTO attendance
            (employee_username, attendance_date, attendance_time, status)
        VALUES (?, ?, ?, ?)
        """,
        (username, current_date, current_time, status),
    )

    return jsonify(
        {
            "already_marked": False,
            "date": current_date,
            "time": current_time,
            "status": status,
            "message": "Attendance marked successfully.",
        }
    )


@bp.get("/history")
@login_required
def history():
    records = query_all(
        """
        SELECT attendance_date, attendance_time, status
        FROM attendance
        WHERE employee_username = ?
        ORDER BY id DESC
        """,
        (g.user["username"],),
    )
    return jsonify({"records": records})
