import sqlite3

connection = sqlite3.connect("database/attendance.db")

cursor = connection.cursor()

cursor.execute("""
INSERT INTO employees (username, password, full_name, department)
VALUES (?, ?, ?, ?)
""", ("admin", "12345", "Admin User", "HR"))

connection.commit()

print("Employee added successfully!")

connection.close()