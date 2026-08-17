import sqlite3
connection = sqlite3.connect("database/attendance.db")
cursor = connection.cursor()
# Add role column (ignore if it already exists)
try:
    cursor.execute("""
        ALTER TABLE employees
        ADD COLUMN role TEXT DEFAULT 'employee'
    """)
    print("Role column added successfully.")
except sqlite3.OperationalError:
    print("Role column already exists.")
# Make the admin user an admin
cursor.execute("""
    UPDATE employees
    SET role = 'admin'
    WHERE username = 'admin'
""")
# Make every other user an employee
cursor.execute("""
    UPDATE employees
    SET role = 'employee'
    WHERE username != 'admin'
""")

connection.commit()
connection.close()
print("Database updated successfully.")