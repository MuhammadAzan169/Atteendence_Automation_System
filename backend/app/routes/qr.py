"""Company QR code.

The QR encodes a permanent link to the attendance page plus a fixed company
code:

    https://<frontend>/attendance.html?qr=AAS-COMPANY-QR-001

Nothing in it expires — there is no timestamp and no signature — so a printed
poster keeps working indefinitely. The image is drawn on demand by the
`qrcode` library, so it never depends on an external (paid or rate-limited)
QR service.
"""

from io import BytesIO
from urllib.parse import quote

from flask import Blueprint, jsonify, request, send_file

from ..config import Config
from ..security import login_required

bp = Blueprint("qr", __name__, url_prefix="/api/qr")


def qr_payload():
    """The exact string encoded in the QR image."""
    base = Config.FRONTEND_URL.rstrip("/")
    return f"{base}/attendance.html?qr={quote(Config.COMPANY_CODE)}"


@bp.get("/image")
def image():
    """PNG of the company QR code. Public, so it can be shown in an <img>."""
    import qrcode
    from qrcode.constants import ERROR_CORRECT_H

    # High error correction keeps a printed poster readable even when the
    # paper is scuffed or partly covered.
    code = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=10, border=4)
    code.add_data(qr_payload())
    code.make(fit=True)

    buffer = BytesIO()
    code.make_image(fill_color="black", back_color="white").save(
        buffer, format="PNG"
    )
    buffer.seek(0)

    response = send_file(buffer, mimetype="image/png")
    # The payload only changes when FRONTEND_URL / COMPANY_CODE change.
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response


@bp.get("/payload")
def payload():
    """What the QR contains — used by the on-screen fallback flow."""
    return jsonify({"payload": qr_payload(), "code": Config.COMPANY_CODE})


@bp.post("/verify")
@login_required
def verify():
    """Check a scanned code against this company's installation."""
    body = request.get_json(silent=True) or {}
    scanned = (body.get("code") or "").strip()

    # A full scanned URL is accepted as well as the bare code.
    if scanned.startswith("http") and "qr=" in scanned:
        scanned = scanned.split("qr=", 1)[1].split("&", 1)[0]

    if scanned != Config.COMPANY_CODE:
        return (
            jsonify(
                {
                    "verified": False,
                    "error": "This QR code does not belong to your company.",
                }
            ),
            400,
        )

    return jsonify({"verified": True})
