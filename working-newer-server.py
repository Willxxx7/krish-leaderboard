from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import sqlite3
import os
import traceback

app = Flask(__name__)

# Database path for Render
if os.environ.get('RENDER'):
    DB_PATH = "/tmp/leaderboard.db"
else:
    DB_PATH = "leaderboard.db"

def init_db():
    """Initialize database with a single table for all scores"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Drop old tables if they exist (clean start)
        c.execute("DROP TABLE IF EXISTS scores")
        c.execute("DROP TABLE IF EXISTS main_scores")
        c.execute("DROP TABLE IF EXISTS test_scores")
        
        # Create a single table for ALL scores with a 'type' column
        c.execute("""
            CREATE TABLE scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                time_s REAL NOT NULL,
                outcome TEXT NOT NULL,
                score_type TEXT NOT NULL DEFAULT 'game',  -- 'game' or 'test'
                timestamp TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized: {DB_PATH}")
        return True
    except Exception as e:
        print(f"❌ Database init error: {e}")
        print(traceback.format_exc())
        return False

def add_score(name, email, time_s, outcome, score_type='game'):
    """Add a score to the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        c.execute("""
            INSERT INTO scores (name, email, time_s, outcome, score_type, timestamp) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, time_s, outcome, score_type, timestamp))
        
        conn.commit()
        conn.close()
        print(f"✅ Added score: {name} - {time_s}s - {score_type}")
        return True
    except Exception as e:
        print(f"❌ Error adding score: {e}")
        return False

