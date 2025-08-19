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
    cur.execute("SELECT id, username, password, role FROM students WHERE username=%s", (username,))
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

@app.route("/student_dashboard")
def student_dashboard():
    if "role" in session and session["role"] == "student":
        return render_template("student.html")
    return redirect(url_for("login"))

@app.route("/lecturer_dashboard")
def lecturer_dashboard():
    if "role" in session and session["role"] == "lecturer":
        return render_template("lecturer.html")
    return redirect(url_for("login"))

@app.route("/update_student_page")
def update_student_page():
    if "role" in session and session["role"] == "student":
        return render_template("update_student.html")
    return redirect(url_for("login"))

@app.route("/update_student", methods=["POST"])
def update_student():
    if "role" in session and session["role"] == "student":
        try:
            # collect form inputs
            fields = {
                "fullname": request.form.get("name"),
                "email": request.form.get("email"),
                "phone": request.form.get("phone"),
                "cgpa": request.form.get("cgpa"),
                "aadhar": request.form.get("aadhar"),
                "pan": request.form.get("pan"),
                "address": request.form.get("address"),
                "parent_mobile": request.form.get("parent_mobile")
            }

            # filter out empty values (None or "")
            updates = {k: v for k, v in fields.items() if v and v.strip()}

            if not updates:
                return "No details provided to update!", 400

            conn = get_db_connection()
            cur = conn.cursor()

            # build SET clause dynamically
            set_clause = ", ".join([f"{k}=%s" for k in updates.keys()])
            values = list(updates.values()) + [session["user_id"]]

            cur.execute(f"""
                INSERT INTO student_details (user_id, {", ".join(updates.keys())})
                VALUES (%s, {", ".join(["%s"] * len(updates))})
                ON CONFLICT (user_id) DO UPDATE
                SET {set_clause}
            """, [session["user_id"]] + list(updates.values()) + list(updates.values()))

            conn.commit()
            cur.close()
            conn.close()

            return "Details updated successfully!"

        except Exception as e:
            return f"Error while updating: {str(e)}", 500

    return redirect(url_for("login"))


@app.route("/view_details")
def view_details():
    if "user_id" not in session:
        return redirect(url_for("index"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT fullname, email, phone, cgpa, aadhar, pan, address, parent_mobile FROM student_details WHERE user_id = %s", (session["user_id"],))
    details = cur.fetchone()
    cur.close()
    conn.close()

    return render_template("student_view.html", details=details)


