"""
Build script to create standalone executable using PyInstaller.
Run this script to build the desktop application EXE.
"""

import PyInstaller.__main__
from pathlib import Path


def build_exe():
    """Build the executable using PyInstaller."""

    # Get the site-packages path for streamlit
    import streamlit

    streamlit_path = Path(streamlit.__file__).parent

    args = [
        "desktop_app.py",
        "--name=PDFOCRApp",
        "--onefile",
        "--windowed",
        "--icon=NONE",
        f"--add-data={streamlit_path};streamlit",
        "--add-data=frontend;frontend",
        "--add-data=app;app",
        "--add-data=.streamlit;.streamlit",
        "--hidden-import=streamlit",
        "--hidden-import=streamlit.web.cli",
        "--hidden-import=streamlit.runtime",
        "--hidden-import=streamlit.runtime.scriptrunner",
        "--hidden-import=uvicorn",
        "--hidden-import=fastapi",
        "--hidden-import=pytesseract",
        "--hidden-import=pdf2image",
        "--hidden-import=pydantic",
        "--hidden-import=PIL",
        "--hidden-import=PIL._imaging",
        "--collect-all=streamlit",
        "--collect-all=altair",
        "--collect-all=plotly",
        "--collect-all=pyarrow",
        "--noconfirm",
    ]

    print("Building executable...")
    print(f"Arguments: {' '.join(args)}")

    PyInstaller.__main__.run(args)

    print("\n" + "=" * 70)
    print("Build complete!")
    print("=" * 70)
    print("\nExecutable location: dist/PDFOCRApp.exe")
    print("\nIMPORTANT: Tesseract OCR must be installed on target system!")
    print("Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("\nAlso ensure Poppler is available for PDF processing.")
    print("=" * 70)


if __name__ == "__main__":
    build_exe()
