import requests
import time
import sys

def print_colored(text, color_code):
    """Print colored text for better visibility"""
    print(f"\033[{color_code}m{text}\033[0m")

def test_server(server_url, server_name):
    """Test a specific server and add test scores"""
    print_colored(f"\n{'='*60}", "1;36")  # Cyan
    print_colored(f"🧪 TESTING {server_name.upper()} SERVER", "1;33")  # Yellow
    print_colored(f"URL: {server_url}", "1;36")
    print_colored(f"{'='*60}", "1;36")
    
    # Test 1: Health check
    print("\n1️⃣  Health Check:")
    try:
        response = requests.get(f"{server_url}/health", timeout=10)
        if response.status_code == 200:
            print_colored(f"   ✅ HEALTH: Server is running (Status: {response.status_code})", "1;32")
            if hasattr(response, 'json'):
                health_data = response.json()
                print(f"   📊 Database: {health_data.get('path', 'N/A')}")
                print(f"   📊 Tables: {health_data.get('tables', 'N/A')}")
        else:
            print_colored(f"   ❌ HEALTH: Server returned {response.status_code}", "1;31")
            return False
    except requests.exceptions.ConnectionError:
        print_colored(f"   ❌ HEALTH: Cannot connect to {server_url}", "1;31")
        print(f"   💡 Make sure the server is running at {server_url}")
        return False
    except Exception as e:
        print_colored(f"   ❌ HEALTH: Error - {e}", "1;31")
        return False
    
    # Test 2: Add test scores via /submit endpoint
    print("\n2️⃣  Adding Test Scores:")
    test_scores = [
        {"name": f"{server_name}_FastRunner", "time_s": 25.5},
        {"name": f"{server_name}_MediumPace", "time_s": 45.2},
        {"name": f"{server_name}_SlowWalker", "time_s": 68.9},
        {"name": f"{server_name}_SpeedDemon", "time_s": 18.3},
        {"name": f"{server_name}_Turtle", "time_s": 95.7},
    ]
    
    successful_tests = 0
    for test in test_scores:
        try:
            response = requests.post(
                f"{server_url}/submit",
                json=test,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                print_colored(f"   ✅ {test['name']}: {test['time_s']:.1f}s - {data.get('message', 'Added')}", "1;32")
                successful_tests += 1
            else:
                print_colored(f"   ❌ {test['name']}: Failed (Status: {response.status_code})", "1;31")
                print(f"      Response: {response.text}")
                
        except Exception as e:
            print_colored(f"   ❌ {test['name']}: Error - {e}", "1;31")
    
    # Test 3: Add a game score via /submit_result endpoint
    print("\n3️⃣  Adding Game Score:")
    try:
        game_data = {
            "name": f"{server_name}_Champion",
            "email": f"player@{server_name.lower()}.com",
            "time_s": 33.7,
            "outcome": "win"
        }
        response = requests.post(
            f"{server_url}/submit_result",
            json=game_data,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print_colored(f"   ✅ Game Score: {game_data['name']} - {game_data['time_s']}s", "1;32")
        else:
            print_colored(f"   ❌ Game Score: Failed (Status: {response.status_code})", "1;31")
            print(f"      Response: {response.text}")
    except Exception as e:
        print_colored(f"   ❌ Game Score Error: {e}", "1;31")
    
    # Test 4: Verify scores are in database via API
    print("\n4️⃣  Verifying Scores:")
    try:
        # Check game scores API
        response = requests.get(f"{server_url}/leaderboard", timeout=10)
        if response.status_code == 200:
            game_scores = response.json()
            print(f"   📊 Game Scores in API: {len(game_scores)}")
        
        # Check the webpage
        response = requests.get(server_url, timeout=10)
        if response.status_code == 200:
            print_colored(f"   ✅ Webpage loaded successfully", "1;32")
        else:
            print_colored(f"   ❌ Webpage failed to load (Status: {response.status_code})", "1;31")
    except Exception as e:
        print_colored(f"   ❌ Verification Error: {e}", "1;31")
    
    return successful_tests > 0

def main():
    """Main test function"""
    print_colored("\n" + "="*70, "1;35")
    print_colored("🚀 WASK LEADERBOARD - COMPREHENSIVE TEST SCRIPT", "1;35")
    print_colored("="*70, "1;35")
    print("\nThis script will:")
    print("  • Send test scores to /submit endpoint (appear in GREEN table)")
    print("  • Send game scores to /submit_result endpoint (appear in MAIN table)")
    print("  • Test both local and production servers")
    print("  • Verify data appears on the webpage")
    
    print_colored("\n📡 IMPORTANT: Make sure your servers are running!", "1;33")
    print("   Local: python server.py")
    print("   Render: Auto-deployed from GitHub")
    
    input("\nPress Enter to start tests...")
    
    results = {}
    
    # Test LOCAL server
    print_colored("\n" + "="*70, "1;34")
    print_colored("🔧 TESTING LOCAL SERVER (localhost:5000)", "1;34")
    print_colored("="*70, "1;34")
    
    local_success = test_server("http://localhost:5000", "Local")
    results["local"] = local_success
    
    # Test RENDER server
    print_colored("\n" + "="*70, "1;34")
    print_colored("🌐 TESTING PRODUCTION SERVER (Render.com)", "1;34")
    print_colored("="*70, "1;34")
    
    # UPDATE THIS TO YOUR ACTUAL RENDER URL
    RENDER_URL = "https://krish-leaderboard.onrender.com"
    prod_success = test_server(RENDER_URL, "Render")
    results["render"] = prod_success
    
    # Summary
    print_colored("\n" + "="*70, "1;35")
    print_colored("📊 TEST RESULTS SUMMARY", "1;35")
    print_colored("="*70, "1;35")
    
    if results.get("local"):
        print_colored("✅ LOCAL SERVER: SUCCESS", "1;32")
        print(f"   🔗 Open: http://localhost:5000")
        print(f"   📍 You should see:")
        print(f"     • Game scores in main table (with medals 🥇🥈🥉)")
        print(f"     • Test scores in green table")
        print(f"     • NO email column in display")
    else:
        print_colored("❌ LOCAL SERVER: FAILED", "1;31")
        print("   💡 Make sure server.py is running:")
        print("      python server.py")
    
    if results.get("render"):
        print_colored(f"\n✅ RENDER SERVER: SUCCESS", "1;32")
        print(f"   🔗 Open: {RENDER_URL}")
        print(f"   📍 Same view as local, but on the web!")
    else:
        print_colored(f"\n❌ RENDER SERVER: FAILED", "1;31")
        print(f"   💡 Check:")
        print(f"      • Is your Render deployment active?")
        print(f"      • Did you update the URL in this script?")
        print(f"      • Check Render.com dashboard → Logs")
    
    print_colored("\n" + "="*70, "1;35")
    print_colored("🎯 NEXT STEPS", "1;35")
    print_colored("="*70, "1;35")
    
    if results.get("local"):
        print("1. Open your browser to: http://localhost:5000")
        print("2. You should see BOTH tables:")
        print("   • Main table with game scores (Local_Champion)")
        print("   • Green table with test scores (Local_FastRunner, etc.)")
    
    if results.get("render"):
        print(f"3. Open your browser to: {RENDER_URL}")
        print("4. You should see the same layout as local, but on the web")
    
    print("\n5. Run this script again to add more test data")
    print("6. Game data comes from your actual game/app via /submit_result")
    
    print_colored("\n✅ TEST SCRIPT COMPLETED!", "1;32")
    print("   Happy testing! 🎮🧪")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n⚠️ Test interrupted by user", "1;33")
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n\n❌ Unexpected error: {e}", "1;31")
        sys.exit(1)