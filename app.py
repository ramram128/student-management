from flask import Flask, render_template, request
import os
import psycopg2

app = Flask(__name__)

# Home Page
@app.route("/")
def home():
    return "<h1>Welcome to Student Management System</h1><p>Choose Student or Lecturer</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
