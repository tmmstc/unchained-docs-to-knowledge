import sqlite3
import os
import tempfile
import datetime
import pytest
import re
# Remove unused imports
# from unittest.mock import patch, MagicMock


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    # Initialize database schema
    conn = sqlite3.connect(db_path)
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
    conn.close()

    yield db_path
    os.unlink(db_path)


def test_database_schema(temp_db):
    """Test that the database has the correct schema"""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    # Get table info
    cursor.execute("PRAGMA table_info(pdf_extracts)")
    columns = cursor.fetchall()

    # Extract column names
    column_names = [column[1] for column in columns]

    expected_columns = [
        "id",
        "filename",
        "extracted_text",
        "word_count",
        "character_length",
        "created_timestamp",
    ]

    assert set(column_names) == set(expected_columns)
    conn.close()


def calculate_text_metrics(text):
    """Calculate word count and character length for extracted text"""
    if not text:
        return 0, 0

    # Character length (including whitespace and punctuation)
    character_length = len(text)

    # Word count - split by whitespace and filter out empty strings
    # This properly handles multiple spaces, tabs, newlines, and punctuation
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)

    return word_count, character_length


def save_extracted_text_mock(db_path, filename, extracted_text):
    """Mock version of save_extracted_text function for testing"""
    try:
        # Calculate metrics
        word_count, character_length = calculate_text_metrics(extracted_text)

        conn = sqlite3.connect(db_path)
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
        conn.close()
        return True
    except Exception:
        return False


def test_save_extracted_text_with_metrics(temp_db):
    """Test saving text with calculated metrics"""
    # Test data
    filename = "test_document.pdf"
    text = "Hello world! This is a test document with some words."

    # Save the text using mock function
    result = save_extracted_text_mock(temp_db, filename, text)
    assert result is True

    # Verify data in database
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT filename, extracted_text, word_count, character_length "
        "FROM pdf_extracts WHERE filename = ?",
        (filename,),
    )
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == filename
    assert row[1] == text
    assert row[2] == 10  # word count
    assert row[3] == len(text)  # character length


def test_save_empty_text(temp_db):
    """Test saving empty text"""
    filename = "empty_document.pdf"
    text = ""

    result = save_extracted_text_mock(temp_db, filename, text)
    assert result is True

    # Verify metrics for empty text
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT word_count, character_length FROM pdf_extracts "
        "WHERE filename = ?",
        (filename,),
    )
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == 0  # word count
    assert row[1] == 0  # character length


def test_save_text_with_special_characters(temp_db):
    """Test saving text with punctuation and special characters"""
    filename = "special_chars.pdf"
    text = "Hello, world! Email: user@example.com. Phone: 555-1234."

    result = save_extracted_text_mock(temp_db, filename, text)
    assert result is True

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT word_count, character_length FROM pdf_extracts "
        "WHERE filename = ?",
        (filename,),
    )
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    # extracted words: Hello, world, Email, user, example, com, Phone, 555, 1234  # noqa: E501
    assert row[0] == 9
    assert row[1] == len(text)
