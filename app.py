from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import psycopg2
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # required for session

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def index():
    return render_template("index.html")  # login page

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password, role FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and user[2] == password:  # (later we’ll hash password for security)
        session["user_id"] = user[0]
        session["role"] = user[3]

        if user[3] == "student":
            return redirect(url_for("student_dashboard"))
        elif user[3] == "lecturer":
            return redirect(url_for("lecturer_dashboard"))
    else:
        return "Invalid username or password", 401

@app.route("/student-dashboard")
def student_dashboard():
    if session.get("role") == "student":
        return "Welcome Student Dashboard!"
    return redirect("/")

@app.route("/lecturer-dashboard")
def lecturer_dashboard():
    if session.get("role") == "lecturer":
        return "Welcome Lecturer Dashboard!"
    return redirect("/")
