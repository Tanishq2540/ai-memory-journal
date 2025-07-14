import sqlite3
from groq_helper import generate_summary_and_reflection
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, url_for, g
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from init_db import init_db
from guardrail import is_input_safe
import os
import time

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def log_response_time(response):
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        print(f"⏱️ Response Time: {duration:.4f} seconds for {request.path}")
    return response

@app.route("/")
def index():
    return redirect("/login")

@app.route("/journal", methods=["GET", "POST"])
def journal():
    if "user_id" not in session:
        return redirect("/login")  

    conn = get_db_connection()

    if request.method == "POST":
        entry = request.form["entry"]
        if not entry:
            return "Entry cannot be empty.", 400
        if len(entry) > 2000:
            return "Entry too long. Please limit to 2000 characters.", 400
        if not is_input_safe(entry):
            return "⚠️ Your journal entry contains content that violates community guidelines."
        date = datetime.now().strftime("%Y-%m-%d")

        mood_entries = conn.execute(
            "SELECT mood FROM journal_entries WHERE user_id = ? ORDER BY id DESC LIMIT 5",
            (session["user_id"],),
        ).fetchall()
        recent_moods = [m["mood"] for m in mood_entries]

        summary, reflection, mood, emoji = generate_summary_and_reflection(entry, recent_moods)
        if not summary or not reflection or len(summary) > 1000 or len(reflection) > 1000:
            summary = "Summary not available."
            reflection = "Reflection not available."

        conn.execute(
            "INSERT INTO journal_entries (user_id, date, content, mood, ai_summary, ai_reflection) VALUES (?, ?, ?, ?, ?, ?)",
            (session["user_id"], date, entry, mood, summary, reflection),
        )
        conn.commit()
        return redirect("/journal")

    entries = conn.execute(
        "SELECT * FROM journal_entries WHERE user_id = ? ORDER BY id DESC",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    return render_template("journal.html", entries=entries)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except:
            return "Username already exists."
        conn.close()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"] 
            session["username"] = user["username"]
            return redirect("/journal")
        return "Invalid username or password."
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

init_db()

if __name__ == "__main__":
    app.run(debug=True)
