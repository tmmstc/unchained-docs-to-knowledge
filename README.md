# PDF OCR Processing Application

A modular full-stack application for extracting text from PDF files using Tesseract OCR, featuring a Streamlit frontend, FastAPI backend, and organized package structure.

## Features

- **PDF Text Extraction**: Extract text from PDF files using Tesseract OCR
- **Batch Processing**: Process multiple PDF files from a directory
- **Database Storage**: Store extracted text with metrics in SQLite database
- **Web Interface**: User-friendly Streamlit frontend
- **REST API**: FastAPI backend with comprehensive endpoints
- **Text Metrics**: Calculate word count and character length
- **Real-time Processing**: Live progress tracking and error handling

## Architecture

The application follows a modular architecture with separate packages:

```
├── app/                 # FastAPI backend
│   ├── __init__.py
│   ├── main.py         # FastAPI application and routes
│   ├── database.py     # Database operations
│   └── models.py       # Pydantic models
├── frontend/           # Streamlit frontend
│   ├── __init__.py
│   └── streamlit_app.py
├── shared/             # Shared utilities
│   ├── __init__.py
│   └── pdf_processor.py # PDF processing and OCR logic
├── tests/              # Test suite
└── requirements.txt
```

## Requirements

- **Python 3.8+** (Recommended: Python 3.13)
- **Tesseract OCR** installed on system
- **Poppler** (for PDF to image conversion)
- **Virtual environment** (recommended)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd pdf-ocr-processing
```

### 2. System Dependencies

#### Install Tesseract OCR
**Windows:**
1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (recommended location: `C:\Program Files\Tesseract-OCR\`)
3. Add Tesseract to PATH:
   - Open System Properties → Advanced → Environment Variables
   - Add `C:\Program Files\Tesseract-OCR` to PATH
   - Restart Command Prompt/PowerShell

**Verify Tesseract installation:**
```bash
tesseract --version
```

#### Install Poppler (for PDF processing)
**Windows:**
1. Download Poppler for Windows: http://blog.alivate.com.au/poppler-windows/
2. Extract to `C:\Program Files\poppler-xx.xx.x`
3. Add `C:\Program Files\poppler-xx.xx.x\Library\bin` to PATH
4. Restart Command Prompt/PowerShell

**Verify Poppler installation:**
```bash
pdftoppm -h
```

### 3. Python Virtual Environment Setup
```bash
# Create virtual environment
py -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# For Git Bash on Windows
source venv/Scripts/activate

# Verify activation (should show venv path)
where python
```

### 4. Install Python Dependencies
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install project dependencies
python -m pip install -r requirements.txt
```

## Usage

### Quick Start - Run Both Services
```bash
# Activate virtual environment if not already active
.\venv\Scripts\activate

# Run both FastAPI backend and Streamlit frontend
python run_both.py
```

**Access the applications:**
- **Streamlit Frontend**: http://localhost:8501
- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Individual Services

**Start FastAPI backend only:**
```bash
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Start Streamlit frontend only:**
```bash
.\venv\Scripts\python.exe -m streamlit run frontend/streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```

## API Endpoints

- `GET /` - API status and health check
- `POST /process-pdf` - Store extracted PDF text and metrics
- `GET /records?limit=10` - Retrieve recent processing records
- `GET /stats` - Get database statistics

## Development

### Testing
```bash
.\venv\Scripts\python.exe -m pytest tests/ -v
```

### Code Quality
```bash
# Linting
.\venv\Scripts\python.exe -m flake8 app/ shared/ frontend/ tests/

# Code formatting
.\venv\Scripts\python.exe -m black app/ shared/ frontend/ tests/
```

---

## Windows-Specific Troubleshooting Guide

### 1. Python & Virtual Environment Issues

#### Problem: `py` command not found
**Solution:**
```bash
# Use python instead of py
python -m venv venv

# Or install Python from Microsoft Store
# Or add Python to PATH manually
```

#### Problem: Virtual environment activation fails
**Symptoms:**
- `.\venv\Scripts\activate` not working
- `cannot be loaded because running scripts is disabled`

**Solutions:**
```bash
# Method 1: Enable execution policy (Run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Method 2: Use alternative activation
.\venv\Scripts\Activate.ps1

# Method 3: Use full path
C:\path\to\your\project\venv\Scripts\python.exe

# Method 4: Git Bash users
source venv/Scripts/activate
```

#### Problem: Wrong Python version in virtual environment
**Verification:**
```bash
.\venv\Scripts\python.exe --version
where python
```

**Solution:**
```bash
# Delete and recreate with specific version
rmdir /s venv
py -3.13 -m venv venv
# or
python3.13 -m venv venv
```

### 2. PATH Configuration Issues

#### Problem: Commands not found after installation
**Common issues:**
- `tesseract --version` fails
- `pdftoppm -h` fails
- Services can't find dependencies

**Solution - Add to PATH:**
1. Press `Win + R`, type `sysdm.cpl`
2. Go to Advanced → Environment Variables
3. Edit System PATH, add:
   - `C:\Program Files\Tesseract-OCR`
   - `C:\Program Files\poppler-xx.xx.x\Library\bin`
   - Your Python installation path
4. **Restart all Command Prompt/PowerShell windows**
5. Verify:
```bash
tesseract --version
pdftoppm -h
python --version
```

### 3. Port Binding Issues

#### Problem: Port already in use
**Symptoms:**
- `Port 8000 is already in use`
- `Port 8501 is already in use`
- Services fail to start

**Solutions:**
```bash
# Check what's using the ports
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# Kill processes using the ports (replace PID)
taskkill /PID <process_id> /F

