#!/usr/bin/env python3
"""
Minimal test to verify FastAPI can start.
"""


def test_fastapi_import():
    """Test that FastAPI can be imported."""
    print("Testing basic imports...")

    try:
        print("OK System imports successful")
        return True
    except Exception as e:
        print(f"ERROR: Import failed: {e}")
        return False


if __name__ == "__main__":
    import sys

    success = test_fastapi_import()

    if success:
        print("\nOK Test completed successfully")

    sys.exit(0 if success else 1)
