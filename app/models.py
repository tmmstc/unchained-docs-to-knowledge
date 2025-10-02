"""
Pydantic models for API requests and responses.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PDFProcessRequest(BaseModel):
    """Request model for PDF processing."""

    filename: str
    extracted_text: str
    word_count: int
    character_length: int
    generate_summary: Optional[bool] = True
    md5_hash: Optional[str] = None


class PDFRecord(BaseModel):
    """Response model for PDF records."""

    id: int
    filename: str
    extracted_text: Optional[str] = None
    word_count: int
    character_length: int
    created_timestamp: datetime
    preview: Optional[str] = None
    summary: Optional[str] = None
    md5_hash: Optional[str] = None


class DatabaseStats(BaseModel):
    """Response model for database statistics."""

    total_records: int
    total_words: int
    total_characters: int
