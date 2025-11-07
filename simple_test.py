import requests

def test_single():
    try:
        response = requests.get("http://127.0.0.1:8000/fibonacci/10", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Content: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_single()