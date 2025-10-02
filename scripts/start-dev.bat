@echo off
REM Cross-platform dev server startup script for Windows

cd /d "%~dp0\.."

REM Create venv if missing
if not exist "venv" (
    echo Creating virtualenv...
    py -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM Run the launcher using venv python
python run.py
