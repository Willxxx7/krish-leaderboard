# test_leaderboard.py code below

import requests

print("🚀 KRISH LEADERBOARD - DUAL TESTS (Local + Production)\n")

def test_local_server():
    try:
        print("🧪 Testing LOCAL server (python server.py)...")
        r = requests.get("http://localhost:5000/health", timeout=3)
        assert r.status_code == 200
        print(f"   ✅ LOCAL Health: {r.status_code} - {r.text}")

        r = requests.post("http://localhost:5000/submit",
                          json={"name": "LocalTest", "score": 999},
                          timeout=3)
        assert r.status_code == 200
        print(f"   ✅ LOCAL Submit: {r.status_code}")
    except requests.exceptions.RequestException:
        print("   ❌ LOCAL server NOT running! Start: python server.py")
    except AssertionError:
        print("   ❌ LOCAL tests FAILED (health or submit not 200)")

def test_render_production():
    try:
        print("\n🌐 Testing PRODUCTION Render server...")
        r = requests.get("https://krish-leaderboard.onrender.com/health", timeout=10)
        assert r.status_code == 200
        assert r.text.strip() == "OK"
        print("✅ PRODUCTION Health check PASSED")

        r = requests.post("https://krish-leaderboard.onrender.com/submit",
                          json={"name": "RenderTest", "score": 888},
                          timeout=10)
        assert r.status_code == 200
        print("✅ PRODUCTION Score submission PASSED")

        r = requests.get("https://krish-leaderboard.onrender.com/", timeout=10)
        assert r.status_code == 200
        print(f"✅ PRODUCTION Leaderboard: {r.status_code} OK")

    except AssertionError:
        print("❌ PRODUCTION tests FAILED (health/submit/leaderboard not OK)")
    except requests.exceptions.RequestException as e:
        print(f"❌ PRODUCTION unreachable or timed out: {e}")
        print("💡 Check: render.com → krish-leaderboard → Logs tab")

if __name__ == "__main__":
    test_local_server()
    test_render_production()
    print("\n🎉 TESTS COMPLETE!")
    print("🌐 Live site: https://krish-leaderboard.onrender.com/")
