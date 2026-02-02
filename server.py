from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import sqlite3
import os
import traceback

app = Flask(__name__)

# Database configuration for Render.com
if os.environ.get('RENDER'):
    DB_PATH = "/tmp/leaderboard.db"
    print("⚡ RENDER ENVIRONMENT DETECTED")
    print(f"⚡ Database: {DB_PATH}")
else:
    DB_PATH = "leaderboard.db"
    print(f"💻 LOCAL DEVELOPMENT")
    print(f"💻 Database: {DB_PATH}")

def init_db():
    """Initialize database - guaranteed to create table"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Create the scores table if it doesn't exist
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
        
        conn.commit()
        conn.close()
        
        # Verify table was created
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        conn.close()
        
        print(f"✅ Database initialized: {DB_PATH}")
        print(f"✅ Tables found: {tables}")
        
        return True
    except Exception as e:
        print(f"❌ Database initialization FAILED: {e}")
        print(traceback.format_exc())
        return False

def add_score(name, email, time_s, outcome, score_type='game'):
    """Add a score to the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Ensure time_s is float
        try:
            time_s_float = float(time_s)
        except:
            time_s_float = 0.0
        
        c.execute("""
            INSERT INTO scores (name, email, time_s, outcome, score_type, timestamp) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, time_s_float, outcome, score_type, timestamp))
        
        conn.commit()
        conn.close()
        print(f"✅ Score added: {name} - {time_s_float}s - {score_type}")
        return True
    except Exception as e:
        print(f"❌ Error adding score: {e}")
        print(traceback.format_exc())
        return False

def get_scores_by_type(score_type):
    """Get scores by type ('game' or 'test') - returns float for time_s"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        if score_type == 'game':
            c.execute("""
                SELECT name, time_s, outcome, timestamp 
                FROM scores 
                WHERE score_type = 'game' 
                ORDER BY time_s ASC
            """)
        else:
            c.execute("""
                SELECT name, time_s, timestamp 
                FROM scores 
                WHERE score_type = 'test' 
                ORDER BY time_s ASC
            """)
        
        rows = c.fetchall()
        conn.close()
        
        # Convert time_s to float to ensure it's numeric
        converted_rows = []
        for row in rows:
            if score_type == 'game':
                try:
                    time_float = float(row[1])
                    converted_rows.append((row[0], time_float, row[2], row[3]))
                except:
                    converted_rows.append((row[0], 0.0, row[2], row[3]))
            else:
                try:
                    time_float = float(row[1])
                    converted_rows.append((row[0], time_float, row[2]))
                except:
                    converted_rows.append((row[0], 0.0, row[2]))
        
        return converted_rows
    except Exception as e:
        print(f"❌ Error getting scores: {e}")
        print(traceback.format_exc())
        return []

@app.route("/")
def index():
    """Main page with game and test scores"""
    try:
        # Initialize database if needed
        init_db()
        
        # Get scores (time_s will be float)
        game_scores = get_scores_by_type('game')
        test_scores = get_scores_by_type('test')
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>WASK Leaderboard</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #111;
                    color: #eee;
                    margin: 0;
                    padding: 20px;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                
                h1 {
                    text-align: center;
                    color: #4CAF50;
                    margin-bottom: 30px;
                }
                
                .section {
                    background: #1a1a1a;
                    padding: 20px;
                    margin-bottom: 30px;
                    border-radius: 10px;
                    border: 1px solid #333;
                }
                
                .section-title {
                    color: #4CAF50;
                    font-size: 1.5em;
                    margin-bottom: 15px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .section-count {
                    font-size: 0.8em;
                    color: #888;
                }
                
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }
                
                th {
                    background: #222;
                    color: #fff;
                    padding: 12px;
                    text-align: center;
                    border: 1px solid #444;
                }
                
                td {
                    padding: 10px;
                    text-align: center;
                    border: 1px solid #444;
                }
                
                .game-table tr:nth-child(even) {
                    background: #1f1f1f;
                }
                
                .game-table tr:nth-child(odd) {
                    background: #252525;
                }
                
                .test-table {
                    background: #0a3d0a;
                }
                
                .test-table tr:nth-child(even) {
                    background: #0c5a0c;
                }
                
                .test-table tr:nth-child(odd) {
                    background: #084a08;
                }
                
                /* Medal styling */
                .gold {
                    background: #4d3b00 !important;
                    color: #ffd700;
                    font-weight: bold;
                }
                
                .silver {
                    background: #3b3f4d !important;
                    color: #c0c0c0;
                    font-weight: bold;
                }
                
                .bronze {
                    background: #4d2f21 !important;
                    color: #cd7f32;
                    font-weight: bold;
                }
                
                .medal-icon {
                    font-size: 1.2em;
                    margin-right: 5px;
                }
                
                .time-cell {
                    font-family: 'Courier New', monospace;
                    font-weight: bold;
                    color: #4CAF50;
                }
                
                .test-name {
                    color: #4CAF50;
                    font-weight: bold;
                }
                
                .empty-message {
                    text-align: center;
                    padding: 30px;
                    color: #888;
                    font-style: italic;
                    font-size: 1.1em;
                }
                
                .stats {
                    display: flex;
                    justify-content: space-around;
                    margin-top: 30px;
                    padding: 20px;
                    background: #222;
                    border-radius: 10px;
                }
                
                .stat-item {
                    text-align: center;
                }
                
                .stat-value {
                    font-size: 1.8em;
                    font-weight: bold;
                    color: #4CAF50;
                    margin-bottom: 5px;
                }
                
                .stat-label {
                    color: #aaa;
                    font-size: 0.9em;
                    text-transform: uppercase;
                }
                
                footer {
                    text-align: center;
                    margin-top: 40px;
                    color: #666;
                    font-size: 0.9em;
                    padding-top: 20px;
                    border-top: 1px solid #333;
                }
                
                @media (max-width: 768px) {
                    .container {
                        padding: 10px;
                    }
                    
                    table {
                        font-size: 0.9em;
                    }
                    
                    th, td {
                        padding: 8px;
                    }
                    
                    .section {
                        padding: 15px;
                    }
                    
                    .stats {
                        flex-direction: column;
                        gap: 15px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏆 WASK Leaderboard</h1>
                
                <!-- Game Scores -->
                <div class="section">
                    <div class="section-title">
                        <span>🎮 Game Scores</span>
                        <span class="section-count">{{ game_count }} players</span>
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
                                {% if i == 1 %}<span class="medal-icon">🥇</span>{% endif %}
                                {% if i == 2 %}<span class="medal-icon">🥈</span>{% endif %}
                                {% if i == 3 %}<span class="medal-icon">🥉</span>{% endif %}
                                {{ i }}
                            </td>
                            <td>{{ row[0] }}</td>
                            <td class="time-cell">{{ "%.2f"|format(row[1]) }}</td>
                            <td>{{ row[2] }}</td>
                            <td>{{ row[3] }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% else %}
                    <div class="empty-message">
                        🏁 No game scores yet. Be the first to play!
                    </div>
                    {% endif %}
                </div>
                
                <!-- Test Scores -->
                <div class="section">
                    <div class="section-title">
                        <span>🧪 Test Scores</span>
                        <span class="section-count" style="color: #4CAF50;">{{ test_count }} tests</span>
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
                            <td class="time-cell">{{ "%.2f"|format(row[1]) }}</td>
                            <td>{{ row[2] }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% else %}
                    <div class="empty-message">
                        🚀 No test scores yet. Run <code>test_leaderboard.py</code> to add test data!
                    </div>
                    {% endif %}
                </div>
                
                <!-- Stats -->
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-value">{{ game_count }}</div>
                        <div class="stat-label">Game Players</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{{ test_count }}</div>
                        <div class="stat-label">Test Scores</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">
                            {% if game_scores %}{{ "%.2f"|format(game_scores[0][1]) }}{% else %}0.00{% endif %}
                        </div>
                        <div class="stat-label">Best Time (s)</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">
                            {% if game_scores or test_scores %}🟢 Active{% else %}⚪ Ready{% endif %}
                        </div>
                        <div class="stat-label">Status</div>
                    </div>
                </div>
                
                <footer>
                    <p>🔧 <strong>Endpoints:</strong> 
                       <code>/submit_result</code> (game scores) | 
                       <code>/submit</code> (test scores)
                    </p>
                    <p>📊 <strong>API:</strong> <code>/leaderboard</code> | 
                       <strong>Health:</strong> <code>/health</code></p>
                    <p>🚀 <strong>Deployed on Render.com</strong> | Database: {{ db_path }}</p>
                </footer>
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
            game_count=len(game_scores),
            test_count=len(test_scores),
            db_path=DB_PATH
        )
        
    except Exception as e:
        print(f"❌ Error in index: {e}")
        print(traceback.format_exc())
        return f"""
        <html>
        <body style="background: #111; color: #eee; padding: 40px; font-family: monospace;">
            <h1>⚠️ Server Error</h1>
            <p><strong>Error:</strong> {str(e)}</p>
            <p><strong>Database path:</strong> {DB_PATH}</p>
            <p><strong>Game scores count:</strong> {len(game_scores) if 'game_scores' in locals() else 'N/A'}</p>
            <p><strong>Test scores count:</strong> {len(test_scores) if 'test_scores' in locals() else 'N/A'}</p>
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
        print(f"❌ API error: {e}")
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
        time_s = data.get('time_s', 0.0)
        outcome = data.get('outcome', 'unknown').strip()
        
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
    """Health check endpoint"""
    try:
        # Initialize database
        init_db()
        
        # Check database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Check if table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        
        # Check if scores table has data
        c.execute("SELECT COUNT(*) FROM scores")
        count = c.fetchone()[0]
        
        # Get score stats
        c.execute("SELECT COUNT(*) FROM scores WHERE score_type = 'game'")
        game_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM scores WHERE score_type = 'test'")
        test_count = c.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "tables": [t[0] for t in tables],
            "total_scores": count,
            "game_scores": game_count,
            "test_scores": test_count,
            "path": DB_PATH
        })
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/submit', methods=['POST'])
def submit():
    """Endpoint for test scores"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data"}), 400
            
        name = data.get('name', 'TestPlayer').strip()
        time_s = data.get('time_s', 0.0)
        
        success = add_score(name, '', time_s, 'test', 'test')
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Test score added for {name}",
                "score": time_s
            })
        else:
            return jsonify({"error": "Failed to add test score"}), 500
            
    except Exception as e:
        print(f"❌ Submit test error: {e}")
        return jsonify({"error": str(e)}), 400

# Initialize database when app starts
print("=" * 60)
print("🚀 Starting WASK Leaderboard Server")
print("=" * 60)

# Initialize database
if init_db():
    print("✅ Database initialized successfully")
else:
    print("⚠️ Database had issues, will retry on first request")

if __name__ == "__main__":
    # Get port from environment (Render sets PORT=10000)
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Server starting on port {port}")
    print(f"🔗 Local: http://localhost:{port}")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=False)