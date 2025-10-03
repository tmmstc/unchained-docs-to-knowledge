@echo off
REM Test script for the packaged PDF OCR executable

echo ========================================================================
echo Testing PDF OCR Packaged Executable
echo ========================================================================
echo.

REM Check if executable exists
if not exist "dist\PDFOCRApp\PDFOCRApp.exe" (
    echo ERROR: Executable not found at dist\PDFOCRApp\PDFOCRApp.exe
    echo Please run build_exe.py first
    exit /b 1
)

echo Found executable: dist\PDFOCRApp\PDFOCRApp.exe
echo.

REM Check if required external dependencies are available
echo Checking for Tesseract OCR...
where tesseract >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Tesseract found in PATH
) else (
    echo [WARNING] Tesseract not found in PATH
    echo The application may fail when processing PDFs
)

echo.
echo Checking for Poppler...
where pdftoppm >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Poppler found in PATH
) else (
    echo [WARNING] Poppler not found in PATH  
    echo The application may fail when processing PDFs
)

echo.
echo ========================================================================
echo Executable is ready to test
echo ========================================================================
echo.
echo To manually test the executable:
echo   1. Open a command prompt
echo   2. Navigate to this directory
echo   3. Run: dist\PDFOCRApp\PDFOCRApp.exe
echo   4. Wait for the browser to open automatically
echo   5. Verify the Streamlit UI loads correctly
echo   6. Check that the backend API is accessible
echo.
echo Note: The first launch may take longer as files are extracted
echo ========================================================================
