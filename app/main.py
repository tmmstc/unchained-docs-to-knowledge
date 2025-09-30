"""
FastAPI backend for PDF OCR processing.
"""

import logging
import sys
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from typing import List
from .database import (
    init_database,
    save_extracted_text,
    get_recent_records,
    get_database_statistics,
)
from .models import PDFProcessRequest, PDFRecord, DatabaseStats
from .summarizer import summarize_document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info("Starting PDF OCR Processing API")
    logger.info("Application version: 1.0.0")
    logger.info("Initializing database...")

    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    logger.info("FastAPI application startup complete")

    yield

    # Shutdown
    logger.info("FastAPI application shutting down")


app = FastAPI(title="PDF OCR Processing API", version="1.0.0", lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses."""
    start_time = time.time()

    # Log incoming request
    logger.info(
        f"Incoming request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log response
    logger.info(
        f"Response: {response.status_code} for {request.method} {request.url.path} "
        f"({process_time:.3f}s)"
    )

    return response


@app.get("/")
def read_root():
    """Root endpoint."""
    logger.info("Root endpoint accessed")
    return {"message": "PDF OCR Processing API", "version": "1.0.0"}


@app.post("/process-pdf", response_model=dict)
async def process_pdf(request: PDFProcessRequest):
    """
    Store extracted PDF text and metrics in the database.
    Optionally generates summary if requested.

    Args:
        request: PDF processing request with filename, text, and metrics

    Returns:
        Success status and message
    """
    logger.info(f"Processing PDF: {request.filename}")
    logger.info(
        f"PDF metrics: {request.word_count} words, "
        f"{request.character_length} characters"
    )

    summary = None
    if request.generate_summary and request.extracted_text:
        logger.info(f"Generating summary for: {request.filename}")
        try:
            summary = await summarize_document(request.extracted_text)
            logger.info(f"Summary generated: {len(summary)} characters")
        except Exception as e:
            logger.error(f"Error generating summary: {e}")

    try:
        success = save_extracted_text(
            filename=request.filename,
            extracted_text=request.extracted_text,
            word_count=request.word_count,
            character_length=request.character_length,
            summary=summary,
        )

        if success:
            logger.info(f"Successfully saved PDF: {request.filename}")
            response_data = {
                "success": True,
                "message": f"Successfully processed {request.filename}",
            }
            if summary:
                response_data["summary"] = summary
            return response_data
        else:
            logger.error(f"Database save failed for: {request.filename}")
            raise HTTPException(status_code=500, detail="Failed to save to database")
    except Exception as e:
        logger.error(f"Error processing PDF {request.filename}: {e}")
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
    logger.info(f"Retrieving {limit} recent records")

    try:
        records = get_recent_records(limit=limit)
        logger.info(f"Retrieved {len(records)} records from database")
        return records
    except Exception as e:
        logger.error(f"Error retrieving records: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=DatabaseStats)
def get_stats():
    """
    Get database statistics.

    Returns:
        Database statistics including total records, words, and characters
    """
    logger.info("Retrieving database statistics")

    try:
        total_records, total_words, total_chars = get_database_statistics()
        logger.info(
            f"Statistics: {total_records} records, "
            f"{total_words} words, {total_chars} characters"
        )
        return DatabaseStats(
            total_records=total_records,
            total_words=total_words,
            total_characters=total_chars,
        )
    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
