import requests
import sys
import time

def print_banner():
    print("=" * 60)
    print("🚀 WASK LEADERBOARD TEST SCRIPT")
    print("=" * 60)
    print("Purpose: Send test scores to both local and production servers")
    print("Test scores appear in GREEN table, game scores in main table")
    print("Email columns are NOT displayed in the HTML table")
    print("=" * 60)

def test_server(server_url, server_name):
    """Test a specific server"""
    print(f"\n📡 Testing {server_name} server: {server_url}")
    
    # Test health endpoint
    try:
        health_response = requests.get(f"{server_url}/health", timeout=10)
        if health_response.status_code == 200 and health_response.text.strip() == "OK":
            print(f"   ✅ Health check: PASSED")
        else:
            print(f"   ❌ Health check: FAILED (Status: {health_response.status_code}, Response: {health_response.text})")
            return False
    except Exception as e:
        print(f"   ❌ Health check: ERROR - {e}")
        return False
    
    # Send test scores to /submit endpoint (goes to test table)
    test_data = [
        {"name": f"{server_name}_Fast", "time_s": 25.5},
        {"name": f"{server_name}_Medium", "time_s": 45.2},
        {"name": f"{server_name}_Slow", "time_s": 68.9},
    ]
    
    successful_tests = 0
    print(f"   📤 Sending {len(test_data)} test scores to /submit endpoint...")
    for test in test_data:
        try:
            response = requests.post(
                f"{server_url}/submit",
                json=test,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"      ✅ {test['name']}: {test['time_s']:.1f}s")
                successful_tests += 1
            else:
                print(f"      ❌ {test['name']}: Failed (Status {response.status_code})")
                
        except Exception as e:
            print(f"      ❌ {test['name']}: Error - {e}")
    
    # Also send a main game score to /submit_result endpoint (goes to main table)
    print(f"   🎮 Sending game score to /submit_result endpoint...")
    try:
        game_data = {
            "name": f"{server_name}_GamePlayer",
            "email": f"test@{server_name.lower()}.com",  # Email sent but not displayed
            "time_s": 55.5,
            "outcome": "win"
        }
        response = requests.post(
            f"{server_url}/submit_result",
            json=game_data,
            timeout=10
        )
        if response.status_code == 200:
            print(f"      ✅ Game score added: {game_data['name']} - {game_data['time_s']}s")
        else:
            print(f"      ❌ Game score failed (Status {response.status_code})")
    except Exception as e:
        print(f"      ❌ Game score error: {e}")
    
    # Check the webpage
    print(f"   🌐 Checking leaderboard webpage...")
    try:
        page_response = requests.get(f"{server_url}/", timeout=10)
        if page_response.status_code == 200:
            print(f"      ✅ Webpage loaded successfully")
        else:
            print(f"      ❌ Webpage failed (Status {page_response.status_code})")
    except Exception as e:
        print(f"      ❌ Webpage error: {e}")
    
    return successful_tests > 0

def main():
    print_banner()
    
    print("\n1️⃣  Testing LOCAL server")
    local_success = test_server("http://localhost:5000", "Local")
    
    print("\n2️⃣  Testing PRODUCTION server")
    # REPLACE WITH YOUR ACTUAL RENDER URL
    production_url = "https://krish-leaderboard.onrender.com"
    prod_success = test_server(production_url, "Render")
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    if local_success:
        print("✅ Local server: SUCCESS")
        print(f"   🔗 View at: http://localhost:5000")
        print(f"   📁 Database: leaderboard.db in your solution folder")
    else:
        print("❌ Local server: FAILED")
        print("   💡 Make sure server.py is running: python server.py")
    
    if prod_success:
        print("✅ Production server: SUCCESS")
        print(f"   🔗 View at: {production_url}")
        print(f"   📁 Database: /tmp/leaderboard.db on Render.com")
    else:
        print("❌ Production server: FAILED or unreachable")
        print("   💡 Check if your Render.com deployment is active")
        print("   💡 Make sure you updated the URL in this script")
    
    print("\n" + "=" * 60)
    print("🎯 WHAT TO LOOK FOR ON THE WEBPAGE:")
    print("=" * 60)
    print("1. 🎮 Game Scores Table:")
    print("   - Real game scores (with medals 🥇🥈🥉)")
    print("   - NO email column shown")
    print("   - Columns: Rank, Name, Time, Result, Submitted")
    print()
    print("2. 🧪 Test Scores Table:")
    print("   - Green themed table")
    print("   - Test scores from this script")
    print("   - Columns: #, Test Player, Time, Submitted")
    print()
    print("3. 📊 Stats section at bottom")
    
    print("\n" + "=" * 60)
    print("🔗 QUICK LINKS:")
    if local_success:
        print(f"   Local:      http://localhost:5000")
    if prod_success:
        print(f"   Production: {production_url}")
    
    print("\n✅ Test script completed!")

if __name__ == "__main__":
    main()