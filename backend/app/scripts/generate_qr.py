"""Save the company QR code as a PNG file.

The running API also serves it live at /api/qr/image; this script is only
useful when you want a printable copy.

Usage (from backend/):  python -m app.scripts.generate_qr [output.png]
"""

import sys

import qrcode
from qrcode.constants import ERROR_CORRECT_H

from ..routes.qr import qr_payload

if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "company_qr.png"
    payload = qr_payload()

    code = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=12, border=4)
    code.add_data(payload)
    code.make(fit=True)
    code.make_image(fill_color="black", back_color="white").save(output)

    print(f"QR code saved to {output}")
    print(f"It encodes: {payload}")
