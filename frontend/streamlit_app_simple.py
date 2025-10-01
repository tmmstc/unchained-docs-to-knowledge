#!/usr/bin/env python3
"""
Simple Streamlit app for PDF OCR processing with minimal dependencies.
"""

import sys
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# FastAPI backend configuration
BACKEND_URL = "http://localhost:8000"


def main():
    """Simple console-based interface to test the backend."""
    logger.info("Simple PDF OCR client starting up")
    logger.info(f"Backend URL: {BACKEND_URL}")

    # Test backend connection
    print("Testing backend connection...")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if response.status_code == 200:
            print("OK Backend API is running")
            data = response.json()
            print(
                f"  Message: {data.get('message', 'N/A')}"
            )
            print(f"  Version: {data.get('version', 'N/A')}")
        else:
            print(f"ERROR Backend API returned status {response.status_code}")
            return
    except Exception as e:
        print(f"ERROR Cannot connect to backend API: {e}")
        print(
            "Please ensure FastAPI backend is running on "
            "http://localhost:8000"
        )
        return

    # Get stats from backend
    print("\nGetting database statistics...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/stats", timeout=10
        )
        response.raise_for_status()
        stats = response.json()
        print("Database Statistics:")
        print(f"  Total Records: {stats.get('total_records', 0)}")
        print(f"  Total Words: {stats.get('total_words', 0)}")
        print(f"  Total Characters: {stats.get('total_characters', 0)}")
    except Exception as e:
        print(f"ERROR Error fetching statistics: {e}")

    # Get recent records
    print("\nGetting recent records...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/records",
            params={"limit": 5},
            timeout=10,
        )
        response.raise_for_status()
        records = response.json()
        print(f"Recent Records ({len(records)}):")
        for record in records:
            print(
                f"  - {record['filename']} "
                f"({record['created_timestamp']})"
            )
            print(
                f"    Words: {record['word_count']}, "
                f"Characters: {record['character_length']}"
            )
    except Exception as e:
        print(f"ERROR Error fetching records: {e}")

    print("\nOK Simple client test completed")


if __name__ == "__main__":
    main()
