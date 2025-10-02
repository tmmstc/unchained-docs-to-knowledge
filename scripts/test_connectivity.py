#!/usr/bin/env python3
"""
Simple connectivity test for FastAPI backend.
"""
import requests
import time


def test_backend_connection():
    """Test connection to FastAPI backend."""
    print("Testing FastAPI backend connection...")
    print("Waiting for backend to be ready...")

    time.sleep(2)

    try:
        print("Attempting to connect to http://127.0.0.1:8000...")
        response = requests.get("http://127.0.0.1:8000/", timeout=10)

        if response.status_code == 200:
            print("OK Successfully connected to backend!")
            data = response.json()
            print(f"OK Message: {data.get('message', 'N/A')}")
            print(f"OK Version: {data.get('version', 'N/A')}")
            return True
        else:
            print(f"ERROR Backend returned status code: " f"{response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("ERROR Cannot connect to backend at " "http://127.0.0.1:8000")
        print("ERROR Make sure the backend is running with: " "py -m uvicorn app.main:app --reload")
        return False

    except Exception as e:
        print(f"ERROR Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_backend_connection()
    import sys

    sys.exit(0 if success else 1)
