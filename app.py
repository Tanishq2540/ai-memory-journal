import sqlite3
from groq_helper import generate_summary_and_reflection
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from init_db import init_db
from guardrail import is_input_safe
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/journal", methods=["GET", "POST"])
def journal():
    conn = get_db_connection()

    if request.method == "POST":
        entry = request.form["entry"]
        if not entry:
            return "Entry cannot be empty.", 400
        if len(entry) > 2000:
            return "Entry too long. Please limit to 2000 characters.", 400
        if not is_input_safe(entry):
            summary = "Summary not generated due to guideline violation."
            reflection = "Reflection not generated due to guideline violation."
            mood = "⚠️"
        else:
            date = datetime.now().strftime("%Y-%m-%d")
            mood_entries = conn.execute(
                "SELECT mood FROM journal_entries ORDER BY id DESC LIMIT 5"
            ).fetchall()
            recent_moods = [m["mood"] for m in mood_entries]
            summary, reflection, mood, emoji = generate_summary_and_reflection(entry, recent_moods)
            if not summary or not reflection or len(summary) > 1000 or len(reflection) > 1000:
                summary = "Summary not available."
                reflection = "Reflection not available."
        conn.execute(
            "INSERT INTO journal_entries (user_id, date, content, mood, ai_summary, ai_reflection) VALUES (?, ?, ?, ?, ?, ?)",
            (0, date, entry, mood, summary, reflection),
        )
        conn.commit()
        return redirect("/journal")

    entries = conn.execute(
        "SELECT * FROM journal_entries ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template("journal.html", entries=entries)

init_db()

if __name__ == "__main__":
    app.run(debug=True)
