"""Excel and PDF exports of the attendance table.

Both files are built in memory so the service never writes to disk, which
keeps it compatible with read-only / ephemeral hosting like Render's free
web service.
"""

from io import BytesIO

from flask import Blueprint, send_file

from ..db import query_all
from ..security import admin_required

bp = Blueprint("reports", __name__, url_prefix="/api/reports")

HEADERS = ["Employee", "Date", "Time", "Status"]


def _records():
    return query_all(
        """
        SELECT employee_username, attendance_date, attendance_time, status
        FROM attendance
        ORDER BY id DESC
        """
    )


def _rows():
    return [
        [
            record["employee_username"],
            record["attendance_date"],
            record["attendance_time"],
            record["status"],
        ]
        for record in _records()
    ]


@bp.get("/excel")
@admin_required
def excel():
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Attendance Report"

    sheet.append(HEADERS)
    for row in _rows():
        sheet.append(row)

    for column, width in zip("ABCD", (22, 16, 16, 14)):
        sheet.column_dimensions[column].width = width

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="attendance_report.xlsx",
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )


@bp.get("/pdf")
@admin_required
def pdf():
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

    buffer = BytesIO()
    document = SimpleDocTemplate(buffer)

    table = Table([HEADERS] + _rows())
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ]
        )
    )

    document.build([table])
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="attendance_report.pdf",
        mimetype="application/pdf",
    )
