from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/index", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    ).fetchone()

    if user:
        session["user"] = username
        session["role"] = user["role"]

        if user["role"] == "admin":
            return redirect("/admin")
        else:
            return redirect("/dashboard")

    return "Invalid login"


@app.route("/dashboard")
def dashboard():
    courses = ["Python", "Data Science", "Web Development", "Machine Learning"]
    return render_template("dashboard.html", courses=courses)


@app.route("/course/<name>")
def course(name):
    db = get_db()
    materials = db.execute(
        "SELECT * FROM materials WHERE course=?", (name,)
    ).fetchall()

    return render_template("course.html", materials=materials, course=name)


@app.route("/download/<id>")
def download(id):
    db = get_db()
    file = db.execute(
        "SELECT * FROM materials WHERE id=?", (id,)
    ).fetchone()

    return send_file(file["filepath"], as_attachment=True)


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/upload", methods=["POST"])
def upload():

    course = request.form["course"]
    file = request.files["file"]

    path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(path)

    db = get_db()
    db.execute(
        "INSERT INTO materials (course, filename, filepath) VALUES (?,?,?)",
        (course, file.filename, path)
    )
    db.commit()

    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=True)
