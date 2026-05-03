from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

app.config["SESSION_PERMANENT"] = True


# 🔹 Database setup
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll TEXT UNIQUE,
            course TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


# 🔹 LOGIN PAGE
@app.route("/")
def login():
    return render_template("login.html")


# 🔹 DASHBOARD (LOGIN HANDLER)
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        name = request.form.get("name")
        roll = request.form.get("roll")

        if not name or not roll:
            return "<h3>Name and Roll required</h3>"

        session["name"] = name
        session["roll"] = roll

        return redirect("/home")

    if "name" not in session:
        return redirect("/")

    return redirect("/home")


# 🔹 HOME PAGE (MAIN MENU)
@app.route("/home")
def home():
    if "name" not in session:
        return redirect("/")

    return render_template("dashboard.html", name=session["name"])


# 🔹 SUBMIT COURSE
@app.route("/submit", methods=["GET", "POST"])
def submit():
    if "name" not in session:
        return redirect("/")

    if request.method == "POST":
        course = request.form.get("course")

        if not course:
            return "<h3>Course required</h3>"

        name = session["name"]
        roll = session["roll"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO records (name, roll, course, status) VALUES (?, ?, ?, ?)",
                (name, roll, course, "Pending")
            )
            conn.commit()
        except:
            conn.close()
            return "<h3>You already submitted!</h3>"

        conn.close()
        return redirect("/status")

    return render_template("submit.html")


# 🔹 STATUS PAGE
@app.route("/status")
def status():
    if "name" not in session:
        return redirect("/")

    roll = session["roll"]

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM records WHERE roll=?", (roll,))
    records = cur.fetchall()
    conn.close()

    return render_template("status.html", records=records)


# 🔹 TEACHER LOGIN
@app.route("/teacher_login", methods=["GET", "POST"])
def teacher_login():
    if request.method == "POST":
        if request.form.get("password") == "admin123":
            session["teacher"] = True
            return redirect("/teacher")
        else:
            return "<h3>Wrong Password</h3>"

    return render_template("teacher_login.html")


# 🔹 TEACHER PANEL
@app.route("/teacher")
def teacher():
    if not session.get("teacher"):
        return redirect("/teacher_login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM records")
    records = cur.fetchall()
    conn.close()

    return render_template("teacher.html", records=records)


# 🔹 APPROVE
@app.route("/approve/<int:id>")
def approve(id):
    if not session.get("teacher"):
        return redirect("/teacher_login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("UPDATE records SET status='Approved' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/teacher")


# 🔹 REJECT
@app.route("/reject/<int:id>")
def reject(id):
    if not session.get("teacher"):
        return redirect("/teacher_login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("UPDATE records SET status='Rejected' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/teacher")


# 🔹 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# 🔹 RUN APP
if __name__ == "__main__":
    app.run(debug=True)