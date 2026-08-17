import sqlite3

connection = sqlite3.connect("database/attendance.db")
cursor = connection.cursor()

# Employees Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    department TEXT NOT NULL
)
""")

# Attendance Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_username TEXT NOT NULL,
    attendance_date TEXT NOT NULL,
    attendance_time TEXT NOT NULL,
    status TEXT NOT NULL
)
""")

# Insert default employee only if it doesn't already exist
cursor.execute("SELECT * FROM employees WHERE username = ?", ("admin",))
employee = cursor.fetchone()

if employee is None:
    cursor.execute("""
    INSERT INTO employees (username, password, full_name, department)
    VALUES (?, ?, ?, ?)
    """, ("admin", "12345", "Admin User", "HR"))

connection.commit()

print("Database created successfully!")

connection.close()