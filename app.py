from flask import Flask, render_template, request, jsonify
import sqlite3, os, datetime

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", "contact.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                ip TEXT
            )
        """)

@app.before_first_request
def _init():
    init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/contact", methods=["POST"])
def contact():
    # Basic anti-spam “honeypot”
    if request.form.get("website"):  # hidden field; real users won't fill it
        return jsonify({"ok": True}), 200

    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    message = (request.form.get("message") or "").strip()

    if not name or not email or not message:
        return jsonify({"ok": False, error: "Missing fields"}), 400

    created_at = datetime.datetime.utcnow().isoformat()
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages(name, email, message, created_at, ip) VALUES (?,?,?,?,?)",
            (name, email, message, created_at, ip)
        )

    return jsonify({"ok": True, "msg": "Thanks for reaching out!"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
