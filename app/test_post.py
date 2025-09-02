# app/test_post.py
import requests
import sys

def main():
    url = "http://127.0.0.1:8000/run"
    query = sys.argv[1] if len(sys.argv) > 1 else "hello"

    try:
        resp = requests.post(url, json={"input": query})
        resp.raise_for_status()
        data = resp.json()
        print("\n=== Agent Response ===")
        print(data["output"])
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    main()
