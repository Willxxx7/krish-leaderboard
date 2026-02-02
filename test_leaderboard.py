import requests

def test_health_check():
    response = requests.get("https://krish-leaderboard.onrender.com/health")
    assert response.status_code == 200
    assert response.text == "OK"
    print("✅ Health check PASSED")

def test_submit_score():
    response = requests.post("https://krish-leaderboard.onrender.com/submit",
                              json={"name": "UnitTest", "time_s": 99.9})
    assert response.status_code == 200
    print("✅ Score submission PASSED")

if __name__ == "__main__":
    test_health_check()
    test_submit_score()

