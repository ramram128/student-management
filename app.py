from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

# Get database URL from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Create table if not exists
with get_db_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        """)
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/students')
def show_students():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM students ORDER BY id")
    students = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('students.html', students=students)

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form['name']
    email = request.form['email']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO students (name, email) VALUES (%s, %s)", (name, email))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/students')

if __name__ == '__main__':
    app.run()
