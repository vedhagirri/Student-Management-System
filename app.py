from flask import Flask, render_template, request, redirect, url_for, Response
import sqlite3

app = Flask(__name__)

# Create Database
def create_table():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
        roll TEXT PRIMARY KEY,
        name TEXT,
        marks INTEGER,
        attendance INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

create_table()


# Login Page
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            return redirect(url_for("dashboard"))

    return render_template("login.html")


# Dashboard
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# Add Student
@app.route("/add", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        roll = request.form["roll"]
        name = request.form["name"]
        marks = int(request.form["marks"])

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO students VALUES (?, ?, ?, ?)",
                (roll, name, marks, 0)
            )

            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "Roll Number Already Exists!"

        conn.close()

        return redirect(url_for("students"))

    return render_template("add_student.html")

#report
@app.route("/students")
def students():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    conn.close()

    return render_template("students.html", students=data)


@app.route("/edit/<roll>", methods=["GET", "POST"])
def edit_student(roll):

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        marks = int(request.form["marks"])

        cursor.execute(
            "UPDATE students SET name=?, marks=? WHERE roll=?",
            (name, marks, roll)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("students"))

    cursor.execute(
        "SELECT * FROM students WHERE roll=?",
        (roll,)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template("edit_student.html", student=student)


# Attendance
@app.route("/attendance/<roll>")
def attendance(roll):

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE students SET attendance = attendance + 1 WHERE roll=?",
        (roll,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("students"))

# Search Student
@app.route("/search", methods=["GET", "POST"])
def search():

    data = []

    if request.method == "POST":

        roll = request.form["roll"]

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE roll=?",
            (roll,)
        )

        data = cursor.fetchall()

        conn.close()

    return render_template("search.html", students=data)



# Student Report
@app.route("/report")
def report():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(marks) FROM students")
    average = cursor.fetchone()[0]

    cursor.execute("SELECT MAX(marks) FROM students")
    highest = cursor.fetchone()[0]

    cursor.execute("SELECT MIN(marks) FROM students")
    lowest = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "report.html",
        total=total,
        average=round(average, 2) if average else 0,
        highest=highest,
        lowest=lowest
    )


# Export CSV
@app.route("/export")
def export():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    def generate():
        yield "Roll No,Name,Marks,Attendance\n"

        for student in students:
            yield f"{student[0]},{student[1]},{student[2]},{student[3]}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=students.csv"
        }
    )


# Logout
@app.route("/logout")
def logout():
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)