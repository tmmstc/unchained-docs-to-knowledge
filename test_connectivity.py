#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify FastAPI backend connectivity.
"""

import httpx
import json

BACKEND_URL = "http://localhost:8000"

def test_backend():
    """Test connection to FastAPI backend"""
    try:
        with httpx.Client(timeout=5) as client:
            response = client.get(f"{BACKEND_URL}/")
            
        if response.status_code == 200:
            print("[SUCCESS] Successfully connected to FastAPI backend!")
            print("Response:", json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"[ERROR] Backend returned status code: {response.status_code}")
            return False
            
    except httpx.ConnectError:
        print("[ERROR] Could not connect to FastAPI backend. Is it running on http://localhost:8000?")
        print("[INFO] Start the FastAPI server with: .\\venv\\Scripts\\python.exe -m uvicorn app.main:app --reload")
        return False
    
    except httpx.TimeoutException:
        print("[ERROR] Connection timed out. The backend might be slow to respond.")
        return False
    
    except Exception as e:
        print(f"[ERROR] Request failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("FastAPI Backend Connectivity Test")
    print("=" * 40)
    test_backend()