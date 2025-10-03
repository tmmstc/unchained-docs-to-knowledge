#!/usr/bin/env python3
"""
Streamlit app for PDF OCR processing with directory input and FastAPI backend.
Main entry point with navigation and statistics dashboard.
"""

import sys
import os
import traceback
import logging
from datetime import datetime
from pathlib import Path

print("=" * 80)
print("STREAMLIT APP STARTUP INITIATED")
print("=" * 80)
print(f"Timestamp: {datetime.now().isoformat()}")
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")
print(f"Working Directory: {os.getcwd()}")
print(f"Script Path: {__file__}")
print("=" * 80)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("streamlit_startup.log", mode="a"),
    ],
)

logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("INITIALIZATION: Configuring logging system")
logger.info("=" * 80)

logger.info("=" * 80)
logger.info("ENVIRONMENT VARIABLES - Deployment Configuration")
logger.info("=" * 80)

env_vars_to_log = [
    "OPENAI_API_BASE_URL",
    "SUMMARIZATION_MODEL",
    "DATABASE_URL",
    "BACKEND_URL",
    "HOST",
    "PORT",
    "STREAMLIT_SERVER_PORT",
    "STREAMLIT_SERVER_ADDRESS",
    "STREAMLIT_SERVER_HEADLESS",
    "PATH",
    "PYTHONPATH",
    "HOME",
    "USER",
    "VIRTUAL_ENV",
]

for var in env_vars_to_log:
    value = os.environ.get(var)
    if value:
        if "KEY" in var or "SECRET" in var or "TOKEN" in var or "PASSWORD" in var:
            masked_value = value[:4] + "****" + value[-4:] if len(value) > 8 else "****"
            logger.info(f"ENV: {var} = {masked_value} (masked)")
        else:
            logger.info(f"ENV: {var} = {value}")
    else:
        logger.info(f"ENV: {var} = <not set>")

logger.info("=" * 80)

OPENAI_API_KEY_SET = bool(os.environ.get("OPENAI_API_KEY"))
logger.info(
    f"Security Check - OPENAI_API_KEY is {'SET' if OPENAI_API_KEY_SET else 'NOT SET'}"
)

logger.info("=" * 80)
logger.info("IMPORTING: Core dependencies")
logger.info("=" * 80)

try:
    logger.info("Importing streamlit...")
    import streamlit as st

    logger.info(f"✓ streamlit imported successfully (version: {st.__version__})")
except ImportError as e:
    logger.error(f"✗ CRITICAL: Failed to import streamlit: {e}")
    logger.error(traceback.format_exc())
    print(f"\n{'=' * 80}")
    print("CRITICAL ERROR: Failed to import streamlit")
    print(f"{'=' * 80}")
    print(traceback.format_exc())
    sys.exit(1)
except Exception as e:
    logger.error(f"✗ CRITICAL: Unexpected error importing streamlit: {e}")
    logger.error(traceback.format_exc())
    print(f"\n{'=' * 80}")
    print("CRITICAL ERROR: Unexpected error importing streamlit")
    print(f"{'=' * 80}")
    print(traceback.format_exc())
    sys.exit(1)

try:
    logger.info("Importing frontend.api_client...")
    from frontend.api_client import get_stats_from_backend

    logger.info("✓ frontend.api_client imported successfully")
except ImportError as e:
    logger.error(f"✗ CRITICAL: Failed to import frontend.api_client: {e}")
    logger.error(traceback.format_exc())
    print(f"\n{'=' * 80}")
    print("CRITICAL ERROR: Failed to import frontend.api_client")
    print(f"{'=' * 80}")
    print(traceback.format_exc())
    sys.exit(1)
except Exception as e:
    logger.error(f"✗ CRITICAL: Unexpected error importing frontend.api_client: {e}")
    logger.error(traceback.format_exc())
    print(f"\n{'=' * 80}")
    print("CRITICAL ERROR: Unexpected error importing frontend.api_client")
    print(f"{'=' * 80}")
    print(traceback.format_exc())
    sys.exit(1)

logger.info("=" * 80)
logger.info("CONFIGURATION: Setting up application constants")
logger.info("=" * 80)

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
logger.info(f"Backend URL configured: {BACKEND_URL}")

logger.info("=" * 80)
logger.info("HEALTH CHECK: Testing backend connectivity")
logger.info("=" * 80)


def check_backend_health():
    """Check if the FastAPI backend is reachable."""
    import requests

    logger.info(f"Health check initiated at {datetime.now().isoformat()}")
    logger.info(f"Target URL: {BACKEND_URL}")

    try:
        logger.info(f"Attempting connection to {BACKEND_URL}/health...")
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)

        logger.info(f"Health check response - Status Code: {response.status_code}")
        logger.info(f"Health check response - Headers: {dict(response.headers)}")
        logger.info(f"Health check response - Body: {response.text}")

        if response.status_code == 200:
            logger.info("✓ Backend health check PASSED")
            return True
        else:
            logger.warning(
                f"✗ Backend health check returned non-200 status: {response.status_code}"
            )
            return False

    except requests.exceptions.ConnectionError as e:
        logger.error(f"✗ Backend health check FAILED - Connection Error: {e}")
        logger.error(f"Could not connect to {BACKEND_URL}")
        logger.error("This may indicate the backend is not running or unreachable")
        return False
    except requests.exceptions.Timeout as e:
        logger.error(f"✗ Backend health check FAILED - Timeout: {e}")
        logger.error(f"Backend at {BACKEND_URL} did not respond within timeout")
        return False
    except Exception as e:
        logger.error(f"✗ Backend health check FAILED - Unexpected error: {e}")
        logger.error(traceback.format_exc())
        return False


