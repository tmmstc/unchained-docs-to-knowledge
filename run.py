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
import webbrowser
import urllib.request
import urllib.error
from pathlib import Path


class ApplicationLauncher:
    """Manages startup and shutdown of FastAPI and Streamlit services."""

    def __init__(self):
        self.processes = []
        self.running = True
        self.browser_launched = False
        self.shutdown_timeout = 300  # 5 minutes timeout
        self.start_time = None

        # Cross-platform virtualenv python path.
        # On Windows venv uses Scripts, on POSIX it uses bin.
        win_path = Path("venv") / "Scripts" / "python.exe"
        posix_path = Path("venv") / "bin" / "python"
        # Prefer the venv python if it exists, otherwise fall back to
        # whichever is present.
        if win_path.exists():
            self.venv_python = win_path
        elif posix_path.exists():
            self.venv_python = posix_path
        else:
            # Last-resort: use system python (may not have required deps)
            self.venv_python = Path(sys.executable)

    def verify_environment(self):
        """Verify that the virtual environment exists (cross-platform).

        Checks for a `venv` directory with either a Windows or POSIX python
        executable. If missing, prints clear setup and activation steps for
        both platforms.
        """
        venv_dir = Path("venv")
        win_python = venv_dir / "Scripts" / "python.exe"
        posix_python = venv_dir / "bin" / "python"

        if not venv_dir.exists() or (
            not win_python.exists() and not posix_python.exists()
        ):
            print("❌ ERROR: Virtual environment not found")
            print("\nSetup required:")
            print("1. Create virtual environment:")
            print("   # Windows")
            print("   py -m venv venv")
            print("   # POSIX (Linux/macOS)")
            print("   python3 -m venv venv")
            print("\n2. Activate the virtual environment:")
            print("   # Windows PowerShell")
            print("   .\\venv\\Scripts\\Activate.ps1")
            print("   # POSIX (bash/zsh)")
            print("   source venv/bin/activate")
            print("\n3. Install dependencies:")
            print("   python -m pip install -r requirements.txt")
            return False

        print("✅ Virtual environment found")
        return True

    def check_service_health(self, url, service_name, timeout=1):
        """Check if a service is ready by making an HTTP request."""
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                return response.status == 200
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            return False

    def wait_for_service(
        self, url, service_name, max_retries=30, initial_delay=1
    ):
        """Wait for a service with exponential backoff."""
        print(f"⏳ Waiting for {service_name} to be ready...")

        delay = initial_delay
        for attempt in range(1, max_retries + 1):
            if not self.running:
                return False

            if self.check_service_health(url, service_name):
                print(f"✅ {service_name} is ready!")
                return True

            if attempt < max_retries:
                time.sleep(delay)
                # Exponential backoff with cap at 5 seconds
                delay = min(delay * 1.5, 5)

        msg = f"{service_name} failed to start after {max_retries} attempts"
        print(f"❌ {msg}")
        return False

    def launch_browser(self, url, max_retries=5, initial_delay=2):
        """Launch browser with retry logic and exponential backoff."""
        if self.browser_launched:
            return

        print("\n🌐 Attempting to launch browser...")

        delay = initial_delay
        for attempt in range(1, max_retries + 1):
            if not self.running:
                return

            if self.check_service_health(url, "Streamlit", timeout=2):
                try:
                    print(f"🚀 Opening browser to {url}")
                    webbrowser.open(url)
                    self.browser_launched = True
                    return
                except Exception as e:
                    print(f"⚠️  Failed to launch browser: {e}")
                    return

            if attempt < max_retries:
                retry_msg = (
                    f"   Retry {attempt}/{max_retries} - "
                    f"waiting {delay:.1f}s..."
                )
                print(retry_msg)
                time.sleep(delay)
                delay = min(delay * 1.5, 10)

        warn_msg = (
            f"⚠️  Could not verify Streamlit is ready "
            f"after {max_retries} attempts"
        )
        print(warn_msg)
        print(f"   Please manually open: {url}")

    def run_fastapi(self):
        """Run FastAPI backend server."""
        try:
            print("\n🚀 Starting FastAPI backend...")
            print("   URL: http://localhost:8000")
            print("   API Docs: http://localhost:8000/docs")

            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

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
                encoding="utf-8",
                errors="replace",
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
            self.running = False

    def run_streamlit(self):
        """Run Streamlit frontend server."""
        try:
            print("\n🎨 Starting Streamlit frontend...")
            print("   URL: http://localhost:8501")

            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

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
                    "--server.headless",
                    "true",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding="utf-8",
                errors="replace",
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
            self.running = False

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print("\n\n🛑 Shutting down services...")
        self.running = False

        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("   Force killing unresponsive process...")
                process.kill()
            except Exception as e:
                print(f"   Error stopping process: {e}")
                try:
                    process.kill()
                except Exception:
                    pass

        print("✅ Services stopped")
        sys.exit(0)

    def check_timeout(self):
        """Check if the application has exceeded the shutdown timeout."""
        if self.start_time and self.shutdown_timeout:
            elapsed = time.time() - self.start_time
            if elapsed > self.shutdown_timeout:
                timeout_msg = (
                    f"\n⏰ Timeout reached ({self.shutdown_timeout}s). "
                    f"Shutting down..."
                )
                print(timeout_msg)
                self.signal_handler(signal.SIGTERM, None)

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
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, self.signal_handler)

        print("\n📋 Starting application services...")
        print("   Press Ctrl+C to stop\n")

        self.start_time = time.time()

        # Start FastAPI in background thread
        fastapi_thread = threading.Thread(target=self.run_fastapi, daemon=True)
        fastapi_thread.start()

        # Wait for FastAPI to be ready
        if not self.wait_for_service(
            "http://localhost:8000/docs", "FastAPI", max_retries=20
        ):
            print("❌ FastAPI failed to start. Exiting...")
            self.signal_handler(signal.SIGTERM, None)
            return

        # Start Streamlit in background thread
        streamlit_thread = threading.Thread(
            target=self.run_streamlit, daemon=True
        )
        streamlit_thread.start()

        # Wait for Streamlit to be ready
        if not self.wait_for_service(
            "http://localhost:8501", "Streamlit", max_retries=30
        ):
            print("❌ Streamlit failed to start. Exiting...")
            self.signal_handler(signal.SIGTERM, None)
            return

        # Launch browser after both services are confirmed ready
        browser_thread = threading.Thread(
            target=self.launch_browser,
            args=("http://localhost:8501",),
            daemon=True,
        )
        browser_thread.start()

        print("\n" + "=" * 70)
        print("✅ All services are running!")
        print("=" * 70)
        print("   FastAPI:   http://localhost:8000")
        print("   Streamlit: http://localhost:8501")
        print("   Press Ctrl+C to stop all services")
        print("=" * 70 + "\n")

        # Keep main thread alive and check for timeout
        try:
            while self.running:
                time.sleep(1)
                self.check_timeout()
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)


if __name__ == "__main__":
    launcher = ApplicationLauncher()
    launcher.run()
