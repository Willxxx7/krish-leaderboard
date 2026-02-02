from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import sqlite3
import os
import traceback

app = Flask(__name__)

# Debug mode for troubleshooting
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Database configuration for Render.com
if os.environ.get('RENDER'):
    # Render.com requires /tmp for writable files
    DB_PATH = "/tmp/leaderboard.db"
    print(f"🔧 RENDER ENVIRONMENT DETECTED")
    print(f"🔧 Using database at: {DB_PATH}")
    print(f"🔧 PORT environment variable: {os.environ.get('PORT')}")
else:
    # Local development
    DB_PATH = "leaderboard.db"
    print(f"💻 LOCAL DEVELOPMENT")
    print(f"💻 Using database at: {DB_PATH}")

def init_db():
    """Initialize the database with proper error handling"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Create scores table (stores all scores with type column)
        c.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                time_s REAL NOT NULL,
                outcome TEXT NOT NULL,
                score_type TEXT DEFAULT 'game',  -- 'game' or 'test'
                timestamp TEXT NOT NULL
            )
        """)
        
        # Create index for faster queries
        c.execute("CREATE INDEX IF NOT EXISTS idx_score_type ON scores(score_type)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_time ON scores(time_s)")
        
        conn.commit()
        conn.close()
        
        print(f"✅ Database initialized successfully at: {DB_PATH}")
        print(f"✅ Database file exists: {os.path.exists(DB_PATH)}")
        
        # Test database connection
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        conn.close()
        print(f"✅ Tables in database: {tables}")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print(traceback.format_exc())
        raise

def add_score(name, email, time_s, outcome, score_type='game'):
    """Add a score to the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            """INSERT INTO scores (name, email, time_s, outcome, score_type, timestamp) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, email, time_s, outcome, score_type, 
             datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error adding score: {e}")
        return False

