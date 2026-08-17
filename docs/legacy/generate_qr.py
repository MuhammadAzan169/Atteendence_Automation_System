import qrcode

# Data to store inside the QR code
data = "http://127.0.0.1:5000/login"

# Create QR code
img = qrcode.make(data)

# Save the QR code image
img.save("static/images/company_qr.png")

print("QR Code generated successfully!")