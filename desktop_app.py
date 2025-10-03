"""
Desktop launcher for Streamlit application.
This script launches the FastAPI backend and opens the Streamlit app.
"""

import subprocess
import sys
import time
import os
import threading
import webbrowser


def is_port_in_use(port):
    """Check if a port is already in use."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def run_fastapi():
    """Run FastAPI backend server."""
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            env=env,
            check=False,
        )
    except Exception as e:
        print(f"Error starting FastAPI: {e}")


def main():
    """Main entry point for desktop application."""
    print("Starting PDF OCR Desktop Application...")

    # Start FastAPI in background thread
    if not is_port_in_use(8000):
        fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
        fastapi_thread.start()
        print("FastAPI backend started on http://127.0.0.1:8000")
        time.sleep(3)
    else:
        print("FastAPI backend already running on http://127.0.0.1:8000")

    # Check if Streamlit is already running
    if not is_port_in_use(8501):
        print("Starting Streamlit frontend on http://127.0.0.1:8501")

        def open_browser():
            time.sleep(2)
            webbrowser.open("http://127.0.0.1:8501")

        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
    else:
        print("Streamlit already running, opening browser...")
        webbrowser.open("http://127.0.0.1:8501")

    # Run Streamlit (this will block)
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "frontend/streamlit_app.py",
            "--server.address",
            "127.0.0.1",
            "--server.port",
            "8501",
            "--server.headless",
            "true",
        ],
        env=env,
    )


if __name__ == "__main__":
    main()
