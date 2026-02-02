from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import sqlite3

app = Flask(__name__)

DB_PATH = "leaderboard.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            time_s REAL NOT NULL,
            outcome TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_score(name, email, time_s, outcome):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO scores (name, email, time_s, outcome, timestamp) VALUES (?, ?, ?, ?, ?)",
        (name, email, time_s, outcome, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    )
    conn.commit()
    conn.close()

def get_scores():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, email, time_s, outcome, timestamp FROM scores ORDER BY time_s ASC")
    rows = c.fetchall()
    conn.close()
    return rows

@app.route("/")
def index():
    rows = get_scores()

    indexed = list(enumerate(rows, start=1))  # ← THIS WAS MISSING!
    
    # 🧪 TEST DATA QUERY - ADDED HERE
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, time_s FROM scores WHERE name LIKE '%Test%' ORDER BY time_s ASC")
    test_scores = c.fetchall()
    conn.close()
    
    html = """
    <!doctype html>
    <html>
    <head>
        <title>WASK Leaderboard</title>
        <style>
            body { font-family: Arial, sans-serif; background: #111; color: #eee; }
            h1, h2 { text-align: center; }
            table { border-collapse: collapse; margin: 20px auto; width: 80%; max-width: 900px; }
            th, td { border: 1px solid #555; padding: 8px 12px; text-align: center; }
            th { background: #222; }
            tr:nth-child(even).normal-row { background: #1a1a1a; }
            tr.normal-row { background: #151515; }
            tr.gold   { background: #4d3b00; }
            tr.silver { background: #3b3f4d; }
            tr.bronze { background: #4d2f21; }
            tr.gold td, tr.silver td, tr.bronze td { font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>WASK Leaderboard</h1>
        <table>
            <tr>
                <th>#</th>
                <th>Name</th>
                <th>Time (s)</th>
                <th>Result</th>
                <th>Submitted</th>
            </tr>
            {% for i,row in rows %}
            {% set cls = "normal-row" %}
            {% set medal = "" %}
            {% if i == 1 %}
                {% set cls = "gold" %}
                {% set medal = "🥇 " %}
            {% elif i == 2 %}
                {% set cls = "silver" %}
                {% set medal = "🥈 " %}
            {% elif i == 3 %}
                {% set cls = "bronze" %}
                {% set medal = "🥉 " %}
            {% endif %}
            <tr class="{{ cls }}">
                <td>{{ medal }}{{ i }}</td>
                <td>{{ row[0] }}</td>
                <td>{{ "%.2f" % row[2] }}</td>
                <td>{{ row[3] }}</td>
                <td>{{ row[4] }}</td>
            </tr>
            {% endfor %}
        </table>
        
        <p style="text-align:center;">Play more to climb the leaderboard!</p>

        <!-- 🧪 TEST DATA TABLE -->
        {% if test_scores %}
        <h2 style="color: lime;">🧪 Test Data ({{ test_scores|length }})</h2>
        <table style="background: #0a3d0a; margin: 20px auto; width: 60%;">
            <tr><th>Rank</th><th>Test Player</th><th>Time (s)</th></tr>
            {% for i, row in enumerate(test_scores) %}
            <tr><td>{{ i+1 }}</td><td><strong style="color: lime;">{{ row[0] }}</strong></td><td>{{ "%.2f"|format(row[1]) }}</td></tr>
            {% endfor %}
        </table>
        {% endif %}

    </body>
    </html>
    """
    indexed = list(enumerate(rows, start=1))
    return render_template_string(html, rows=indexed, test_scores=test_scores)  # ← FIXED HERE

@app.route("/leaderboard")
def api_leaderboard():
    rows = get_scores()
    data = [
        {"name": r[0], "email": r[1], "time_s": r[2], "outcome": r[3], "timestamp": r[4]}
        for r in rows
    ]
    return jsonify(data)

@app.route("/submit_result", methods=["POST"])
def submit_result():
    data = request.get_json(force=True)
    name = (data.get("name") or "Player").strip()
    email = (data.get("email") or "").strip()
    time_s = float(data.get("time_s", 0.0))
    outcome = (data.get("outcome") or "unknown").strip()

    add_score(name, email, time_s, outcome)

    return jsonify({"status": "ok", "received": {
        "name": name,
        "email": email,
        "time_s": time_s,
        "outcome": outcome
    }})

@app.route('/health')
def health_check():
    """Health check endpoint - returns 200 OK for monitoring systems"""
    return "OK", 200

@app.route('/submit', methods=['POST'])
def submit_score():
    data = request.json
    conn = sqlite3.connect(DB_PATH)  # ← FIXED: Use DB_PATH
    c = conn.cursor()
    c.execute('INSERT INTO scores (name, time_s) VALUES (?, ?)',  # ← FIXED: time_s not score
              (data['name'], data['time_s']))  # ← FIXED: time_s not score
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