def get_scores_by_type(score_type):
    """Get scores by type ('game' or 'test')"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        if score_type == 'game':
            # For game scores: name, time_s, outcome, timestamp
            c.execute("""
                SELECT name, time_s, outcome, timestamp 
                FROM scores 
                WHERE score_type = 'game' 
                ORDER BY time_s ASC
            """)
        else:
            # For test scores: name, time_s, timestamp
            c.execute("""
                SELECT name, time_s, timestamp 
                FROM scores 
                WHERE score_type = 'test' 
                ORDER BY time_s ASC
            """)
        
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"❌ Error getting scores: {e}")
        return []

@app.route("/")
def index():
    """Main page with game and test scores"""
    try:
        # Get game scores (without email)
        game_scores = get_scores_by_type('game')
        
        # Get test scores
        test_scores = get_scores_by_type('test')
        
        # Simple HTML template
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>WASK Leaderboard</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: #0f172a;
                    color: #e2e8f0;
                    line-height: 1.6;
                    padding: 20px;
                    min-height: 100vh;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                
                header {
                    text-align: center;
                    margin-bottom: 40px;
                    padding: 30px 20px;
                    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                    border-radius: 15px;
                    border: 1px solid #334155;
                }
                
                h1 {
                    font-size: 2.8em;
                    margin-bottom: 10px;
                    background: linear-gradient(90deg, #38bdf8, #818cf8);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                
                .subtitle {
                    color: #94a3b8;
                    font-size: 1.1em;
                }
                
                .section {
                    background: #1e293b;
                    border-radius: 12px;
                    padding: 25px;
                    margin-bottom: 30px;
                    border: 1px solid #334155;
                }
                
                .section-title {
                    color: #38bdf8;
                    font-size: 1.5em;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #38bdf8;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                
                th {
                    background: #0f172a;
                    color: #cbd5e1;
                    padding: 15px;
                    text-align: center;
                    font-weight: 600;
                    border: 1px solid #475569;
                }
                
                td {
                    padding: 14px;
                    text-align: center;
                    border: 1px solid #475569;
                }
                
                /* Main table styling */
                .game-table tr:nth-child(even) {
                    background: rgba(30, 41, 59, 0.6);
                }
                
                .game-table tr:nth-child(odd) {
                    background: rgba(15, 23, 42, 0.6);
                }
                
                /* Test table styling */
                .test-table {
                    background: rgba(6, 78, 59, 0.2);
                }
                
                .test-table tr:nth-child(even) {
                    background: rgba(6, 95, 70, 0.3);
                }
                
                .test-table tr:nth-child(odd) {
                    background: rgba(5, 85, 65, 0.3);
                }
                
                .test-table th, .test-table td {
                    border-color: #047857;
                }
                
                /* Medal rows */
                .gold {
                    background: linear-gradient(135deg, #78350f 0%, #d97706 100%) !important;
                    color: #fbbf24;
                    font-weight: bold;
                }
                
                .silver {
                    background: linear-gradient(135deg, #374151 0%, #6b7280 100%) !important;
                    color: #d1d5db;
                    font-weight: bold;
                }
                
                .bronze {
                    background: linear-gradient(135deg, #7c2d12 0%, #92400e 100%) !important;
                    color: #f97316;
                    font-weight: bold;
                }
                
                .medal {
                    font-size: 1.2em;
                    margin-right: 8px;
                }
                
                .time {
                    font-family: 'Courier New', monospace;
                    font-weight: bold;
                    color: #22c55e;
                }
                
                .test-name {
                    color: #22c55e;
                    font-weight: bold;
                }
                
                .empty {
                    text-align: center;
                    padding: 40px;
                    color: #64748b;
                    font-style: italic;
                }
                
                .stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-top: 30px;
                }
                
                .stat-card {
                    background: #1e293b;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    border: 1px solid #334155;
                }
                
                .stat-value {
                    font-size: 2em;
                    font-weight: bold;
                    color: #38bdf8;
                }
                
                .stat-label {
                    color: #94a3b8;
                    font-size: 0.9em;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                
                footer {
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #334155;
                    color: #64748b;
                    font-size: 0.9em;
                }
                
                @media (max-width: 768px) {
                    .container {
                        padding: 10px;
                    }
                    
                    table {
                        font-size: 0.9em;
                    }
                    
                    th, td {
                        padding: 10px;
                    }
                    
                    .section {
                        padding: 15px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>🏆 WASK Leaderboard</h1>
                    <div class="subtitle">Game Scores & Test Results | Render.com</div>
                </header>
                
                <!-- Game Scores -->
                <div class="section">
                    <div class="section-title">
                        🎮 Game Scores
                        <span style="font-size: 0.7em; color: #94a3b8; margin-left: auto;">
                            {{ game_count }} players
                        </span>
                    </div>
                    
                    {% if game_scores %}
                    <table class="game-table">
                        <tr>
                            <th>Rank</th>
                            <th>Player</th>
                            <th>Time (s)</th>
                            <th>Result</th>
                            <th>Submitted</th>
                        </tr>
                        {% for i, row in game_scores %}
                        <tr class="{% if i == 1 %}gold{% elif i == 2 %}silver{% elif i == 3 %}bronze{% endif %}">
                            <td>
                                {% if i == 1 %}🥇{% elif i == 2 %}🥈{% elif i == 3 %}🥉{% endif %}
                                {{ i }}
                            </td>
                            <td>{{ row[0] }}</td>
                            <td class="time">{{ "%.2f" % row[1] }}</td>
                            <td>{{ row[2] }}</td>
                            <td>{{ row[3] }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% else %}
                    <div class="empty">No game scores yet. Be the first to play! 🚀</div>
                    {% endif %}
                </div>
                
                <!-- Test Scores -->
                <div class="section">
                    <div class="section-title">
                        🧪 Test Scores
                        <span style="font-size: 0.7em; color: #22c55e; margin-left: auto;">
                            {{ test_count }} tests
                        </span>
                    </div>
                    
                    {% if test_scores %}
                    <table class="test-table">
                        <tr>
                            <th>#</th>
                            <th>Test Player</th>
                            <th>Time (s)</th>
                            <th>Submitted</th>
                        </tr>
                        {% for i, row in test_scores %}
                        <tr>
                            <td>{{ i }}</td>
                            <td class="test-name">{{ row[0] }}</td>
                            <td class="time">{{ "%.2f" % row[1] }}</td>
                            <td>{{ row[2] }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% else %}
                    <div class="empty">No test scores yet. Run test_leaderboard.py! 🔧</div>
                    {% endif %}
                </div>
                
                <!-- Stats -->
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">{{ game_count }}</div>
                        <div class="stat-label">Game Players</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{{ test_count }}</div>
                        <div class="stat-label">Test Scores</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">
                            {% if game_scores %}{{ "%.2f" % game_scores[0][1] }}{% else %}0.00{% endif %}
                        </div>
                        <div class="stat-label">Best Time</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">
                            {% if game_scores or test_scores %}Active{% else %}Ready{% endif %}
                        </div>
                        <div class="stat-label">Status</div>
                    </div>
                </div>
                
                <footer>
                    <p>🔧 Game scores: POST /submit_result | Test scores: POST /submit</p>
                    <p>📊 API: GET /leaderboard | Health: GET /health</p>
                    <p>🚀 Deployed on Render.com | Database: {{ db_path }}</p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        # Prepare data for template
        indexed_game_scores = list(enumerate(game_scores, start=1))
        indexed_test_scores = list(enumerate(test_scores, start=1))
        
        return render_template_string(
            html, 
            game_scores=indexed_game_scores,
            test_scores=indexed_test_scores,
            game_count=len(game_scores),
            test_count=len(test_scores),
            db_path=DB_PATH
        )
        
    except Exception as e:
        print(f"❌ Error in index: {e}")
        return f"""
        <html>
        <body style="background: #0f172a; color: #e2e8f0; padding: 40px; font-family: monospace;">
            <h1>Error Loading Page</h1>
            <p><strong>Error:</strong> {str(e)}</p>
            <p><strong>Database:</strong> {DB_PATH}</p>
            <p>Try refreshing the page or checking Render logs.</p>
        </body>
        </html>
        """, 500

@app.route("/leaderboard")
def api_leaderboard():
    """API endpoint for game scores"""
    try:
        scores = get_scores_by_type('game')
        data = [
            {
                "rank": i+1,
                "name": row[0],
                "time_s": row[1],
                "outcome": row[2],
                "timestamp": row[3]
            }
            for i, row in enumerate(scores)
        ]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/submit_result", methods=["POST"])
def submit_result():
    """Endpoint for game scores"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data"}), 400
            
        name = data.get('name', 'Player').strip()
        email = data.get('email', '').strip()
        time_s = float(data.get('time_s', 0.0))
        outcome = data.get('outcome', 'unknown').strip()
        
        add_score(name, email, time_s, outcome, 'game')
        
        return jsonify({
            "status": "success",
            "message": "Game score added",
            "data": {
                "name": name,
                "time_s": time_s,
                "outcome": outcome
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/submit', methods=['POST'])
def submit():
    """Endpoint for test scores"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data"}), 400
            
        name = data.get('name', 'TestPlayer').strip()
        time_s = float(data.get('time_s', 0.0))
        
        add_score(name, '', time_s, 'test', 'test')
        
        return jsonify({
            "status": "success",
            "message": f"Test score added for {name}",
            "score": time_s
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "tables": [t[0] for t in tables],
            "path": DB_PATH
        })
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

# Initialize database on startup
print("=" * 60)
print("🚀 Starting WASK Leaderboard Server")
print("=" * 60)

if __name__ == "__main__":
    # Initialize database
    if init_db():
        print("✅ Database initialized successfully")
    else:
        print("⚠️ Database initialization had issues")
    
    # Get port from environment
    port = int(os.environ.get("PORT", 5000))
    
    print(f"🌐 Server starting on port {port}")
    print(f"🔗 Local: http://localhost:{port}")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=False)