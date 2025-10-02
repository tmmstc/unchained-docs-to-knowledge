# Repository Agent Instructions

## Setup Commands
- **Initial setup**: `py -m venv venv` then `.\venv\Scripts\python.exe -m pip install -r requirements.txt`
- **Build**: No build step required for Python project
- **Lint**: `.\venv\Scripts\python.exe -m flake8 app/ tests/`
- **Tests**: `.\venv\Scripts\python.exe -m pytest tests/`
- **Dev server**: `python run.py` (runs both FastAPI and Streamlit)
- **Format**: `.\venv\Scripts\python.exe -m black app/ tests/`

## Project Structure
- **app/**: FastAPI backend
- **frontend/**: Streamlit frontend  
- **shared/**: Shared utilities (PDF processing, OCR)
- **tests/**: Test suite
- **scripts/**: Utility scripts for development and testing
- **docs/**: Project documentation

## Tech Stack & Architecture
- **Python 3.13** with virtual environment (venv)
- **FastAPI** - Web framework for building APIs
- **Uvicorn** - ASGI web server
- **Pytest** - Testing framework with TestClient for API testing
- **Flake8** - Code linting
- **Black** - Code formatting

## Code Style Guidelines
- Use Black for code formatting (line length 88)
- Follow PEP 8 guidelines enforced by Flake8
- Use type hints where beneficial
- Keep functions small and focused
- Write tests for all endpoints