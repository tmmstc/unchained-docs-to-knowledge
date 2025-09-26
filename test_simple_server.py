#!/usr/bin/env python3
"""
Simple test to check if FastAPI can start and respond.
"""
import sys
import time
import requests
import subprocess
import threading
from pathlib import Path

def test_server_startup():
    """Test if FastAPI server can start and respond."""
    print("🧪 Testing FastAPI server startup...")
    
    venv_python = Path("venv/Scripts/python.exe")
    if not venv_python.exists():
        print("❌ Virtual environment not found")
        return False
    
    # Start server in background
    process = subprocess.Popen([
        str(venv_python), 
        "-m", "uvicorn", 
        "app.main:app", 
        "--host", "127.0.0.1", 
        "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Give server time to start
    time.sleep(5)
    
    try:
        # Test connectivity
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Server responded successfully!")
            print(f"Response: {data}")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    finally:
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=5)
        except:
            process.kill()

if __name__ == "__main__":
    success = test_server_startup()
    sys.exit(0 if success else 1)