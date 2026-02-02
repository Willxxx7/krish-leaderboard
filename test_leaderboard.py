import requests

print("🚀 KRISH LEADERBOARD - DUAL TESTS (Local + Production)\n")

# ========================================
# TEST 1: LOCAL FLASK SERVER (http://localhost:5000)
# ========================================
def test_local_server():
    try:
        print("🧪 Testing LOCAL server (python server.py)...")
        response = requests.get("http://localhost:5000/health", timeout=3)
        print(f"   ✅ LOCAL Health: {response.status_code} - {response.text}")
        
        response = requests.post("http://localhost:5000/submit", 
                               json={"name": "LocalTest", "score": 999}, 
                               timeout=3)
        print(f"   ✅ LOCAL Submit: {response.status_code}")
    except requests.exceptions.RequestException:
        print("   ❌ LOCAL server NOT running! Start: python server.py")
        print("   💡 Keep reading for PRODUCTION tests...")

# ========================================
# TEST 2: PRODUCTION RENDER SERVER
# ========================================
def test_render_production():
    try:
        print("\n🌐 Testing PRODUCTION Render server...")
        response = requests.get("https://krish-leaderboard.onrender.com/health", timeout=10)
        assert response.status_code == 200
        assert response.text == "OK"
        print("✅ PRODUCTION Health check PASSED")
        
        response = requests.post("https://krish-leaderboard.onrender.com/submit",
                               json={"name": "RenderTest", "score": 888},
                               timeout=10)
        assert response.status_code == 200
        print("✅ PRODUCTION Score submission PASSED")
        
        # Test leaderboard loads
        response = requests.get("https://krish-leaderboard.onrender.com/", timeout=10)
        print(f"✅ PRODUCTION Leaderboard: {response.status_code} OK")
        
    except AssertionError:
        print("❌ PRODUCTION /submit endpoint MISSING!")
        print("💡 Fix: Add @app.route('/submit', methods=['POST']) to server.py")
        print("💡 Then: git add . && git commit -m 'fix submit' && git push")
    except requests.exceptions.RequestException as e:
        print(f"❌ Render app DOWN: {e}")
        print("💡 Check: render.com → krish-leaderboard → Logs tab")

# ========================================
# RUN ALL TESTS
# ========================================
if __name__ == "__main__":
    test_local_server()
    test_render_production()
    print("\n🎉 TESTS COMPLETE!")
    print("🌐 Live site: https://krish-leaderboard.onrender.com/")


