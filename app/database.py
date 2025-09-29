"""
Database operations for PDF OCR processing.
"""

import sqlite3
import datetime
import logging
from typing import List, Dict, Tuple
from contextlib import contextmanager

# Configure module logger
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_PATH = "pdf_ocr_database.db"


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize SQLite database with required schema."""
    logger.info("Initializing SQLite database")
    logger.info(f"Database location: {DATABASE_PATH}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS pdf_extracts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    extracted_text TEXT,
                    word_count INTEGER,
                    character_length INTEGER,
                    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            conn.commit()
            logger.info("Database schema initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def save_extracted_text(
    filename: str, extracted_text: str, word_count: int, character_length: int
) -> bool:
    """
    Save extracted text to SQLite database with metrics.

    Args:
        filename: Name of the PDF file
        extracted_text: The extracted text content
        word_count: Number of words in the text
        character_length: Character count including spaces/punctuation

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Saving extracted text to database: {filename}")
    logger.info(f"Text metrics: {word_count} words, {character_length} characters")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO pdf_extracts (filename, extracted_text, word_count,
                                        character_length, created_timestamp)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    filename,
                    extracted_text,
                    word_count,
                    character_length,
                    datetime.datetime.now(),
                ),
            )
            conn.commit()
        logger.info(f"Successfully saved to database: {filename}")
        return True
    except Exception as e:
        logger.error(f"Database save error for {filename}: {e}")
        return False


def get_recent_records(limit: int = 10) -> List[Dict]:
    """
    Get recent records from the database.

    Args:
        limit: Maximum number of records to return

    Returns:
        List of database records as dictionaries
    """
    logger.info(f"Retrieving {limit} recent records from database")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, filename, created_timestamp, word_count, character_length,
                       SUBSTR(extracted_text, 1, 200) || '...' as preview
                FROM pdf_extracts
                ORDER BY created_timestamp DESC
                LIMIT ?
            """,
                (limit,),
            )

            columns = [desc[0] for desc in cursor.description]
            records = cursor.fetchall()

            logger.info(f"Retrieved {len(records)} records from database")
            return [dict(zip(columns, record)) for record in records]

    except Exception as e:
        logger.error(f"Error retrieving records: {e}")
        raise


def get_database_statistics() -> Tuple[int, int, int]:
    """
    Get database statistics.

    Returns:
        Tuple of (total_records, total_words, total_characters)
    """
    logger.info("Retrieving database statistics")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get total records
            cursor.execute("SELECT COUNT(*) FROM pdf_extracts")
            total_records = cursor.fetchone()[0]

            # Get total words and characters
            cursor.execute(
                "SELECT SUM(word_count), SUM(character_length) FROM pdf_extracts"
            )
            result = cursor.fetchone()
            total_words, total_chars = result if result else (0, 0)

            logger.info(
                f"Database statistics: {total_records} records, "
                f"{total_words or 0} words, {total_chars or 0} characters"
            )

            return total_records, total_words or 0, total_chars or 0

    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}")
        raise
