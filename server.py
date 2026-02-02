from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)

# Use Render's writable /tmp directory when deployed, otherwise local
if os.environ.get('RENDER'):
    DB_PATH = "/tmp/leaderboard.db"
    print("⚡ Running on RENDER - using /tmp/leaderboard.db")
else:
    DB_PATH = "leaderboard.db"
    print("💻 Running LOCALLY - using local leaderboard.db")

def init_db():
    """Initialize database - storing emails but not showing them in table"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create main scores table (stores email but won't display it)
    c.execute("""
        CREATE TABLE IF NOT EXISTS main_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,  -- Stored but not displayed
            time_s REAL NOT NULL,
            outcome TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    
    # Create test scores table (no email)
    c.execute("""
        CREATE TABLE IF NOT EXISTS test_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            time_s REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {DB_PATH}")

def add_main_score(name, email, time_s, outcome):
    """Add a main game score"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO main_scores (name, email, time_s, outcome, timestamp) VALUES (?, ?, ?, ?, ?)",
        (name, email, time_s, outcome, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    )
    conn.commit()
    conn.close()

def add_test_score(name, time_s):
    """Add a test score"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO test_scores (name, time_s, timestamp) VALUES (?, ?, ?)",
        (name, time_s, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    )
    conn.commit()
    conn.close()

def get_main_scores():
    """Get all main scores, ordered by time (fastest first) - return without email"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # SELECT name, time_s, outcome, timestamp - skipping email
    c.execute("SELECT name, time_s, outcome, timestamp FROM main_scores ORDER BY time_s ASC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_test_scores():
    """Get all test scores, ordered by time (fastest first)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, time_s, timestamp FROM test_scores ORDER BY time_s ASC")
    rows = c.fetchall()
    conn.close()
    return rows

@app.route("/")
def index():
    # Get scores from both tables
    main_scores = get_main_scores()
    test_scores = get_test_scores()
    
    # HTML template (NO EMAIL COLUMN IN DISPLAY)
    html = """
    <!doctype html>
    <html>
    <head>
        <title>WASK Leaderboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
                color: #e0e0e0;
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            header {
                text-align: center;
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 3px solid #4CAF50;
            }
            
            h1 {
                color: #fff;
                font-size: 2.8em;
                margin-bottom: 10px;
                text-shadow: 0 2px 10px rgba(0,0,0,0.5);
            }
            
            .subtitle {
                color: #aaa;
                font-size: 1.1em;
                margin-bottom: 30px;
            }
            
            .section {
                background: rgba(30, 30, 30, 0.8);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.4);
                border: 1px solid #333;
            }
            
            .section-title {
                color: #4CAF50;
                font-size: 1.8em;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #4CAF50;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            
            th {
                background: #222;
                color: #fff;
                padding: 15px;
                text-align: center;
                font-weight: 600;
                border: 1px solid #444;
            }
            
            td {
                padding: 12px 15px;
                text-align: center;
                border: 1px solid #444;
            }
            
            /* Main table styling */
            .main-table tr:nth-child(even) {
                background: rgba(40, 40, 40, 0.6);
            }
            
            .main-table tr:nth-child(odd) {
                background: rgba(35, 35, 35, 0.6);
            }
            
            /* Test table styling */
            .test-table {
                background: rgba(10, 40, 10, 0.3);
            }
            
            .test-table tr:nth-child(even) {
                background: rgba(20, 50, 20, 0.4);
            }
            
            .test-table tr:nth-child(odd) {
                background: rgba(15, 45, 15, 0.4);
            }
            
            /* Medal styling */
            .gold { 
                background: linear-gradient(135deg, #4d3b00 0%, #8b7500 100%) !important;
                color: #ffd700;
                font-weight: bold;
                position: relative;
            }
            
            .silver { 
                background: linear-gradient(135deg, #3b3f4d 0%, #6a6f88 100%) !important;
                color: #c0c0c0;
                font-weight: bold;
            }
            
            .bronze { 
                background: linear-gradient(135deg, #4d2f21 0%, #8b5a3c 100%) !important;
                color: #cd7f32;
                font-weight: bold;
            }
            
            .medal-icon {
                font-size: 1.3em;
                margin-right: 5px;
            }
            
            .time-cell {
                font-family: 'Courier New', monospace;
                font-size: 1.1em;
                font-weight: bold;
                color: #4CAF50;
            }
            
            .test-name {
                color: #4CAF50;
                font-weight: bold;
            }
            
            .empty-message {
                text-align: center;
                padding: 40px;
                color: #888;
                font-style: italic;
                font-size: 1.1em;
            }
            
            .stats {
                display: flex;
                justify-content: space-around;
                margin-top: 30px;
                padding: 20px;
                background: rgba(0,0,0,0.3);
                border-radius: 10px;
                border: 1px solid #333;
            }
            
            .stat-item {
                text-align: center;
            }
            
            .stat-value {
                font-size: 2em;
                font-weight: bold;
                color: #4CAF50;
            }
            
            .stat-label {
                color: #aaa;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 10px;
                }
                
                table {
                    display: block;
                    overflow-x: auto;
                }
                
                h1 {
                    font-size: 2em;
                }
                
                .stats {
                    flex-direction: column;
                    gap: 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🏆 WASK Leaderboard</h1>
                <div class="subtitle">
                    Real-time game scores and test results | Auto-deployed from GitHub
                </div>
            </header>
            
            <!-- Main Game Scores Section -->
            <div class="section">
                <div class="section-title">
                    🎮 Game Scores
                    <span style="font-size: 0.6em; color: #888; margin-left: auto;">
                        {{ main_scores|length }} players
                    </span>
                </div>
                
                {% if main_scores %}
                <table class="main-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Name</th>
                            <th>Time (seconds)</th>
                            <th>Result</th>
                            <th>Submitted</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for i, row in main_scores %}
                        {% set row_class = "" %}
                        {% if i == 1 %}{% set row_class = "gold" %}{% endif %}
                        {% if i == 2 %}{% set row_class = "silver" %}{% endif %}
                        {% if i == 3 %}{% set row_class = "bronze" %}{% endif %}
                        <tr class="{{ row_class }}">
                            <td>
                                {% if i == 1 %}<span class="medal-icon">🥇</span>{% endif %}
                                {% if i == 2 %}<span class="medal-icon">🥈</span>{% endif %}
                                {% if i == 3 %}<span class="medal-icon">🥉</span>{% endif %}
                                {{ i }}
                            </td>
                            <td>{{ row[0] }}</td>
                            <td class="time-cell">{{ "%.2f" % row[1] }}</td>
                            <td>{{ row[2] }}</td>
                            <td>{{ row[3] }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty-message">
                    No game scores yet. Be the first to play and claim the top spot! 🏁
                </div>
                {% endif %}
            </div>
            
            <!-- Test Scores Section -->
            <div class="section">
                <div class="section-title">
                    🧪 Test Scores
                    <span style="font-size: 0.6em; color: #4CAF50; margin-left: auto;">
                        {{ test_scores|length }} tests
                    </span>
                </div>
                
                {% if test_scores %}
                <table class="test-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Test Player</th>
                            <th>Time (seconds)</th>
                            <th>Submitted</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for i, row in test_scores %}
                        <tr>
                            <td>{{ i }}</td>
                            <td class="test-name">{{ row[0] }}</td>
                            <td class="time-cell">{{ "%.2f" % row[1] }}</td>
                            <td>{{ row[2] }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty-message">
                    No test scores yet. Run <code>test_leaderboard.py</code> to add test data! 🚀
                </div>
                {% endif %}
            </div>
            
            <!-- Stats Section -->
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{{ main_scores|length }}</div>
                    <div class="stat-label">Game Players</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ test_scores|length }}</div>
                    <div class="stat-label">Test Runs</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">
                        {% if main_scores %}{{ "%.2f" % main_scores[0][1] }}{% else %}0.00{% endif %}
                    </div>
                    <div class="stat-label">Best Time (s)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">
                        {% if main_scores %}{{ main_scores[-1][1][3].split()[0] }}{% else %}N/A{% endif %}
                    </div>
                    <div class="stat-label">Last Updated</div>
                </div>
            </div>
            
            <footer style="text-align: center; margin-top: 40px; color: #666; font-size: 0.9em;">
                <p>🔧 Game submissions: <code>/submit_result</code> | Test submissions: <code>/submit</code></p>
                <p>📊 API endpoint: <code>/leaderboard</code> | Health check: <code>/health</code></p>
                <p>🔄 Auto-deployed from GitHub | Running on Render.com</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    # Prepare data for template
    indexed_main_scores = list(enumerate(main_scores, start=1))
    indexed_test_scores = list(enumerate(test_scores, start=1))
    
    return render_template_string(
        html, 
        main_scores=indexed_main_scores, 
        test_scores=indexed_test_scores
    )

@app.route("/leaderboard")
def api_leaderboard():
    """API endpoint for main scores (JSON format) - includes email in API"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, email, time_s, outcome, timestamp FROM main_scores ORDER BY time_s ASC")
    rows = c.fetchall()
    conn.close()
    
    data = [
        {
            "rank": idx + 1,
            "name": row[0],
            "email": row[1],  # Email included in API but not displayed in HTML
            "time_s": row[2],
            "outcome": row[3],
            "timestamp": row[4]
        }
        for idx, row in enumerate(rows)
    ]
    return jsonify(data)

@app.route("/submit_result", methods=["POST"])
def submit_result():
    """Endpoint for real game submissions"""
    try:
        data = request.get_json(force=True)
        name = (data.get("name") or "Player").strip()
        email = (data.get("email") or "").strip()
        time_s = float(data.get("time_s", 0.0))
        outcome = (data.get("outcome") or "unknown").strip()

        add_main_score(name, email, time_s, outcome)

        return jsonify({
            "status": "success",
            "message": "Score added to main leaderboard",
            "data": {
                "name": name,
                "time_s": time_s,
                "outcome": outcome
                # Email not returned in response
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return "OK", 200

@app.route('/submit', methods=['POST'])
def submit():
    """Endpoint for test_leaderboard.py submissions"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        name = data.get('name', 'TestPlayer').strip()
        time_s = float(data.get('time_s', 0.0))
        
        add_test_score(name, time_s)
        
        return jsonify({
            'status': 'success',
            'message': f'Test score added for {name}',
            'score': time_s
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)