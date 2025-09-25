# FastAPI + Streamlit Project

A demonstration project showing integration between FastAPI backend and Streamlit frontend.

## Setup

1. Create and activate virtual environment:
```bash
py -m venv venv
```

2. Install dependencies:
```bash
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Running the Applications

### Option 1: Quick Start (Recommended)
```bash
.\venv\Scripts\python.exe start_services.py
```
This starts FastAPI and provides instructions for Streamlit.

### Option 2: Manual Start

**Terminal 1 - FastAPI Backend:**
```bash
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

**Terminal 2 - Streamlit Frontend:**
```bash
.\venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

### Option 3: Test Connectivity Only
```bash
.\venv\Scripts\python.exe test_connectivity.py
```

## Available Endpoints

- **FastAPI Backend**: http://localhost:8000
  - `GET /` - Returns hello world message
  - `GET /docs` - Swagger API documentation

- **Streamlit Frontend**: http://localhost:8501
  - Interactive UI to test backend connectivity

## Development Commands

- **Format code**: `.\venv\Scripts\python.exe -m black app/ tests/`
- **Lint code**: `.\venv\Scripts\python.exe -m flake8 app/ tests/`
- **Run tests**: `.\venv\Scripts\python.exe -m pytest tests/`

## Features

- ✅ FastAPI backend with hello world endpoint
- ✅ Streamlit frontend with connectivity testing  
- ✅ Error handling for offline backend scenarios
- ✅ Easy-to-use startup scripts
- ✅ Fallback connectivity testing without Streamlit

## Notes

- The Streamlit app includes fallback functionality if Streamlit installation fails
- Use `test_connectivity.py` to verify backend connectivity without UI
- All HTTP requests use httpx for better compatibility