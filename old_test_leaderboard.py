import requests

print("🚀 KRISH LEADERBOARD - DUAL TESTS (Local + Production)\n")

def test_local_server():
    try:
        print("🧪 Testing LOCAL server (python server.py)...")
        
        # Test health endpoint
        r = requests.get("http://localhost:5000/health", timeout=3)
        if r.status_code == 200:
            print(f"   ✅ LOCAL Health: {r.status_code} - {r.text}")
        else:
            print(f"   ❌ LOCAL Health: {r.status_code}")
            return
        
        # Test main submission endpoint
        print("   Testing /submit_result endpoint...")
        r = requests.post("http://localhost:5000/submit_result",
                          json={"name": "LocalTest", "email": "test@example.com", 
                                "time_s": 99.9, "outcome": "win"},
                          timeout=3)
        if r.status_code == 200:
            print(f"   ✅ LOCAL Submit Result: {r.status_code}")
        else:
            print(f"   ❌ LOCAL Submit Result: {r.status_code}")
        
        # Test legacy /submit endpoint (for test compatibility)
        print("   Testing /submit endpoint...")
        r = requests.post("http://localhost:5000/submit",
                          json={"name": "LocalTest", "time_s": 999},
                          timeout=3)
        if r.status_code == 200:
            print(f"   ✅ LOCAL Submit: {r.status_code}")
        else:
            print(f"   ❌ LOCAL Submit: {r.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ LOCAL server NOT running! Start: python server.py")
    except Exception as e:
        print(f"   ❌ LOCAL test error: {e}")

def test_render_production():
    try:
        print("\n🌐 Testing PRODUCTION Render server...")
        
        # Replace with your actual Render URL
        base_url = "https://krish-leaderboard.onrender.com"
        
        # Test health endpoint
        r = requests.get(f"{base_url}/health", timeout=10)
        if r.status_code == 200 and r.text.strip() == "OK":
            print("✅ PRODUCTION Health check PASSED")
        else:
            print(f"❌ PRODUCTION Health: {r.status_code} - {r.text}")
            return
        
        # Test main submission endpoint
        r = requests.post(f"{base_url}/submit_result",
                          json={"name": "RenderTest", "email": "render@test.com",
                                "time_s": 88.8, "outcome": "win"},
                          timeout=10)
        if r.status_code == 200:
            print("✅ PRODUCTION Score submission PASSED")
        else:
            print(f"❌ PRODUCTION Submit: {r.status_code}")
        
        # Test home page
        r = requests.get(f"{base_url}/", timeout=10)
        if r.status_code == 200:
            print(f"✅ PRODUCTION Leaderboard: {r.status_code} OK")
        else:
            print(f"❌ PRODUCTION Leaderboard: {r.status_code}")
        
        # Test API endpoint
        r = requests.get(f"{base_url}/leaderboard", timeout=10)
        if r.status_code == 200:
            print(f"✅ PRODUCTION API: {r.status_code} OK")
        else:
            print(f"❌ PRODUCTION API: {r.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"❌ PRODUCTION unreachable or timed out: {e}")
        print("💡 Check: render.com → krish-leaderboard → Logs tab")

if __name__ == "__main__":
    test_local_server()
    test_render_production()
    print("\n🎉 TESTS COMPLETE!")
    print("🌐 Live site: https://krish-leaderboard.onrender.com/")