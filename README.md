# FastAPI Hello World Project

A simple FastAPI application with a single "Hello World" endpoint.

## Setup

1. Create and activate virtual environment:
```bash
py -m venv venv
# On Windows PowerShell (if execution policy allows):
.\venv\Scripts\Activate.ps1
# Alternative activation:
.\venv\Scripts\python.exe
```

2. Install dependencies:
```bash
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Commands

- **Run the application**: `.\venv\Scripts\python.exe -m uvicorn app.main:app --reload`
- **Run tests**: `.\venv\Scripts\python.exe -m pytest tests/`
- **Run linter**: `.\venv\Scripts\python.exe -m flake8 app/ tests/`
- **Format code**: `.\venv\Scripts\python.exe -m black app/ tests/`

## API Endpoints

- `GET /` - Returns `{"message": "Hello World"}`

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI application
├── tests/
│   ├── __init__.py
│   └── test_main.py     # Unit tests
├── venv/                # Virtual environment
├── requirements.txt     # Dependencies
├── .gitignore          # Git ignore rules
└── README.md           # This file
```