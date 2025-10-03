"""
Database operations for PDF OCR processing.
"""

import sqlite3
import datetime
import logging
import os
import sys
from typing import List, Dict, Tuple
from contextlib import contextmanager

# Configure module logger
logger = logging.getLogger(__name__)


def get_database_path():
    """Get the database path, ensuring it's writable."""
    # If running from PyInstaller bundle, use the exe directory
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        db_path = os.path.join(exe_dir, "pdf_ocr_database.db")
    else:
        db_path = "pdf_ocr_database.db"
    
    return db_path


# Database configuration
DATABASE_PATH = get_database_path()


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DATABASE_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
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
                    summary TEXT,
                    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            conn.commit()

            cursor.execute("PRAGMA table_info(pdf_extracts)")
            columns = [row[1] for row in cursor.fetchall()]

            if 'summary' not in columns:
                logger.info("Migrating database: adding summary column")
                cursor.execute(
                    "ALTER TABLE pdf_extracts ADD COLUMN summary TEXT"
                )
                conn.commit()
                logger.info("Database migration completed successfully")

            if 'md5_hash' not in columns:
                logger.info("Migrating database: adding md5_hash column")
                cursor.execute(
                    "ALTER TABLE pdf_extracts ADD COLUMN md5_hash TEXT"
                )
                conn.commit()
                logger.info("md5_hash column added successfully")

            cursor.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='index' AND name='idx_md5_hash'
            """
            )
            if not cursor.fetchone():
                logger.info("Creating unique index on md5_hash column")
                cursor.execute(
                    """
                    CREATE UNIQUE INDEX idx_md5_hash
                    ON pdf_extracts(md5_hash)
                """
                )
                conn.commit()
                logger.info("Unique index on md5_hash created successfully")

            logger.info("Database schema initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def check_duplicate_by_hash(md5_hash: str) -> bool:
    """
    Check if a document with the given MD5 hash already exists.

    Args:
        md5_hash: MD5 hash of the PDF file

    Returns:
        True if duplicate exists, False otherwise
    """
    logger.info(f"Checking for duplicate hash: {md5_hash}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, filename FROM pdf_extracts
                WHERE md5_hash = ?
            """,
                (md5_hash,),
            )
            result = cursor.fetchone()

            if result:
                logger.info(
                    f"Duplicate found: {result['filename']} (ID: {result['id']})"
                )
                return True
            else:
                logger.info("No duplicate found")
                return False

    except Exception as e:
        logger.error(f"Error checking for duplicate hash: {e}")
        return False


