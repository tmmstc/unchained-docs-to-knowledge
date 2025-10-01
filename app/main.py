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
    check_duplicate_by_hash,
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


app = FastAPI(
    title="PDF OCR Processing API", version="1.0.0", lifespan=lifespan
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses."""
    start_time = time.time()

    client_host = request.client.host if request.client else 'unknown'
    logger.info(
        f"Incoming request: {request.method} {request.url.path} "
        f"from {client_host}"
    )

    response = await call_next(request)

    process_time = time.time() - start_time

    logger.info(
        f"Response: {response.status_code} for "
        f"{request.method} {request.url.path} ({process_time:.3f}s)"
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
        f"{request.character_length} chars"
    )

    if request.md5_hash:
        logger.info(f"Checking for duplicate with hash: {request.md5_hash}")
        if check_duplicate_by_hash(request.md5_hash):
            logger.info(
                f"Duplicate file detected, skipping: {request.filename}"
            )
            return {
                "success": True,
                "skipped": True,
                "message": f"File {request.filename} already exists (duplicate)",
            }

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
            md5_hash=request.md5_hash,
        )

        if success:
            logger.info(f"Successfully saved PDF: {request.filename}")
            response_data = {
                "success": True,
                "skipped": False,
                "message": (
                    f"Successfully processed {request.filename}"
                ),
            }
            if summary:
                response_data["summary"] = summary
            return response_data
        else:
            logger.error(
                f"Database save failed for: {request.filename}"
            )
            raise HTTPException(
                status_code=500, detail="Failed to save to database"
            )
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
        if limit < 1:
            logger.warning(
                f"Invalid limit value: {limit}, using default 10"
            )
            limit = 10
        elif limit > 1000:
            logger.warning(f"Limit too high: {limit}, capping at 1000")
            limit = 1000

        records = get_recent_records(limit=limit)
        logger.info(f"Retrieved {len(records)} records from database")
        logger.debug(f"Records data: {records}")
        return records
    except Exception as e:
        logger.error(f"Error retrieving records: {e}", exc_info=True)
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


@app.get("/records/no-summary", response_model=List[PDFRecord])
def get_records_without_summary(limit: int = 100):
    """
    Get records that don't have summaries yet.

    Args:
        limit: Maximum number of records to return

    Returns:
        List of PDF records without summaries
    """
    logger.info(f"Retrieving up to {limit} records without summaries")

    try:
        from .database import get_records_without_summary

        if limit < 1:
            logger.warning(f"Invalid limit value: {limit}, using default 100")
            limit = 100
        elif limit > 1000:
            logger.warning(f"Limit too high: {limit}, capping at 1000")
            limit = 1000

        records = get_records_without_summary(limit=limit)
        logger.info(
            f"Retrieved {len(records)} records without summaries"
        )
        return records
    except Exception as e:
        logger.error(f"Error retrieving records without summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/records/{record_id}/summary")
async def update_record_summary(record_id: int, generate: bool = True):
    """
    Update the summary for a specific document record.

    Args:
        record_id: ID of the record to update
        generate: Whether to generate a new summary

    Returns:
        Success status and updated summary
    """
    logger.info(f"Updating summary for record ID: {record_id}")

    try:
        from .database import get_record_by_id, update_record_summary

        record = get_record_by_id(record_id)
        if not record:
            logger.warning(f"Record not found: {record_id}")
            raise HTTPException(status_code=404, detail="Record not found")

        if not generate:
            raise HTTPException(
                status_code=400,
                detail="Generate parameter must be True"
            )

        if not record.get("extracted_text"):
            logger.warning(
                f"No extracted text for record {record_id}"
            )
            raise HTTPException(
                status_code=400,
                detail="No extracted text available for summarization"
            )

        logger.info(f"Generating summary for record {record_id}")
        summary = await summarize_document(record["extracted_text"])

        success = update_record_summary(record_id, summary)
        if success:
            logger.info(
                f"Successfully updated summary for record {record_id}"
            )
            return {
                "success": True,
                "message": "Summary updated successfully",
                "summary": summary,
            }
        else:
            logger.error(
                f"Failed to update summary for record {record_id}"
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to update summary"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating summary for record {record_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
