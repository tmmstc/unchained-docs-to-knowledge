#!/usr/bin/env python3
"""
Script to run both FastAPI backend and Streamlit frontend simultaneously.
Requires Python subprocess and threading.
"""

import subprocess
import threading
import time
import signal
import sys
import os
from pathlib import Path

class ServiceRunner:
    def __init__(self):
        self.processes = []
        self.running = True

    def run_fastapi(self):
        """Run FastAPI backend server"""
        try:
            print("🚀 Starting FastAPI backend on http://localhost:8000")
            venv_python = Path("venv/Scripts/python.exe")
            if not venv_python.exists():
                print("❌ Virtual environment not found. Run: py -m venv venv")
                return
            
            process = subprocess.Popen(
                [str(venv_python), "-m", "uvicorn", "app.main:app", "--reload"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            self.processes.append(process)
            
            # Stream output
            for line in process.stdout:
                if self.running:
                    print(f"[FastAPI] {line.strip()}")
                else:
                    break
                    
        except Exception as e:
            print(f"❌ Error starting FastAPI: {e}")

    def run_streamlit(self):
        """Run Streamlit frontend server"""
        try:
            # Wait a bit for FastAPI to start
            time.sleep(3)
            print("🎨 Starting Streamlit frontend on http://localhost:8501")
            
            venv_python = Path("venv/Scripts/python.exe")
            process = subprocess.Popen(
                [str(venv_python), "-m", "streamlit", "run", "streamlit_app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            self.processes.append(process)
            
            # Stream output
            for line in process.stdout:
                if self.running:
                    print(f"[Streamlit] {line.strip()}")
                else:
                    break
                    
        except Exception as e:
            print(f"❌ Error starting Streamlit: {e}")

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n🛑 Shutting down services...")
        self.running = False
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        
        print("✅ Services stopped")
        sys.exit(0)

    def run(self):
        """Start both services"""
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print("🌟 Starting FastAPI + Streamlit Development Environment")
        print("📝 Press Ctrl+C to stop both services\n")
        
        # Start FastAPI in background thread
        fastapi_thread = threading.Thread(target=self.run_fastapi, daemon=True)
        fastapi_thread.start()
        
        # Start Streamlit in background thread
        streamlit_thread = threading.Thread(target=self.run_streamlit, daemon=True)
        streamlit_thread.start()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    runner = ServiceRunner()
    runner.run()