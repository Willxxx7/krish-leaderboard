import requests
import time

def test_endpoint(url, endpoint, data, name):
    """Test a single endpoint"""
    try:
        full_url = f"{url}{endpoint}"
        print(f"   Testing {name}: {full_url}")
        
        response = requests.post(
            full_url,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"      ✅ Success: {response.json()}")
            return True
        else:
            print(f"      ❌ Failed: Status {response.status_code}")
            print(f"      Response: {response.text}")
            return False
    except Exception as e:
        print(f"      ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 WASK Leaderboard Test Script")
    print("=" * 60)
    
    # Your Render URL
    RENDER_URL = "https://krish-leaderboard.onrender.com"
    
    print(f"\n1. Testing RENDER server: {RENDER_URL}")
    print("-" * 40)
    
    # Test health endpoint first
    try:
        health = requests.get(f"{RENDER_URL}/health", timeout=10)
        if health.status_code == 200:
            print("   ✅ Health check: PASSED")
            print(f"      Response: {health.json()}")
        else:
            print(f"   ❌ Health check: FAILED (Status: {health.status_code})")
    except Exception as e:
        print(f"   ❌ Health check: ERROR - {e}")
    
    # Add test scores
    test_scores = [
        {"name": "TestPlayer1", "time_s": 45.23},
        {"name": "TestPlayer2", "time_s": 67.89},
        {"name": "TestPlayer3", "time_s": 89.12},
    ]
    
    for score in test_scores:
        test_endpoint(
            RENDER_URL,
            "/submit",
            score,
            f"Test score: {score['name']}"
        )
        time.sleep(0.5)  # Small delay between requests
    
    # Add a game score
    game_score = {
        "name": "GamePlayer1",
        "email": "player@example.com",
        "time_s": 55.55,
        "outcome": "win"
    }
    
    test_endpoint(
        RENDER_URL,
        "/submit_result",
        game_score,
        "Game score"
    )
    
    print(f"\n2. Testing LOCAL server: http://localhost:5000")
    print("-" * 40)
    
    # Test local server
    try:
        local_health = requests.get("http://localhost:5000/health", timeout=5)
        if local_health.status_code == 200:
            print("   ✅ Local health: PASSED")
            
            # Add local test scores
            for score in test_scores:
                test_endpoint(
                    "http://localhost:5000",
                    "/submit",
                    score,
                    f"Local test: {score['name']}"
                )
        else:
            print(f"   ❌ Local server not running")
            print("      Start it with: python server.py")
    except:
        print("   ❌ Local server not running")
        print("      Start it with: python server.py")
    
    print("\n" + "=" * 60)
    print("🎯 TEST COMPLETE")
    print("=" * 60)
    
    print(f"\n📊 View your leaderboard:")
    print(f"   🔗 Render: {RENDER_URL}")
    print(f"   🔗 Local: http://localhost:5000")
    
    print(f"\n💡 What to expect:")
    print(f"   - Game scores in MAIN table (with medals 🥇🥈🥉)")
    print(f"   - Test scores in GREEN table")
    print(f"   - NO email column shown in display")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()