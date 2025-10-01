#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple script to start both FastAPI backend and provide instructions for
Streamlit.
"""

import subprocess
from pathlib import Path


def start_services():
    """Start FastAPI and provide instructions for Streamlit"""
    venv_python = Path("venv/Scripts/python.exe")

    if not venv_python.exists():
        print("[ERROR] Virtual environment not found.")
        print("[INFO] Run: py -m venv venv")
        print(
            "[INFO] Then: .\\venv\\Scripts\\python.exe -m pip install "
            "-r requirements.txt"
        )
        return False

    print("FastAPI + Streamlit Development Environment")
    print("=" * 45)

    print("\n1. Starting FastAPI backend...")
    try:
        print(
            "   Command: .\\venv\\Scripts\\python.exe -m uvicorn "
            "app.main:app --reload"
        )
        print("   URL: http://localhost:8000")
        print("   Docs: http://localhost:8000/docs")

        # Start FastAPI in the background
        fastapi_process = subprocess.Popen(
            [str(venv_python), "-m", "uvicorn", "app.main:app", "--reload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        print("   [SUCCESS] FastAPI started!")

    except Exception as e:
        print(f"   [ERROR] Failed to start FastAPI: {e}")
        return False

    print("\n2. To start Streamlit frontend:")
    print("   Open a new terminal and run:")
    print(
        "   .\\venv\\Scripts\\python.exe -m streamlit run "
        "streamlit_app.py"
    )
    print("   URL: http://localhost:8501")

    print("\n3. Alternative - Test connectivity:")
    print("   .\\venv\\Scripts\\python.exe test_connectivity.py")

    print("\n[INFO] FastAPI is running. Press Ctrl+C to stop.")

    try:
        # Keep the script running and show FastAPI output
        for line in fastapi_process.stdout:
            print(f"[FastAPI] {line.strip()}")
    except KeyboardInterrupt:
        print("\n[INFO] Stopping FastAPI...")
        fastapi_process.terminate()
        fastapi_process.wait()
        print("[SUCCESS] Services stopped.")

    return True


if __name__ == "__main__":
    start_services()