def save_extracted_text(
    filename: str,
    extracted_text: str,
    word_count: int,
    character_length: int,
    summary: str = None,
    md5_hash: str = None,
) -> bool:
    """
    Save extracted text to SQLite database with metrics.

    Args:
        filename: Name of the PDF file
        extracted_text: The extracted text content
        word_count: Number of words in the text
        character_length: Character count including spaces/punctuation
        summary: Summary of the document text
        md5_hash: MD5 hash of the PDF file

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Saving extracted text to database: {filename}")
    logger.info(
        f"Text metrics: {word_count} words, {character_length} characters"
    )
    if summary:
        logger.info(f"Summary length: {len(summary)} characters")
    if md5_hash:
        logger.info(f"MD5 hash: {md5_hash}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.datetime.now().isoformat()
            cursor.execute(
                """
                INSERT INTO pdf_extracts (filename, extracted_text,
                                        word_count, character_length,
                                        summary, md5_hash, created_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    filename,
                    extracted_text,
                    word_count,
                    character_length,
                    summary,
                    md5_hash,
                    timestamp,
                ),
            )
            conn.commit()
        logger.info(f"Successfully saved to database: {filename}")
        return True
    except Exception as e:
        logger.error(
            f"Database save error for {filename}: {e}", exc_info=True
        )
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
                SELECT id, filename, created_timestamp, word_count,
                       character_length,
                       SUBSTR(extracted_text, 1, 200) || '...' as preview,
                       summary, md5_hash
                FROM pdf_extracts
                ORDER BY created_timestamp DESC
                LIMIT ?
            """,
                (limit,),
            )

            records = cursor.fetchall()
            logger.info(f"Retrieved {len(records)} records from database")

            result = []
            for record in records:
                record_dict = dict(record)
                if record_dict.get('created_timestamp'):
                    try:
                        ts = record_dict['created_timestamp']
                        if isinstance(ts, str):
                            record_dict['created_timestamp'] = (
                                datetime.datetime.fromisoformat(ts)
                            )
                    except (ValueError, TypeError) as e:
                        rec_id = record_dict.get('id')
                        logger.warning(
                            f"Error parsing timestamp for "
                            f"record {rec_id}: {e}"
                        )
                result.append(record_dict)

            return result

    except Exception as e:
        logger.error(f"Error retrieving records: {e}", exc_info=True)
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

            cursor.execute("SELECT COUNT(*) FROM pdf_extracts")
            total_records = cursor.fetchone()[0]

            cursor.execute(
                "SELECT SUM(word_count), SUM(character_length) "
                "FROM pdf_extracts"
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


def get_records_without_summary(limit: int = 100) -> List[Dict]:
    """
    Get records that don't have summaries yet.

    Args:
        limit: Maximum number of records to return

    Returns:
        List of database records without summaries
    """
    logger.info(f"Retrieving up to {limit} records without summaries")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, filename, created_timestamp, word_count,
                       character_length,
                       SUBSTR(extracted_text, 1, 200) || '...' as preview,
                       summary, md5_hash
                FROM pdf_extracts
                WHERE summary IS NULL OR summary = ''
                ORDER BY created_timestamp DESC
                LIMIT ?
            """,
                (limit,),
            )

            records = cursor.fetchall()
            logger.info(
                f"Retrieved {len(records)} records without summaries"
            )

            result = []
            for record in records:
                record_dict = dict(record)
                if record_dict.get('created_timestamp'):
                    try:
                        ts = record_dict['created_timestamp']
                        if isinstance(ts, str):
                            record_dict['created_timestamp'] = (
                                datetime.datetime.fromisoformat(ts)
                            )
                    except (ValueError, TypeError) as e:
                        rec_id = record_dict.get('id')
                        logger.warning(
                            f"Error parsing timestamp for "
                            f"record {rec_id}: {e}"
                        )
                result.append(record_dict)

            return result

    except Exception as e:
        logger.error(
            f"Error retrieving records without summary: {e}",
            exc_info=True
        )
        raise


def get_record_by_id(record_id: int) -> Dict:
    """
    Get a specific record by ID.

    Args:
        record_id: ID of the record to retrieve

    Returns:
        Dictionary containing the record data, or None if not found
    """
    logger.info(f"Retrieving record by ID: {record_id}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, filename, extracted_text, word_count,
                       character_length, summary, created_timestamp, md5_hash
                FROM pdf_extracts
                WHERE id = ?
            """,
                (record_id,),
            )

            record = cursor.fetchone()
            if record:
                record_dict = dict(record)
                logger.info(f"Found record: {record_dict['filename']}")
                return record_dict
            else:
                logger.warning(f"Record not found: {record_id}")
                return None

    except Exception as e:
        logger.error(f"Error retrieving record {record_id}: {e}")
        raise


def update_record_summary(record_id: int, summary: str) -> bool:
    """
    Update the summary for a specific record.

    Args:
        record_id: ID of the record to update
        summary: The new summary text

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Updating summary for record ID: {record_id}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE pdf_extracts
                SET summary = ?
                WHERE id = ?
            """,
                (summary, record_id),
            )
            conn.commit()

            if cursor.rowcount > 0:
                logger.info(
                    f"Successfully updated summary for record {record_id}"
                )
                return True
            else:
                logger.warning(f"No record found with ID: {record_id}")
                return False

    except Exception as e:
        logger.error(
            f"Error updating summary for record {record_id}: {e}"
        )
        return False


def delete_record(record_id: int) -> bool:
    """
    Delete a specific record from the database.

    Args:
        record_id: ID of the record to delete

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Deleting record ID: {record_id}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM pdf_extracts
                WHERE id = ?
            """,
                (record_id,),
            )
            conn.commit()

            if cursor.rowcount > 0:
                logger.info(f"Successfully deleted record {record_id}")
                return True
            else:
                logger.warning(f"No record found with ID: {record_id}")
                return False

    except Exception as e:
        logger.error(f"Error deleting record {record_id}: {e}")
        return False
