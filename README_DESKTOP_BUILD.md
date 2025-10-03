# Building Desktop Application (EXE) - Quick Start

This guide shows how to convert the PDF OCR Streamlit application into a standalone Windows desktop executable.

## Quick Build Steps

### 1. Ensure Dependencies are Installed

```powershell
.\venv\Scripts\activate
python -m pip install -r requirements.txt
```

This will install PyInstaller and Streamlit (newly added to requirements.txt).

### 2. Run the Build Script

```powershell
python build_exe.py
```

The script will:
- Bundle the entire application into a single EXE
- Include all Python dependencies
- Package the Streamlit frontend and FastAPI backend
- Create `dist/PDFOCRApp.exe`

### 3. Test the Executable

```powershell
.\dist\PDFOCRApp.exe
```

The application will:
- Start FastAPI backend on http://127.0.0.1:8000
- Launch Streamlit frontend on http://127.0.0.1:8501
- Automatically open your browser to the application

## What Was Created

### New Files

1. **`desktop_app.py`** - Desktop launcher script that:
   - Starts FastAPI backend in a background thread
   - Launches Streamlit frontend
   - Opens the browser automatically
   - Manages both services

2. **`build_exe.py`** - PyInstaller build script that:
   - Configures PyInstaller with all necessary options
   - Bundles Streamlit, FastAPI, and dependencies
   - Creates a single executable file
   - Includes hidden imports for all required packages

3. **`BUILD_EXE.md`** - Comprehensive documentation covering:
   - Detailed build instructions
   - Troubleshooting common issues
   - Deployment guidelines
   - Customization options

4. **`README_DESKTOP_BUILD.md`** - This quick-start guide

### Updated Files

- **`requirements.txt`** - Added `streamlit` and `pyinstaller`
- **`.gitignore`** - Added `*.spec` to ignore PyInstaller spec files

## Important Notes

### External Dependencies

The EXE bundles Python and all packages, but you still need:

1. **Tesseract OCR** - Must be installed on any machine running the EXE
   - Download: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location: `C:\Program Files\Tesseract-OCR\`

2. **Poppler** - Required for PDF to image conversion
   - Ensure it's available in the system PATH or app directory

### File Size

The resulting EXE will be large (100+ MB) because it includes:
- Python interpreter
- All libraries (Streamlit, FastAPI, PIL, NumPy, etc.)
- Application code

### Performance

- First launch may be slow as PyInstaller extracts files to a temp directory
- Subsequent launches will be faster
- For better startup performance, consider using `--onedir` instead of `--onefile`

## Debugging

If the EXE doesn't work:

1. Run it from command line to see errors:
   ```powershell
   .\dist\PDFOCRApp.exe
   ```

2. Edit `build_exe.py` and comment out the `'--windowed',` line to show console output

3. Rebuild:
   ```powershell
   python build_exe.py
   ```

## Advanced: Manual PyInstaller

For more control, run PyInstaller directly:

```powershell
pyinstaller desktop_app.py `
  --name=PDFOCRApp `
  --onefile `
  --windowed `
  --add-data="frontend;frontend" `
  --add-data="app;app" `
  --add-data="shared;shared" `
  --hidden-import=streamlit `
  --hidden-import=uvicorn `
  --collect-all=streamlit `
  --noconfirm
```

## Distribution

To share the application:

1. Copy `dist/PDFOCRApp.exe` to the target system
2. Ensure Tesseract OCR is installed
3. Include any required `.env` configuration files
4. Provide instructions for first-time setup

## See Also

- **BUILD_EXE.md** - Full documentation with troubleshooting
- **AGENTS.md** - Development commands and architecture
- **README.md** - General application documentation
