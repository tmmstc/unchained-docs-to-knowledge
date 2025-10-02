# PDF OCR Processing Application - Agent Instructions

## Setup
```bash
py -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Commands
- **Build**: N/A (Python project, no build step)
- **Lint**: `.\venv\Scripts\python.exe -m flake8 app/ shared/ frontend/ tests/`
- **Format**: `.\venv\Scripts\python.exe -m black app/ shared/ frontend/ tests/`
- **Test**: `.\venv\Scripts\python.exe -m pytest tests/ -v`
- **Dev Server**: `python run.py` (starts FastAPI on :8000 and Streamlit on :8501)

## Tech Stack
- **Backend**: FastAPI (REST API), SQLite (database), Uvicorn (ASGI server)
- **Frontend**: Streamlit (web UI)
- **PDF Processing**: Tesseract OCR, pdf2image, Poppler
- **AI**: OpenAI-compatible API for summarization with chunking
- **Testing**: pytest, pytest-asyncio, httpx

## Architecture
- `app/` - FastAPI backend (main.py, database.py, models.py, summarizer.py)
- `frontend/` - Streamlit app with modular components (state management, API client, file operations)
- `shared/` - Shared PDF processing utilities (pdf_processor.py)
- `tests/` - Test suite with unit and E2E tests (mark E2E with `@pytest.mark.e2e`)

## Code Style
- Use Python 3.8+ features, type hints with Pydantic models
- Modular architecture: separate concerns (API, database, processing, UI)
- Logging via standard library `logging` module
- Environment config via `.env` file (python-dotenv)
- Follow existing patterns: async/await for FastAPI, stateful design for Streamlit