# Use different ports
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
streamlit run frontend/streamlit_app.py --server.port 8502
```

#### Problem: Services not accessible from browser
**Check binding:**
```bash
# Ensure services bind to correct interface
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
# NOT --host 0.0.0.0 which may be blocked
```

### 4. File Path Handling Issues

#### Problem: PDF file path errors
**Symptoms:**
- `FileNotFoundError` when processing PDFs
- Path separator issues (`/` vs `\`)

**Solutions:**
```python
# Always use forward slashes or Path objects
import os
pdf_path = r"C:\Users\Username\Documents\file.pdf"
# or
from pathlib import Path
pdf_path = Path("C:/Users/Username/Documents/file.pdf")
```

**Streamlit directory input tips:**
- Use forward slashes: `C:/Users/Username/Documents/PDFs`
- Avoid spaces in paths when possible
- Use raw strings: `r"C:\Users\Username\Documents\PDFs"`

### 5. Windows Firewall & Antivirus Issues

#### Problem: Development servers blocked
**Symptoms:**
- Services start but not accessible in browser
- Connection timeouts
- "Site can't be reached" errors

**Windows Firewall Solutions:**
1. **Allow through firewall:**
   ```bash
   # Run as Administrator
   netsh advfirewall firewall add rule name="Python Dev Server" dir=in action=allow protocol=TCP localport=8000
   netsh advfirewall firewall add rule name="Streamlit Dev Server" dir=in action=allow protocol=TCP localport=8501
   ```

2. **Manual firewall configuration:**
   - Open Windows Defender Firewall
   - Click "Allow an app through firewall"
   - Add Python.exe and allow both Public/Private networks

3. **Temporary disable (testing only):**
   ```bash
   # Run as Administrator - ONLY FOR TESTING
   netsh advfirewall set allprofiles state off
   # Remember to re-enable!
   netsh advfirewall set allprofiles state on
   ```

#### Problem: Antivirus blocking Python/servers
**Solutions:**
- Add project folder to antivirus exclusions
- Add Python executable to trusted applications
- Add venv folder to exclusions
- Temporarily disable real-time protection for testing

### 6. Service Connectivity Verification

#### Step-by-step connectivity check:

**1. Verify Python setup:**
```bash
# Check Python version and location
python --version
where python

# Check virtual environment
.\venv\Scripts\python.exe --version
.\venv\Scripts\pip list
```

**2. Check dependencies:**
```bash
# Verify Tesseract
tesseract --version

# Verify Poppler
pdftoppm -h

# Test Python imports
.\venv\Scripts\python.exe -c "import fastapi, streamlit, pytesseract, pdf2image; print('All imports successful')"
```

**3. Test services individually:**
```bash
# Start FastAPI and test
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
# In browser: http://127.0.0.1:8000
# Should see: {"message": "FastAPI backend is running"}

# Test API docs: http://127.0.0.1:8000/docs
```

```bash
# Start Streamlit (in new terminal)
.\venv\Scripts\python.exe -m streamlit run frontend/streamlit_app.py --server.port 8501
# In browser: http://localhost:8501
```

**4. Network connectivity test:**
```bash
# Test local network stack
ping 127.0.0.1
ping localhost

# Test if ports are listening
netstat -an | findstr :8000
netstat -an | findstr :8501

# Test HTTP connectivity
curl http://127.0.0.1:8000
# or use PowerShell
Invoke-WebRequest http://127.0.0.1:8000
```

### 7. Performance & Resource Issues

#### Problem: Slow PDF processing
**Solutions:**
- Close unnecessary applications
- Increase virtual memory/page file
- Process smaller batches
- Monitor Task Manager during processing

#### Problem: Out of memory errors
**Solutions:**
```bash
# Monitor memory usage
tasklist /fi "imagename eq python.exe"

# Process files individually instead of batch
# Increase system virtual memory
```

### 8. Database Issues

#### Problem: SQLite permission errors
**Solutions:**
```bash
# Ensure database directory is writable
# Check if file is locked by another process
# Run as Administrator if necessary

# Reset database
del pdf_ocr_database.db
```

### 9. Common Error Messages and Solutions

| Error | Solution |
|-------|----------|
| `'py' is not recognized` | Install Python from python.org or Microsoft Store |
| `execution of scripts is disabled` | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `Port 8000 is already in use` | Kill process: `taskkill /PID <pid> /F` or use different port |
| `tesseract is not installed` | Install Tesseract and add to PATH |
| `No module named 'streamlit'` | Activate venv and run `pip install -r requirements.txt` |
| `Connection refused` | Check firewall settings and port binding |
| `Permission denied` | Run as Administrator or check file permissions |

### 10. Verification Checklist

Before starting development, verify:

- [ ] Python 3.8+ installed and in PATH
- [ ] Virtual environment created and activated
- [ ] All pip packages installed successfully
- [ ] Tesseract OCR installed and in PATH
- [ ] Poppler installed and in PATH  
- [ ] Ports 8000 and 8501 are available
- [ ] Windows Firewall allows Python/dev servers
- [ ] Project directory has write permissions
- [ ] Can import all required Python modules

**Quick verification script:**
```bash
python test_connectivity.py
```

This will test all components and report any issues.

---

## License

MIT License