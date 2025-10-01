#!/usr/bin/env python3
"""
Single entry point script to run both FastAPI and Streamlit services.

This is the main launch script for the PDF OCR Processing Application.
Starts both services simultaneously with proper error handling
and graceful shutdown.
"""

import subprocess
import threading
import time
import signal
import sys
import os
from pathlib import Path


class ApplicationLauncher:
    """Manages startup and shutdown of FastAPI and Streamlit services."""

    def __init__(self):
        self.processes = []
        self.running = True
        self.venv_python = Path("venv/Scripts/python.exe")

    def verify_environment(self):
        """Verify that the virtual environment exists."""
        if not self.venv_python.exists():
            print("❌ ERROR: Virtual environment not found")
            print("\nSetup required:")
            print("1. Create virtual environment:")
            print("   py -m venv venv")
            print("\n2. Install dependencies:")
            pip_cmd = ".\\venv\\Scripts\\python.exe -m pip install -r"
            print(f"   {pip_cmd} requirements.txt")
            return False

        print("✅ Virtual environment found")
        return True

    def run_fastapi(self):
        """Run FastAPI backend server."""
        try:
            print("\n🚀 Starting FastAPI backend...")
            print("   URL: http://localhost:8000")
            print("   API Docs: http://localhost:8000/docs")

            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'

            process = subprocess.Popen(
                [
                    str(self.venv_python),
                    "-m",
                    "uvicorn",
                    "app.main:app",
                    "--reload",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8000",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                env=env,
            )
            self.processes.append(process)

            # Stream output
            for line in process.stdout:
                if self.running:
                    print(f"[FastAPI] {line.strip()}")
                else:
                    break

        except Exception as e:
            print(f"❌ ERROR starting FastAPI: {e}")

    def run_streamlit(self):
        """Run Streamlit frontend server."""
        try:
            # Wait for FastAPI to initialize
            time.sleep(3)

            print("\n🎨 Starting Streamlit frontend...")
            print("   URL: http://localhost:8501")

            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'

            process = subprocess.Popen(
                [
                    str(self.venv_python),
                    "-m",
                    "streamlit",
                    "run",
                    "frontend/streamlit_app.py",
                    "--server.address",
                    "0.0.0.0",
                    "--server.port",
                    "8501",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                env=env,
            )
            self.processes.append(process)

            # Stream output
            for line in process.stdout:
                if self.running:
                    print(f"[Streamlit] {line.strip()}")
                else:
                    break

        except Exception as e:
            print(f"❌ ERROR starting Streamlit: {e}")

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print("\n\n🛑 Shutting down services...")
        self.running = False

        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except Exception:
                process.kill()

        print("✅ Services stopped")
        sys.exit(0)

    def run(self):
        """Start both services."""
        print("=" * 70)
        print("PDF OCR Processing Application")
        print("=" * 70)

        # Verify environment
        if not self.verify_environment():
            sys.exit(1)

        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)

        print("\n📋 Starting application services...")
        print("   Press Ctrl+C to stop\n")

        # Start FastAPI in background thread
        fastapi_thread = threading.Thread(
            target=self.run_fastapi, daemon=True
        )
        fastapi_thread.start()

        # Start Streamlit in background thread
        streamlit_thread = threading.Thread(
            target=self.run_streamlit, daemon=True
        )
        streamlit_thread.start()

        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)


if __name__ == "__main__":
    launcher = ApplicationLauncher()
    launcher.run()
