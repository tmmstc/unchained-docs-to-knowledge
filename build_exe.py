"""
Build script to create standalone executable using PyInstaller.
Run this script to build the desktop application EXE.
"""

import PyInstaller.__main__
import sys
import os


def build_exe():
    """Build the executable using PyInstaller."""

    print("=" * 70)
    print("PyInstaller Build Script for PDF OCR Desktop Application")
    print("=" * 70)

    # Verify we're in a virtual environment
    if not hasattr(sys, "real_prefix") and not (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("\nWARNING: Not running in a virtual environment!")
        print("It's recommended to build from within the venv.")

    print(f"\nPython: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")

    args = [
        "desktop_app.py",
        "--name=PDFOCRApp",
        "--onedir",  # Use onedir for easier debugging and faster startup
        "--console",  # Show console for debugging
        "--icon=NONE",
        # Add application directories
        "--add-data=frontend;frontend",
        "--add-data=app;app",
        "--add-data=.streamlit;.streamlit",
        "--add-data=.env.example;.",
        # Core hidden imports
        "--hidden-import=streamlit",
        "--hidden-import=streamlit.web.cli",
        "--hidden-import=streamlit.web.bootstrap",
        "--hidden-import=streamlit.runtime",
        "--hidden-import=streamlit.runtime.scriptrunner",
        "--hidden-import=streamlit.runtime.scriptrunner.script_runner",
        "--hidden-import=streamlit.runtime.state",
        "--hidden-import=streamlit.runtime.state.session_state",
        # Uvicorn and FastAPI
        "--hidden-import=uvicorn",
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.protocols",
        "--hidden-import=uvicorn.protocols.http",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.protocols.websockets",
        "--hidden-import=uvicorn.protocols.websockets.auto",
        "--hidden-import=uvicorn.lifespan",
        "--hidden-import=uvicorn.lifespan.on",
        "--hidden-import=fastapi",
        "--hidden-import=starlette",
        "--hidden-import=starlette.middleware",
        "--hidden-import=starlette.middleware.cors",
        # PDF and OCR
        "--hidden-import=pytesseract",
        "--hidden-import=pdf2image",
        "--hidden-import=PIL",
        "--hidden-import=PIL._imaging",
        "--hidden-import=PIL.Image",
        # Data handling
        "--hidden-import=pydantic",
        "--hidden-import=pydantic_core",
        "--hidden-import=sqlite3",
        # HTTP clients
        "--hidden-import=requests",
        "--hidden-import=httpx",
        "--hidden-import=urllib3",
        # Environment and utilities
        "--hidden-import=dotenv",
        "--hidden-import=openai",
        # Collect all required packages
        "--collect-all=streamlit",
        "--collect-all=tornado",
        "--collect-all=watchdog",
        # Copy metadata for packages that need it
        "--copy-metadata=streamlit",
        "--copy-metadata=pydantic",
        "--copy-metadata=pydantic_core",
        # Build options
        "--noconfirm",
        "--clean",
    ]

    print("\n" + "=" * 70)
    print("Starting PyInstaller build...")
    print("=" * 70)
    print("\nBuild mode: --onedir (directory with executable + dependencies)")
    print("Console: enabled (for debugging)")

    try:
        PyInstaller.__main__.run(args)

        print("\n" + "=" * 70)
        print("BUILD COMPLETE!")
        print("=" * 70)
        print("\nExecutable location: dist/PDFOCRApp/PDFOCRApp.exe")
        print("\n" + "=" * 70)
        print("IMPORTANT NOTES:")
        print("=" * 70)
        print("1. Tesseract OCR must be installed on the target system")
        print("   Download: https://github.com/UB-Mannheim/tesseract/wiki")
        print("\n2. Poppler must be available for PDF processing")
        print("\n3. The first run will create pdf_ocr_database.db in the app directory")
        print("\n4. To create a single-file EXE, change --onedir to --onefile")
        print("   (but note: --onefile is slower to start)")
        print("\n5. To test the executable, run: dist\\PDFOCRApp\\PDFOCRApp.exe")
        print("=" * 70)

        return True

    except Exception as e:
        print("\n" + "=" * 70)
        print("BUILD FAILED!")
        print("=" * 70)
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
        print("\n" + "=" * 70)
        print("TROUBLESHOOTING:")
        print("=" * 70)
        print(
            "1. Ensure all dependencies are installed: pip install -r requirements.txt"
        )
        print("2. Check that you're in the virtual environment")
        print("3. Try deleting build/ and dist/ directories and rebuilding")
        print("=" * 70)
        return False


if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
