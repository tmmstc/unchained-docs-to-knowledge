# Cross-Platform Scripts Migration

This document describes the cross-platform improvements made to all utility scripts in the `scripts/` directory.

## Overview

All utility scripts have been updated to work seamlessly across Windows, Linux, and macOS using Python's built-in cross-platform capabilities.

## Key Changes

### 1. Path Handling with `pathlib.Path`

**Before (Windows-specific):**
```python
import os
file_path = os.path.join(script_dir, "..", "frontend", "streamlit_app.py")
```

**After (Cross-platform):**
```python
from pathlib import Path
file_path = Path(__file__).parent.parent / "frontend" / "streamlit_app.py"
```

### 2. Virtual Environment Detection

**Before (Windows-only):**
```python
venv_python = os.path.join("venv", "Scripts", "python.exe")
```

**After (Cross-platform):**
```python
import sys
from pathlib import Path

venv_dir = Path("venv")
if sys.platform == "win32":
    venv_python = venv_dir / "Scripts" / "python.exe"
else:
    venv_python = venv_dir / "bin" / "python"
```

### 3. Python Shebang

All Python scripts now include the standard cross-platform shebang:
```python
#!/usr/bin/env python3
```

This allows scripts to be executed directly on POSIX systems:
```bash
./scripts/test_backend.py  # Works on Linux/macOS
```

### 4. Import Path Construction

**Before:**
```python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

**After:**
```python
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))
```

## Updated Scripts

### Development Launchers

1. **start_dev.py** (NEW)
   - Pure Python launcher that works on all platforms
   - Detects and creates virtual environment
   - Installs dependencies
   - Launches application
   - Usage: `python scripts/start_dev.py`

2. **start-dev.sh**
   - Bash script for POSIX systems (unchanged)
   - Usage: `bash scripts/start-dev.sh` or `./scripts/start-dev.sh`

3. **start-dev.bat** (NEW)
   - Windows batch file equivalent
   - Usage: `scripts\start-dev.bat`

### Testing Scripts

All testing scripts updated with cross-platform path handling:

1. **check_summarizer.py**
   - Tests summarizer module import
   - Uses `pathlib.Path` for path construction

2. **create_test_db.py**
   - Creates test database
   - Uses `Path` for database file path

3. **test_backend.py**
   - Tests backend functionality
   - Cross-platform import paths

4. **test_connectivity.py**
   - Tests API connectivity
   - Cross-platform compatible

5. **simple_test.py**
   - Backend integration test
   - Platform-aware venv detection

6. **test_simple_fastapi.py**
   - Minimal FastAPI test
   - Cross-platform compatible

7. **test_simple_server.py**
   - HTTP server test
   - Already cross-platform

### UI Testing Scripts

1. **test_streamlit_layout.py**
   - Streamlit layout testing
   - Already cross-platform (Streamlit handles compatibility)

2. **test_streamlit_summarize_controls.py**
   - Control verification
   - Uses `pathlib.Path`

3. **test_ui_components.py**
   - UI component verification
   - Cross-platform path handling

4. **ui_inspection_checklist.py**
   - Detailed UI analysis
   - Cross-platform compatible

### New Scripts

5. **test_cross_platform.py** (NEW)
   - Comprehensive cross-platform compatibility test
   - Verifies platform detection
   - Tests path handling
   - Checks virtual environment detection
   - Usage: `python scripts/test_cross_platform.py`

## Platform-Specific Considerations

### Windows
- Virtual environment located in `venv\Scripts\`
- Python executable: `python.exe`
- Pip executable: `pip.exe`
- Path separator: `\` (handled automatically by `pathlib`)

### Linux/macOS (POSIX)
- Virtual environment located in `venv/bin/`
- Python executable: `python` (no .exe extension)
- Pip executable: `pip` (no .exe extension)
- Path separator: `/` (handled automatically by `pathlib`)

## Benefits

1. **Consistency**: All scripts use the same cross-platform patterns
2. **Maintainability**: Single codebase works on all platforms
3. **Reliability**: No hard-coded platform-specific paths
4. **Readability**: `pathlib.Path` operations are more intuitive than `os.path`
5. **Future-proof**: Uses modern Python best practices

## Testing

All scripts have been:
- ✅ Formatted with Black
- ✅ Linted with Flake8
- ✅ Tested on Windows
- ✅ Verified to use cross-platform patterns

To verify cross-platform compatibility:
```bash
python scripts/test_cross_platform.py
```

## Usage Examples

### Running Tests (All Platforms)
```bash
# Backend tests
python scripts/test_backend.py

# Check summarizer
python scripts/check_summarizer.py

# Create test database
python scripts/create_test_db.py

# Cross-platform compatibility test
python scripts/test_cross_platform.py
```

### Starting Development Server

**Cross-platform Python script:**
```bash
python scripts/start_dev.py
```

**Platform-specific alternatives:**
```bash
# Linux/macOS
bash scripts/start-dev.sh
./scripts/start-dev.sh

# Windows
scripts\start-dev.bat
```

### Running UI Tests
```bash
# Streamlit layout test (opens in browser)
streamlit run scripts/test_streamlit_layout.py

# UI component verification
python scripts/test_ui_components.py

# Detailed UI inspection
python scripts/ui_inspection_checklist.py
```

## Migration Checklist

When creating new scripts, ensure:

- [ ] Use `#!/usr/bin/env python3` shebang
- [ ] Import `pathlib.Path` for all path operations
- [ ] Use `sys.platform` checks for platform-specific logic
- [ ] Detect virtual environment for both Windows and POSIX
- [ ] Use `str(path)` when passing `Path` objects to functions expecting strings
- [ ] Test on multiple platforms if possible
- [ ] Format with Black: `python -m black scripts/`
- [ ] Lint with Flake8: `python -m flake8 scripts/`

## Related Files

- `run.py` - Main application launcher (already cross-platform)
- `AGENTS.md` - Repository instructions
- `scripts/README.md` - Scripts directory documentation

## References

- [pathlib documentation](https://docs.python.org/3/library/pathlib.html)
- [sys.platform values](https://docs.python.org/3/library/sys.html#sys.platform)
- [Python virtual environments](https://docs.python.org/3/library/venv.html)
