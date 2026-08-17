import sqlite3

connection = sqlite3.connect("database/attendance.db")
cursor = connection.cursor()

cursor.execute("DELETE FROM attendance")

connection.commit()
connection.close()

print("All attendance records deleted successfully!")