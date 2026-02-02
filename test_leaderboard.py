import requests
import time
import sys

def test_server(server_url, server_name):
    """Test a specific server"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing {server_name} server")
    print(f"URL: {server_url}")
    print(f"{'='*60}")
    
    # Test 1: Health check
    print("\n1. Health check:")
    try:
        response = requests.get(f"{server_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Server is healthy")
            print(f"   📊 Tables: {health_data.get('tables', 'N/A')}")
            print(f"   📊 Scores: {health_data.get('score_count', 0)}")
        else:
            print(f"   ❌ Server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect: {e}")
        return False
    
    # Test 2: Add test scores
    print("\n2. Adding test scores:")
    test_scores = [
        {"name": f"{server_name}_Test1", "time_s": 25.5},
        {"name": f"{server_name}_Test2", "time_s": 45.2},
        {"name": f"{server_name}_Test3", "time_s": 68.9},
    ]
    
    success_count = 0
    for test in test_scores:
        try:
            response = requests.post(
                f"{server_url}/submit",
                json=test,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"   ✅ {test['name']}: {test['time_s']:.1f}s")
                success_count += 1
            else:
                print(f"   ❌ {test['name']}: Failed (Status: {response.status_code})")
                print(f"      Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ {test['name']}: Error - {e}")
    
    # Test 3: Add a game score
    print("\n3. Adding game score:")
    try:
        game_data = {
            "name": f"{server_name}_Player",
            "email": f"player@{server_name.lower()}.com",
            "time_s": 33.7,
            "outcome": "win"
        }
        response = requests.post(
            f"{server_url}/submit_result",
            json=game_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"   ✅ Game score added: {game_data['name']}")
        else:
            print(f"   ❌ Game score failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Game score error: {e}")
    
    # Test 4: Check webpage
    print("\n4. Checking webpage:")
    try:
        response = requests.get(server_url, timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Webpage loaded")
            # Check if test scores are mentioned
            if "Test Scores" in response.text:
                print(f"   ✅ Test scores section found")
        else:
            print(f"   ❌ Webpage failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Webpage error: {e}")
    
    return success_count > 0

def main():
    print("\n🚀 WASK Leaderboard Test Script")
    print("=" * 60)
    
    # Test LOCAL server
    print("\n📡 Testing LOCAL server...")
    local_success = test_server("http://localhost:5000", "Local")
    
    # Test RENDER server - IMPORTANT: Render uses port 10000
    print("\n🌐 Testing RENDER server...")
    # Your Render URL (no port needed - Render handles it)
    RENDER_URL = "https://krish-leaderboard.onrender.com"
    render_success = test_server(RENDER_URL, "Render")
    
    # Summary
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    
    if local_success:
        print("✅ Local server: SUCCESS")
        print("   Open: http://localhost:5000")
    else:
        print("❌ Local server: FAILED")
        print("   Run: python server.py")
    
    if render_success:
        print(f"✅ Render server: SUCCESS")
        print(f"   Open: {RENDER_URL}")
    else:
        print(f"❌ Render server: FAILED")
        print(f"   Check Render dashboard for logs")
    
    print("\n" + "="*60)
    print("🎯 What to check:")
    print("="*60)
    print("1. Game scores in MAIN table (with medals)")
    print("2. Test scores in GREEN table")
    print("3. NO email column shown")
    print("\n✅ Test complete!")

if __name__ == "__main__":
    main()