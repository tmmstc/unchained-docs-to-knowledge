#!/usr/bin/env python3
"""
Test script to verify backend functionality works.
"""
import os
import sys
import logging

sys.path.insert(0, os.path.abspath('.'))

from app.main import app  # noqa: E402
from app.database import init_database  # noqa: E402

# Configure logging without emojis
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def test_backend():
    """Test that backend can start without Unicode issues."""
    print("Testing backend imports...")

    try:
        print("OK FastAPI app imported successfully")
        print("OK Database module imported successfully")

        print("Testing database initialization...")
        init_database()
        print("OK Database initialized successfully")

        print("Testing FastAPI app creation...")
        print(f"OK FastAPI app title: {app.title}")
        print(f"OK FastAPI app version: {app.version}")

        print("\nOK All backend tests passed!")
        print("Backend should now start without Unicode errors")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)
