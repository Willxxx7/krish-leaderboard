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
    """Get scores by type ('game' or 'test')"""
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
        return rows
    except Exception as e:
        print(f"❌ Error getting scores: {e}")
        print(traceback.format_exc())
        return []

@app.route("/")
def index():
    """Main page with game and test scores - SIMPLIFIED VERSION"""
    try:
        # Initialize database if needed
        init_db()
        
        # Get scores
        game_scores = get_scores_by_type('game')
        test_scores = get_scores_by_type('test')
        
        # Create indexed lists WITHOUT enumerate
        indexed_game_scores = []
        for i, row in enumerate(game_scores, 1):
            try:
                time_float = float(row[1])
                indexed_game_scores.append({
                    'rank': i,
                    'name': row[0],
                    'time': time_float,
                    'outcome': row[2],
                    'timestamp': row[3]
                })
            except:
                indexed_game_scores.append({
                    'rank': i,
                    'name': row[0],
                    'time': 0.0,
                    'outcome': row[2],
                    'timestamp': row[3]
                })
        
        indexed_test_scores = []
        for i, row in enumerate(test_scores, 1):
            try:
                time_float = float(row[1])
                indexed_test_scores.append({
                    'rank': i,
                    'name': row[0],
                    'time': time_float,
                    'timestamp': row[2]
                })
            except:
                indexed_test_scores.append({
                    'rank': i,
                    'name': row[0],
                    'time': 0.0,
                    'timestamp': row[2]
                })
        
        # Calculate best time safely
        if indexed_game_scores:
            best_time = f"{indexed_game_scores[0]['time']:.2f}"
        else:
            best_time = "0.00"
        
        # SIMPLE HTML TEMPLATE WITHOUT COMPLEX JINJA2 FORMATTING
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>WASK Leaderboard</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #111;
                    color: #eee;
                    margin: 0;
                    padding: 20px;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                
                h1 {{
                    text-align: center;
                    color: #4CAF50;
                    margin-bottom: 30px;
                }}
                
                .section {{
                    background: #1a1a1a;
                    padding: 20px;
                    margin-bottom: 30px;
                    border-radius: 10px;
                    border: 1px solid #333;
                }}
                
                .section-title {{
                    color: #4CAF50;
                    font-size: 1.5em;
                    margin-bottom: 15px;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }}
                
                th {{
                    background: #222;
                    color: #fff;
                    padding: 12px;
                    text-align: center;
                    border: 1px solid #444;
                }}
                
                td {{
                    padding: 10px;
                    text-align: center;
                    border: 1px solid #444;
                }}
                
                .game-table tr:nth-child(even) {{
                    background: #1f1f1f;
                }}
                
                .game-table tr:nth-child(odd) {{
                    background: #252525;
                }}
                
                .test-table {{
                    background: #0a3d0a;
                }}
                
                .test-table tr:nth-child(even) {{
                    background: #0c5a0c;
                }}
                
                .test-table tr:nth-child(odd) {{
                    background: #084a08;
                }}
                
                /* Medal styling */
                .gold {{
                    background: #4d3b00 !important;
                    color: #ffd700;
                    font-weight: bold;
                }}
                
                .silver {{
                    background: #3b3f4d !important;
                    color: #c0c0c0;
                    font-weight: bold;
                }}
                
                .bronze {{
                    background: #4d2f21 !important;
                    color: #cd7f32;
                    font-weight: bold;
                }}
                
                .time-cell {{
                    font-family: 'Courier New', monospace;
                    font-weight: bold;
                    color: #4CAF50;
                }}
                
                .test-name {{
                    color: #4CAF50;
                    font-weight: bold;
                }}
                
                .empty {{
                    text-align: center;
                    padding: 30px;
                    color: #888;
                    font-style: italic;
                }}
                
                .stats {{
                    display: flex;
                    justify-content: space-around;
                    margin-top: 20px;
                    padding: 15px;
                    background: #222;
                    border-radius: 8px;
                }}
                
                .stat {{
                    text-align: center;
                }}
                
                .stat-value {{
                    font-size: 1.5em;
                    color: #4CAF50;
                    font-weight: bold;
                }}
                
                .stat-label {{
                    color: #aaa;
                    font-size: 0.9em;
                }}
                
                footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏆 WASK Leaderboard</h1>
                
                <!-- Game Scores -->
                <div class="section">
                    <div class="section-title">🎮 Game Scores ({len(indexed_game_scores)} players)</div>
        """
        
        if indexed_game_scores:
            html += """
                    <table class="game-table">
                        <tr>
                            <th>Rank</th>
                            <th>Player</th>
                            <th>Time (s)</th>
                            <th>Result</th>
                            <th>Submitted</th>
                        </tr>
            """
            
            for i, score in enumerate(indexed_game_scores, 1):
                medal_class = ""
                medal_icon = ""
                if i == 1:
                    medal_class = "gold"
                    medal_icon = "🥇 "
                elif i == 2:
                    medal_class = "silver"
                    medal_icon = "🥈 "
                elif i == 3:
                    medal_class = "bronze"
                    medal_icon = "🥉 "
                
                html += f"""
                        <tr class="{medal_class}">
                            <td>{medal_icon}{score['rank']}</td>
                            <td>{score['name']}</td>
                            <td class="time-cell">{score['time']:.2f}</td>
                            <td>{score['outcome']}</td>
                            <td>{score['timestamp']}</td>
                        </tr>
                """
            
            html += """
                    </table>
            """
        else:
            html += """
                    <div class="empty">No game scores yet. Be the first to play!</div>
            """
        
        html += f"""
                </div>
                
                <!-- Test Scores -->
                <div class="section">
                    <div class="section-title">🧪 Test Scores ({len(indexed_test_scores)} tests)</div>
        """
        
        if indexed_test_scores:
            html += """
                    <table class="test-table">
                        <tr>
                            <th>#</th>
                            <th>Test Player</th>
                            <th>Time (s)</th>
                            <th>Submitted</th>
                        </tr>
            """
            
            for score in indexed_test_scores:
                html += f"""
                        <tr>
                            <td>{score['rank']}</td>
                            <td class="test-name">{score['name']}</td>
                            <td class="time-cell">{score['time']:.2f}</td>
                            <td>{score['timestamp']}</td>
                        </tr>
                """
            
            html += """
                    </table>
            """
        else:
            html += """
                    <div class="empty">No test scores yet. Run test_leaderboard.py!</div>
            """
        
        html += f"""
                </div>
                
                <!-- Stats -->
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{len(indexed_game_scores)}</div>
                        <div class="stat-label">Game Players</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{len(indexed_test_scores)}</div>
                        <div class="stat-label">Test Scores</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{best_time}</div>
                        <div class="stat-label">Best Time</div>
                    </div>
                </div>
                
                <footer>
                    <p>Running on Render.com | Database: {DB_PATH}</p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        print(f"❌ Error in index: {e}")
        print(traceback.format_exc())
        return f"""
        <html>
        <body style="background: #111; color: #eee; padding: 40px; font-family: monospace;">
            <h1>⚠️ Server Error</h1>
            <p><strong>Error:</strong> {str(e)}</p>
            <p><strong>Full traceback:</strong></p>
            <pre>{traceback.format_exc()}</pre>
            <p>Database path: {DB_PATH}</p>
            <p>Try refreshing the page.</p>
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
                "time_s": float(row[1]),
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
        
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "tables": [t[0] for t in tables],
            "score_count": count,
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
    port = int(os.environ.get("PORT", 5001))
    print(f"🌐 Server starting on port {port}")
    print(f"🔗 Local: http://localhost:{port}")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=False)