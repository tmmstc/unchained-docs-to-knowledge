#!/usr/bin/env python3
"""
Simple script to start just the FastAPI server for testing.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Start FastAPI server."""
    print("🚀 Starting FastAPI backend on http://localhost:8000")
    
    venv_python = Path("venv/Scripts/python.exe")
    if not venv_python.exists():
        print("❌ Virtual environment not found. Run: py -m venv venv")
        return 1
    
    try:
        # Start FastAPI server
        subprocess.run([
            str(venv_python), 
            "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting FastAPI: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 FastAPI server stopped")
        return 0

if __name__ == "__main__":
    sys.exit(main())