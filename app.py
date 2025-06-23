import sqlite3
from groq_helper import generate_summary_and_reflection
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

load_dotenv()
app = Flask(__name__)
app.secret_key = 'myAppPass'  # Use something secure

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
@app.route("/")
def index():
    return redirect("/login")

@app.route("/journal", methods=["GET", "POST"])
def journal():
    if "user_id" not in session:
        return redirect("/login")  # 🚫 Block if not logged in

    conn = get_db_connection()

    if request.method == "POST":
        # Handle new entry
        entry = request.form["entry"]
        date = datetime.now().strftime("%Y-%m-%d")

        # Fetch recent moods of current user
        mood_entries = conn.execute(
            "SELECT mood FROM journal_entries WHERE user_id = ? ORDER BY id DESC LIMIT 5",
            (session["user_id"],),
        ).fetchall()
        recent_moods = [m["mood"] for m in mood_entries]

        summary, reflection, mood, emoji = generate_summary_and_reflection(entry, recent_moods)

        # Save entry in database
        conn.execute(
            "INSERT INTO journal_entries (user_id, date, content, mood, ai_summary, ai_reflection) VALUES (?, ?, ?, ?, ?, ?)",
            (session["user_id"], date, entry, mood, summary, reflection),
        )
        conn.commit()
        return redirect("/journal")

    # Fetch only this user's entries
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



if __name__ == "__main__":
    app.run(debug=True)
