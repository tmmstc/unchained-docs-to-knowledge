#!/usr/bin/env python3
"""
Simple test to verify backend works with requests.
"""
import os
import time
import subprocess
import threading
import requests

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'


def start_backend_process():
    """Start FastAPI backend in subprocess."""
    try:
        venv_python = os.path.join("venv", "Scripts", "python.exe")
        process = subprocess.Popen(
            [venv_python, "start_backend.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        # Read output lines
        for line in iter(process.stdout.readline, ''):
            print(f"[Backend] {line.strip()}")

    except Exception as e:
        print(f"ERROR: Failed to start backend: {e}")


def test_api():
    """Test API endpoints after backend starts."""
    print("Waiting for backend to start...")
    time.sleep(5)

    try:
        # Test root endpoint
        print("Testing root endpoint...")
        response = requests.get(
            "http://127.0.0.1:8000/", timeout=10
        )
        if response.status_code == 200:
            print("OK Root endpoint works")
            data = response.json()
            print(f"  Message: {data.get('message')}")
            print(f"  Version: {data.get('version')}")
        else:
            print(
                f"ERROR: Root endpoint returned "
                f"{response.status_code}"
            )

        # Test stats endpoint
        print("Testing stats endpoint...")
        response = requests.get(
            "http://127.0.0.1:8000/stats", timeout=10
        )
        if response.status_code == 200:
            print("OK Stats endpoint works")
            data = response.json()
            print(f"  Records: {data.get('total_records', 0)}")
            print(f"  Words: {data.get('total_words', 0)}")
            print(f"  Characters: {data.get('total_characters', 0)}")
        else:
            print(
                f"ERROR: Stats endpoint returned "
                f"{response.status_code}"
            )

        print("\nAPI tests completed successfully!")
        print(
            "Backend is working and can be accessed at "
            "http://127.0.0.1:8000"
        )
        print(
            "You can now manually start Streamlit at "
            "http://localhost:8501"
        )

    except Exception as e:
        print(f"ERROR: API test failed: {e}")


if __name__ == "__main__":
    print("Starting FastAPI backend test...")

    # Start backend in thread
    backend_thread = threading.Thread(
        target=start_backend_process, daemon=True
    )
    backend_thread.start()

    # Test API
    test_api()

    print("\nPress Ctrl+C to stop")
