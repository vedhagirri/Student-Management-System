import sqlite3

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    roll TEXT,
    name TEXT,
    marks INTEGER
)
""")

conn.commit()
conn.close()

print("Database Created Successfully")