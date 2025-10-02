# Streamlit Multipage App Structure

This directory contains the page files for the multipage Streamlit application.

## Pages

1. **1_📤_Ingest_Documents.py** - Document ingestion page for uploading and processing PDFs
2. **2_📊_View_Database.py** - Database viewing and management page

## Navigation

Streamlit automatically creates a sidebar navigation based on the filename prefix numbers and emojis. The main app (`streamlit_app.py`) serves as the home page.

## Adding New Pages

To add new pages, create a new Python file in this directory with the naming convention:
- `<number>_<emoji>_<Page_Name>.py`

Example: `3_🔍_Search_Results.py`
