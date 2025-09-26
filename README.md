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

- Python 3.8+
- Tesseract OCR installed on system
- Virtual environment (recommended)

## Installation

1. Clone the repository
2. Create and activate virtual environment:
   ```bash
   py -m venv venv
   .\venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```bash
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

## Usage

### Quick Start
Run both services together:
```bash
python run_both.py
```

Access the applications:
- **Streamlit Frontend**: http://localhost:8501
- **FastAPI Backend**: http://localhost:8000

### Individual Services

Start FastAPI backend:
```bash
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Start Streamlit frontend:
```bash
.\venv\Scripts\python.exe -m streamlit run frontend/streamlit_app.py
```

## API Endpoints

- `GET /` - API status
- `POST /process-pdf` - Store extracted PDF text and metrics
- `GET /records?limit=10` - Retrieve recent processing records
- `GET /stats` - Get database statistics

## Development

### Testing
```bash
.\venv\Scripts\python.exe -m pytest tests/
```

### Code Quality
```bash
.\venv\Scripts\python.exe -m flake8 app/ shared/ frontend/ tests/
.\venv\Scripts\python.exe -m black app/ shared/ frontend/ tests/
```

## Modules

### PDF Processor (`shared/pdf_processor.py`)
- `extract_text_from_pdf(pdf_path)`: Extract text using Tesseract OCR
- `calculate_text_metrics(text)`: Calculate word count and character length

### Database (`app/database.py`)
- Database connection management with context managers
- CRUD operations for PDF processing records
- Statistics and analytics functions

### API (`app/main.py`)
- RESTful endpoints for PDF processing
- Pydantic models for request/response validation
- Error handling and status reporting

### Frontend (`frontend/streamlit_app.py`)
- Directory-based PDF file selection
- Batch processing with progress tracking
- Database record viewing and statistics

## License

MIT License