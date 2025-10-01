#!/usr/bin/env python3
"""
Simple script to start the FastAPI backend with proper encoding.
"""
import os

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'


def start_backend():
    """Start the FastAPI backend."""
    print("Starting FastAPI backend...")

    try:
        import uvicorn
        from app.main import app

        print("FastAPI backend starting on http://127.0.0.1:8000")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
        )
    except Exception as e:
        print(f"ERROR: Failed to start backend: {e}")
        return False


if __name__ == "__main__":
    start_backend()
