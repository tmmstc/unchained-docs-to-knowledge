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


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


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

        # Set working directory to the resource path for database access
        app_path = get_resource_path("app")
        if os.path.exists(app_path):
            sys.path.insert(0, get_resource_path("."))

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
        import traceback

        traceback.print_exc()


def main():
    """Main entry point for desktop application."""
    print("=" * 70)
    print("PDF OCR Desktop Application")
    print("=" * 70)

    # Print environment info for debugging
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")

    # Handle PyInstaller bundle
    if getattr(sys, "frozen", False):
        print("Running from PyInstaller bundle")
        print(f"Bundle directory: {sys._MEIPASS}")

        # Change working directory to a writable location
        # Use the directory where the exe is located for database and logs
        exe_dir = os.path.dirname(sys.executable)
        os.chdir(exe_dir)
        print(f"Changed working directory to: {os.getcwd()}")
    else:
        print("Running from Python script")

    print("=" * 70)

    # Start FastAPI in background thread
    if not is_port_in_use(8000):
        print("Starting FastAPI backend on http://127.0.0.1:8000")
        fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
        fastapi_thread.start()
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

    # Get the correct path to streamlit_app.py
    if getattr(sys, "frozen", False):
        streamlit_app_path = get_resource_path(
            os.path.join("frontend", "streamlit_app.py")
        )
    else:
        streamlit_app_path = os.path.join("frontend", "streamlit_app.py")

    print(f"Launching Streamlit from: {streamlit_app_path}")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            streamlit_app_path,
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
