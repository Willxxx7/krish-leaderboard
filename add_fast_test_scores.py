import requests

# FAST times to beat real players
fast_tests = [
    ("TEST1", 20),  # Beats will's 33.83
    ("TEST2", 45),  # Beats k's 59.67  
    ("TEST3", 50)   # Beats krish's 61.87
]

print("🥇 ADDING FAST TEST SCORES...")
for name, score in fast_tests:
    requests.post("https://krish-leaderboard.onrender.com/submit",
                json={"name": name, "score": score})
    print(f"Added 🥇 {name}: {score}s")

print("✅ REFRESH: https://krish-leaderboard.onrender.com/")