try:
    backend_healthy = check_backend_health()
    logger.info(
        f"Backend health status: {'HEALTHY' if backend_healthy else 'UNHEALTHY'}"
    )
except Exception as e:
    logger.error(f"Error during health check: {e}")
    logger.error(traceback.format_exc())
    backend_healthy = False

logger.info("=" * 80)
logger.info("DATABASE: Checking database connectivity")
logger.info("=" * 80)

try:
    logger.info(
        "Attempting to fetch statistics from backend (tests database connectivity)..."
    )
    test_stats = get_stats_from_backend()
    logger.info(f"✓ Database connectivity verified - Stats: {test_stats}")
except Exception as e:
    logger.error(f"✗ Database connectivity check failed: {e}")
    logger.error(traceback.format_exc())

logger.info("=" * 80)
logger.info("PAGE DISCOVERY: Scanning multipage app structure")
logger.info("=" * 80)

pages_dir = Path(__file__).parent / "pages"
logger.info(f"Pages directory: {pages_dir}")
logger.info(f"Pages directory exists: {pages_dir.exists()}")

if pages_dir.exists():
    page_files = list(pages_dir.glob("*.py"))
    logger.info(f"Found {len(page_files)} page module(s):")
    for page_file in sorted(page_files):
        logger.info(f"  - {page_file.name}")
else:
    logger.warning("Pages directory not found!")

logger.info("=" * 80)
logger.info("STARTUP COMPLETE: Application ready")
logger.info("=" * 80)
logger.info("Application: PDF OCR Processor")
logger.info("Entry Point: streamlit_app.py (Main Dashboard)")
logger.info(f"Backend Integration: {BACKEND_URL}")
logger.info(f"Backend Status: {'CONNECTED' if backend_healthy else 'DISCONNECTED'}")
logger.info("=" * 80)

print("\n" + "=" * 80)
print("📄 PDF OCR PROCESSOR - STREAMLIT FRONTEND")
print("=" * 80)
print(f"✓ Startup timestamp: {datetime.now().isoformat()}")
print(f"✓ Entry point: streamlit_app.py (Main Dashboard)")
print(f"✓ Backend URL: {BACKEND_URL}")
print(f"✓ Backend health: {'CONNECTED ✓' if backend_healthy else 'DISCONNECTED ✗'}")
print(f"✓ Streamlit version: {st.__version__}")
print(f"✓ Python version: {sys.version.split()[0]}")
print(f"✓ Pages discovered: {len(page_files) if pages_dir.exists() else 0}")
print("=" * 80)
print()


def main():
    """Main application entry point with comprehensive error handling."""
    try:
        logger.info("Executing main() function")

        logger.info("Setting page configuration...")
        st.set_page_config(
            page_title="PDF OCR Processor",
            page_icon="📄",
            layout="wide",
        )
        logger.info("✓ Page configuration set successfully")

        logger.info("Rendering page title and header...")
        st.title("📄 PDF OCR Processor")
        st.markdown("Process PDF files with OCR and store results in a database")
        st.markdown("---")

        logger.info("Rendering dashboard statistics section...")
        st.subheader("📈 Dashboard Statistics")

        logger.info("Fetching statistics from backend...")
        stats = get_stats_from_backend()
        logger.info(f"Statistics retrieved: {stats}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", stats.get("total_records", 0))
        with col2:
            st.metric("Total Words", f"{stats.get('total_words', 0):,}")
        with col3:
            st.metric("Total Characters", f"{stats.get('total_characters', 0):,}")

        st.markdown("---")

        logger.info("Rendering navigation section...")
        st.markdown("### Navigation")
        st.markdown("Use the sidebar to navigate between pages:")
        st.markdown(
            "- **📤 Ingest Documents**: Upload or process PDF files from a folder"
        )
        st.markdown(
            "- **📊 View Database**: Browse, search, and manage processed documents"
        )

        logger.info("✓ Main page rendered successfully")

    except Exception as e:
        logger.error(f"✗ CRITICAL ERROR in main() function: {e}")
        logger.error(traceback.format_exc())

        st.error("⚠️ Application Error")
        st.error(f"An error occurred while loading the application: {str(e)}")

        with st.expander("View Error Details", expanded=True):
            st.code(traceback.format_exc())

        st.warning(
            "Please check the logs for more details and contact support if the issue persists."
        )


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("EXECUTION: Running main() function")
    logger.info("=" * 80)

    try:
        main()
    except Exception as e:
        logger.error("=" * 80)
        logger.error("FATAL ERROR: Uncaught exception in __main__")
        logger.error("=" * 80)
        logger.error(f"Error: {e}")
        logger.error(traceback.format_exc())

        print("\n" + "=" * 80)
        print("FATAL ERROR")
        print("=" * 80)
        print(traceback.format_exc())
        print("=" * 80)

        raise
