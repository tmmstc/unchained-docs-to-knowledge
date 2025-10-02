# Scripts Directory

This directory contains utility scripts for testing, setup, and development of the PDF OCR Processing Application.

## Cross-Platform Compatibility

All scripts have been updated to work across Windows, Linux, and macOS using:
- `pathlib.Path` for cross-platform path handling
- `sys.platform` checks for platform-specific logic
- `python3` shebang for POSIX systems
- Proper virtual environment detection for both Windows (Scripts) and POSIX (bin)

## Development Scripts

### start_dev.py
**Cross-platform development server launcher (Pure Python)**
```bash
# Works on all platforms
python scripts/start_dev.py
```
This script:
- Creates virtual environment if missing
- Installs/upgrades dependencies
- Runs the main `run.py` launcher

### start-dev.sh
**POSIX shell script (Linux/macOS)**
```bash
bash scripts/start-dev.sh
# or
./scripts/start-dev.sh
```

### start-dev.bat
**Windows batch script**
```cmd
scripts\start-dev.bat
```

## Testing Scripts

### check_summarizer.py
Verifies that the summarizer module can be imported correctly.
```bash
python scripts/check_summarizer.py
```

### create_test_db.py
Creates a test database with sample records for UI testing.
```bash
python scripts/create_test_db.py
```

### test_backend.py
Tests backend imports and database initialization.
```bash
python scripts/test_backend.py
```

### test_connectivity.py
Tests connection to the FastAPI backend (requires backend to be running).
```bash
python scripts/test_connectivity.py
```

### test_simple_fastapi.py
Minimal test to verify FastAPI can start.
```bash
python scripts/test_simple_fastapi.py
```

### test_simple_server.py
Runs a simple HTTP server for basic connectivity testing.
```bash
python scripts/test_simple_server.py
```

## UI Testing Scripts

### test_streamlit_layout.py
Tests Streamlit UI layout and component rendering.
```bash
streamlit run scripts/test_streamlit_layout.py
```

### test_streamlit_summarize_controls.py
Verifies summarization controls are present in the Streamlit app.
```bash
python scripts/test_streamlit_summarize_controls.py
```

### test_ui_components.py
Comprehensive test of Streamlit UI components and structure.
```bash
python scripts/test_ui_components.py
```

### ui_inspection_checklist.py
Detailed analysis of streamlit_app.py for rendering issues.
```bash
python scripts/ui_inspection_checklist.py
```

## Notes

- All Python scripts use `#!/usr/bin/env python3` shebang for POSIX compatibility
- Path handling uses `pathlib.Path` for cross-platform support
- Virtual environment detection works for both Windows (`venv/Scripts`) and POSIX (`venv/bin`)
- Scripts that require a running backend will fail gracefully with helpful error messages
