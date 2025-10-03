# Executable Mode Configuration

This document describes the configuration changes made to prevent automatic browser launching when running the application as an executable.

## Overview

The application now supports an **executable mode** that disables automatic browser launching to prevent browser opening loops when packaged as a standalone executable (e.g., using PyInstaller).

## Changes Made

### 1. `run.py` Modifications

#### Detection Methods
The application detects executable mode through two methods:

1. **Automatic Detection**: Detects PyInstaller frozen executables via `sys.frozen` and `sys._MEIPASS` attributes
2. **Command-Line Flags**: 
   - `--executable-mode`: Explicitly run in executable mode
   - `--no-browser`: Disable browser auto-launch

#### Configuration
When running in executable mode, the following Streamlit configurations are applied:

```python
--server.headless true
--browser.serverAddress localhost
--server.enableCORS false
--server.enableXsrfProtection false
```

#### Key Features
- Browser launch is disabled when `executable_mode=True`
- Normal browser behavior is preserved during development
- Visual indicator shows when running in executable mode

### 2. `.streamlit/config.toml` Updates

Added browser configuration to disable usage stats:

```toml
[browser]
gatherUsageStats = false
```

### 3. New Test Suite

Created `tests/test_run_launcher.py` with tests for:
- Executable mode flag functionality
- Frozen executable detection
- Command-line argument parsing

## Usage

### Development Mode (Default)
```bash
python run.py
```
- Browser launches automatically at http://localhost:8501

### Executable Mode (No Browser Launch)
```bash
python run.py --executable-mode
```
or
```bash
python run.py --no-browser
```
- Browser does NOT launch automatically
- User must manually navigate to http://localhost:8501

### Building Executables

When packaging with PyInstaller:
```bash
pyinstaller --onefile run.py
```

The executable will automatically detect it's running in frozen mode and disable browser launching.

## Technical Details

### Detection Logic
```python
def _is_frozen(self):
    """Detect if running as a frozen executable (PyInstaller, etc.)."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
```

### Browser Launch Prevention
```python
def launch_browser(self, url, max_retries=5, initial_delay=2):
    """Launch browser with retry logic and exponential backoff."""
    if self.browser_launched or self.executable_mode:
        return
    # ... browser launch logic
```

## Benefits

1. **Prevents Browser Loop**: Stops repeated browser window openings when running as executable
2. **Preserves Dev Experience**: Normal development workflow unchanged
3. **Flexible Configuration**: Multiple ways to control browser behavior
4. **Automatic Detection**: No manual configuration needed for packaged executables
5. **Security**: Disables unnecessary features (CORS, XSRF) in standalone mode