def get_scores(score_type=None):
    """Get scores, optionally filtered by type"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        if score_type:
            c.execute("""
                SELECT name, time_s, outcome, timestamp 
                FROM scores 
                WHERE score_type = ? 
                ORDER BY time_s ASC
            """, (score_type,))
        else:
            c.execute("""
                SELECT name, time_s, outcome, timestamp 
                FROM scores 
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
    """Main page with both game and test scores"""
    try:
        # Get game scores (type='game')
        game_scores = get_scores('game')
        
        # Get test scores (type='test')
        test_scores = get_scores('test')
        
        html = """
        <!doctype html>
        <html>
        <head>
            <title>WASK Leaderboard</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                    background: #0f172a;
                    color: #e2e8f0;
                    margin: 0;
                    padding: 20px;
                    line-height: 1.6;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                header {
                    text-align: center;
                    margin-bottom: 40px;
                    padding: 20px;
                    background: rgba(30, 41, 59, 0.7);
                    border-radius: 15px;
                    border: 1px solid #334155;
                }
                
                h1 {
                    color: #38bdf8;
                    font-size: 2.5em;
                    margin: 0 0 10px 0;
                    background: linear-gradient(90deg, #38bdf8, #818cf8);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                
                .subtitle {
                    color: #94a3b8;
                    font-size: 1.1em;
                }
                
                .section {
                    background: rgba(30, 41, 59, 0.7);
                    border-radius: 15px;
                    padding: 25px;
                    margin-bottom: 30px;
                    border: 1px solid #334155;
                }
                
                .section-title {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    color: #38bdf8;
                    font-size: 1.5em;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #38bdf8;
                }
                
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    font-size: 0.95em;
                }
                
                th {
                    background: #1e293b;
                    color: #cbd5e1;
                    padding: 15px;
                    text-align: center;
                    font-weight: 600;
                    border: 1px solid #475569;
                }
                
                td {
                    padding: 12px 15px;
                    text-align: center;
                    border: 1px solid #475569;
                }
                
                .game-table tr:nth-child(even) {
                    background: rgba(51, 65, 85, 0.3);
                }
                
                .game-table tr:nth-child(odd) {
                    background: rgba(30, 41, 59, 0.5);
                }
                
                .test-table {
                    background: rgba(6, 78, 59, 0.2);
                }
                
                .test-table tr:nth-child(even) {
                    background: rgba(6, 95, 70, 0.3);
                }
                
                .test-table tr:nth-child(odd) {
                    background: rgba(5, 85, 65, 0.3);
                }
                
                .test-table td, .test-table th {
                    border-color: #047857;
                }
                
                /* Medal styling */
                .gold-row {
                    background: linear-gradient(135deg, #78350f 0%, #d97706 100%) !important;
                    color: #fbbf24;
                    font-weight: bold;
                }
                
                .silver-row {
                    background: linear-gradient(135deg, #374151 0%, #6b7280 100%) !important;
                    color: #d1d5db;
                    font-weight: bold;
                }
                
                .bronze-row {
                    background: linear-gradient(135deg, #7c2d12 0%, #92400e 100%) !important;
                    color: #f97316;
                    font-weight: bold;
                }
                
                .medal-icon {
                    font-size: 1.2em;
                    margin-right: 8px;
                }
                
                .time-cell {
                    font-family: 'Courier New', monospace;
                    font-size: 1.1em;
                    font-weight: bold;
                    color: #22c55e;
                }
                
                .test-name {
                    color: #22c55e;
                    font-weight: bold;
                }
                
                .empty-message {
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
                    background: rgba(30, 41, 59, 0.7);
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    border: 1px solid #334155;
                }
                
                .stat-value {
                    font-size: 2em;
                    font-weight: bold;
                    color: #38bdf8;
                    margin-bottom: 5px;
                }
                
                .stat-label {
                    color: #94a3b8;
                    font-size: 0.9em;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                
                .footer {
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #334155;
                    color: #64748b;
                    font-size: 0.9em;
                }
                
                .badge {
                    display: inline-block;
                    padding: 4px 8px;
                    background: #0f766e;
                    color: white;
                    border-radius: 4px;
                    font-size: 0.8em;
                    margin-left: 8px;
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
                    <div class="subtitle">
                        Real-time game scores | Deployed on Render.com
                    </div>
                </header>
                
                <!-- Game Scores Section -->
                <div class="section">
                    <div class="section-title">
                        🎮 Game Scores
                        <span class="badge">{{ game_scores|length }} players</span>
                    </div>
                    
                    {% if game_scores %}
                    <table class="game-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Player</th>
                                <th>Time (s)</th>
                                <th>Result</th>
                                <th>Submitted</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for i, row in game_scores %}
                            {% set row_class = "" %}
                            {% if i == 1 %}{% set row_class = "gold-row" %}{% endif %}
                            {% if i == 2 %}{% set row_class = "silver-row" %}{% endif %}
                            {% if i == 3 %}{% set row_class = "bronze-row" %}{% endif %}
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
                        No game scores yet. Be the first to play! 🚀
                    </div>
                    {% endif %}
                </div>
                
                <!-- Test Scores Section -->
                <div class="section">
                    <div class="section-title">
                        🧪 Test Scores
                        <span class="badge" style="background: #047857;">{{ test_scores|length }} tests</span>
                    </div>
                    
                    {% if test_scores %}
                    <table class="test-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Test Player</th>
                                <th>Time (s)</th>
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
                        No test scores yet. Run <code>test_leaderboard.py</code> to add test data!
                    </div>
                    {% endif %}
                </div>
                
                <!-- Stats Section -->
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">{{ game_scores|length }}</div>
                        <div class="stat-label">Game Players</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{{ test_scores|length }}</div>
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
                            {% if game_scores or test_scores %}Active{% else %}Idle{% endif %}
                        </div>
                        <div class="stat-label">Status</div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>🔧 <strong>Endpoints:</strong> 
                       <code>/submit_result</code> (game scores) | 
                       <code>/submit</code> (test scores) |
                       <code>/health</code> (health check)
                    </p>
                    <p>🚀 <strong>Deployment:</strong> Auto-deployed from GitHub | Running on Render.com</p>
                    <p>📊 <strong>Database:</strong> SQLite at {{ db_path }}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        indexed_game_scores = list(enumerate(game_scores, start=1))
        indexed_test_scores = list(enumerate(test_scores, start=1))
        
        return render_template_string(
            html, 
            game_scores=indexed_game_scores, 
            test_scores=indexed_test_scores,
            db_path=DB_PATH
        )
        
    except Exception as e:
        print(f"❌ Error in index route: {e}")
        print(traceback.format_exc())
        return f"""
        <html>
        <body style="background: #0f172a; color: #e2e8f0; padding: 40px; font-family: monospace;">
            <h1>⚠️ Server Error</h1>
            <p>Error: {str(e)}</p>
            <pre>{traceback.format_exc()}</pre>
            <p>Database path: {DB_PATH}</p>
            <p>Database exists: {os.path.exists(DB_PATH)}</p>
        </body>
        </html>
        """, 500

@app.route("/leaderboard")
def api_leaderboard():
    """API endpoint for game scores"""
    try:
        scores = get_scores('game')
        data = [
            {
                "rank": idx + 1,
                "name": row[0],
                "time_s": row[1],
                "outcome": row[2],
                "timestamp": row[3]
            }
            for idx, row in enumerate(scores)
        ]
        return jsonify(data)
    except Exception as e:
        print(f"❌ API error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/submit_result", methods=["POST"])
def submit_result():
    """Endpoint for game submissions"""
    try:
        data = request.get_json(force=True)
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        name = (data.get("name") or "Player").strip()
        email = (data.get("email") or "").strip()
        time_s = float(data.get("time_s", 0.0))
        outcome = (data.get("outcome") or "unknown").strip()

        success = add_score(name, email, time_s, outcome, 'game')
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Game score added",
                "data": {
                    "name": name,
                    "time_s": time_s,
                    "outcome": outcome
                }
            })
        else:
            return jsonify({"error": "Failed to add score"}), 500
            
    except Exception as e:
        print(f"❌ Submit result error: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/health')
def health_check():
    """Health check endpoint with database test"""
    try:
        # Test database connection
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = c.fetchone()[0]
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "tables": table_count,
            "path": DB_PATH,
            "exists": os.path.exists(DB_PATH)
        }), 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "path": DB_PATH,
            "exists": os.path.exists(DB_PATH)
        }), 500

@app.route('/submit', methods=['POST'])
def submit():
    """Endpoint for test submissions"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        name = data.get('name', 'TestPlayer').strip()
        time_s = float(data.get('time_s', 0.0))
        
        success = add_score(name, "", time_s, "test", 'test')
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Test score added for {name}',
                'score': time_s
            })
        else:
            return jsonify({"error": "Failed to add test score"}), 500
            
    except Exception as e:
        print(f"❌ Submit test error: {e}")
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    # Initialize database
    print("🚀 Starting WASK Leaderboard Server")
    print("=" * 50)
    init_db()
    
    # Get port from environment (Render.com sets this)
    port = int(os.environ.get("PORT", 5000))
    
    print(f"🌐 Starting server on port {port}")
    print(f"🔗 Local URL: http://localhost:{port}")
    print(f"🔗 Network URL: http://{os.environ.get('HOST', '0.0.0.0')}:{port}")
    print("=" * 50)
    
    # Run the app
    app.run(
        host='0.0.0.0',  # Bind to all interfaces
        port=port,
        debug=DEBUG
    )