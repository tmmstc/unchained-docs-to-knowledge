"""
FastAPI backend for PDF OCR processing.
"""

from fastapi import FastAPI, HTTPException
from typing import List
from .database import (
    init_database,
    save_extracted_text,
    get_recent_records,
    get_database_statistics,
)
from .models import PDFProcessRequest, PDFRecord, DatabaseStats

app = FastAPI(title="PDF OCR Processing API", version="1.0.0")

# Initialize database on startup
init_database()


@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "PDF OCR Processing API", "version": "1.0.0"}


@app.post("/process-pdf", response_model=dict)
def process_pdf(request: PDFProcessRequest):
    """
    Store extracted PDF text and metrics in the database.

    Args:
        request: PDF processing request with filename, text, and metrics

    Returns:
        Success status and message
    """
    try:
        success = save_extracted_text(
            filename=request.filename,
            extracted_text=request.extracted_text,
            word_count=request.word_count,
            character_length=request.character_length,
        )

        if success:
            return {
                "success": True,
                "message": f"Successfully processed {request.filename}",
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save to database")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/records", response_model=List[PDFRecord])
def get_records(limit: int = 10):
    """
    Get recent PDF processing records.

    Args:
        limit: Maximum number of records to return

    Returns:
        List of recent PDF processing records
    """
    try:
        records = get_recent_records(limit=limit)
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=DatabaseStats)
def get_stats():
    """
    Get database statistics.

    Returns:
        Database statistics including total records, words, and characters
    """
    try:
        total_records, total_words, total_chars = get_database_statistics()
        return DatabaseStats(
            total_records=total_records,
            total_words=total_words,
            total_characters=total_chars,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
