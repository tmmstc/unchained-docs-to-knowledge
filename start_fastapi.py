#!/usr/bin/env python3
"""
Simple script to start just the FastAPI server for testing.
"""

import subprocess
import sys
import logging
from pathlib import Path

# Configure logging for startup script
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def main():
    """Start FastAPI server."""
    logger.info("🚀 Initializing FastAPI backend startup")
    logger.info("Target URL: http://localhost:8000")
    logger.info("Host: 127.0.0.1")
    logger.info("Port: 8000")
    logger.info("Reload mode: enabled")

    venv_python = Path("venv/Scripts/python.exe")
    if not venv_python.exists():
        logger.error("❌ Virtual environment not found at: %s", venv_python)
        logger.error("Please run: py -m venv venv")
        return 1

    logger.info("✅ Virtual environment found at: %s", venv_python)

    try:
        logger.info("📡 Starting uvicorn server...")
        # Start FastAPI server
        subprocess.run(
            [
                str(venv_python),
                "-m",
                "uvicorn",
                "app.main:app",
                "--reload",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error("❌ Error starting FastAPI: %s", e)
        return 1
    except KeyboardInterrupt:
        logger.info("\n🛑 FastAPI server stopped by user")
        return 0


if __name__ == "__main__":
    sys.exit(main())
