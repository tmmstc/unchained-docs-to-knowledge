# Building Streamlit Desktop Application as EXE

This guide explains how to convert the Streamlit PDF OCR application into a standalone Windows executable.

## Prerequisites

1. **Python Environment**: Ensure your virtual environment is set up and activated
   ```bash
   .\venv\Scripts\activate
   ```

2. **Install Dependencies**: Make sure all required packages are installed
   ```bash
   python -m pip install -r requirements.txt
   ```

3. **External Tools**: The application requires:
   - **Tesseract OCR** - Must be installed on the target system
     - Download: https://github.com/UB-Mannheim/tesseract/wiki
     - Default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - **Poppler** - For PDF to image conversion
     - Can be bundled or installed separately

## Building the EXE

### Method 1: Using the Build Script (Recommended)

Simply run the provided build script:

```bash
python build_exe.py
```

This will:
- Create a single executable file using PyInstaller
- Bundle all necessary Python dependencies
- Include the Streamlit frontend and FastAPI backend
- Output the EXE to `dist/PDFOCRApp.exe`

### Method 2: Manual PyInstaller Command

If you need more control, you can run PyInstaller directly:

```bash
pyinstaller desktop_app.py ^
  --name=PDFOCRApp ^
  --onefile ^
  --windowed ^
  --add-data=frontend;frontend ^
  --add-data=app;app ^
  --add-data=shared;shared ^
  --add-data=.streamlit;.streamlit ^
  --hidden-import=streamlit ^
  --hidden-import=streamlit.web.cli ^
  --hidden-import=uvicorn ^
  --hidden-import=fastapi ^
  --hidden-import=pytesseract ^
  --hidden-import=pdf2image ^
  --collect-all=streamlit ^
  --noconfirm
```

## Build Outputs

After building, you'll find:
- `dist/PDFOCRApp.exe` - The standalone executable
- `build/` - Temporary build files (can be deleted)
- `PDFOCRApp.spec` - PyInstaller specification file (can be customized)

## Running the Application

1. Double-click `PDFOCRApp.exe` or run from command line:
   ```bash
   .\dist\PDFOCRApp.exe
   ```

2. The application will:
   - Start the FastAPI backend on port 8000
   - Launch Streamlit frontend on port 8501
   - Automatically open your default browser to the Streamlit UI

## Troubleshooting

### Common Issues

1. **"Tesseract not found" error**
   - Ensure Tesseract is installed on the system
   - Set the `TESSERACT_PATH` environment variable if installed in a non-standard location

2. **Import errors**
   - Add missing imports to the `--hidden-import` flags in `build_exe.py`
   - Use `--collect-all=package_name` for packages that need all their files

3. **Application doesn't start**
   - Run without `--windowed` flag to see console output for debugging
   - Edit `build_exe.py` and comment out the `'--windowed',` line

4. **Large EXE size**
   - The EXE will be large (100+ MB) due to bundled Python and all dependencies
   - Consider using `--onedir` instead of `--onefile` for faster startup

### Debugging

For debugging, modify `build_exe.py` to remove the `--windowed` flag:

```python
# Comment out this line in build_exe.py:
# '--windowed',
```

This will show a console window with error messages.

## Deployment

To distribute the application:

1. **Include in installer/package**:
   - The EXE file (`PDFOCRApp.exe`)
   - Installation instructions for Tesseract OCR
   - Any required `.env` configuration files

2. **System Requirements Document**:
   - Windows 10 or later
   - Tesseract OCR installed
   - Poppler binaries (if not bundled)
   - Internet connection (if using OpenAI API)

3. **Optional: Create Windows Installer**
   - Use tools like Inno Setup or NSIS to create a proper installer
   - Include Tesseract and Poppler in the installer
   - Set up desktop shortcuts and start menu entries

## Customization

### Adding an Icon

1. Create or obtain a `.ico` file
2. Update `build_exe.py`:
   ```python
   '--icon=path/to/your/icon.ico',
   ```

### Changing Application Name

Edit `build_exe.py` and change the `--name` parameter:
```python
'--name=YourAppName',
```

### Bundle Additional Files

Add more data files to the bundle:
```python
'--add-data=path/to/source;path/in/bundle',
```

## Performance Considerations

- **First Launch**: The EXE will be slower on first launch as it extracts to a temp directory
- **OneDIR vs OneFile**: 
  - `--onefile`: Single EXE, slower startup
  - `--onedir`: Folder with EXE and DLLs, faster startup but more files to distribute

## Alternative: Using PyInstaller Spec File

After first build, edit `PDFOCRApp.spec` for more advanced configuration:

```bash
pyinstaller PDFOCRApp.spec
```

This allows fine-grained control over the build process.
