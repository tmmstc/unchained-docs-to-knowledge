"""
Integration tests for database functionality.
Tests the actual database operations including table creation,
data insertion, retrieval, and metrics calculation.
"""

import sqlite3
import tempfile
import os
import datetime
import pytest
from app.database import (
    init_database,
    save_extracted_text,
    get_recent_records,
    get_database_statistics,
    DATABASE_PATH,
)
from shared.pdf_processor import calculate_text_metrics


@pytest.fixture
def temp_database():
    """Create a temporary database for testing"""
    # Create a temporary file for the test database
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(temp_db_fd)

    # Temporarily replace the database path
    original_db_path = DATABASE_PATH
    import app.database

    app.database.DATABASE_PATH = temp_db_path

    yield temp_db_path

    # Clean up - restore original path and delete temp file
    app.database.DATABASE_PATH = original_db_path
    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)


class TestDatabaseOperations:
    def test_init_database_creates_table(self, temp_database):
        """Test that database initialization creates the required table"""
        init_database()

        # Check if the table was created
        conn = sqlite3.connect(temp_database)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='pdf_extracts'"
        )
        table_exists = cursor.fetchone() is not None
        conn.close()

        assert table_exists, "pdf_extracts table was not created"

    def test_save_and_retrieve_extracted_text(self, temp_database):
        """Test saving extracted text and calculating metrics"""
        init_database()

        # Test data
        filename = "test_document.pdf"
        extracted_text = "This is a test document with multiple words and sentences."
        word_count, character_length = calculate_text_metrics(extracted_text)

        # Save the extracted text
        success = save_extracted_text(
            filename, extracted_text, word_count, character_length
        )
        assert success, "Failed to save extracted text"

        # Verify the data was saved correctly
        conn = sqlite3.connect(temp_database)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM pdf_extracts WHERE filename = ?", (filename,))
        result = cursor.fetchone()
        conn.close()

        assert result is not None, "No record found in database"

        # Unpack the result
        (
            db_id,
            db_filename,
            db_text,
            db_word_count,
            db_char_length,
            db_summary,
            db_timestamp,
        ) = result

        # Verify the saved data
        assert db_filename == filename
        assert db_text == extracted_text
        assert db_word_count == word_count
        assert db_char_length == character_length

        # Verify timestamp is recent (within last minute)
        saved_time = datetime.datetime.fromisoformat(db_timestamp)
        time_diff = datetime.datetime.now() - saved_time
        assert time_diff.total_seconds() < 60, "Timestamp is not recent"

    def test_save_multiple_files(self, temp_database):
        """Test saving multiple files and retrieving them"""
        init_database()

        # Test data for multiple files
        test_files = [
            ("doc1.pdf", "First document content"),
            ("doc2.pdf", "Second document with more content and words"),
            ("doc3.pdf", "Third document content here"),
        ]

        # Save all files
        for filename, content in test_files:
            word_count, character_length = calculate_text_metrics(content)
            success = save_extracted_text(
                filename, content, word_count, character_length
            )
            assert success, f"Failed to save {filename}"

        # Verify all files were saved
        conn = sqlite3.connect(temp_database)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM pdf_extracts")
        count = cursor.fetchone()[0]
        assert count == len(test_files), "Not all files were saved"

        conn.close()

    def test_get_recent_records(self, temp_database):
        """Test retrieving recent records"""
        init_database()

        # Add test data
        test_files = [
            ("doc1.pdf", "First document"),
            ("doc2.pdf", "Second document"),
        ]

        for filename, content in test_files:
            word_count, character_length = calculate_text_metrics(content)
            save_extracted_text(filename, content, word_count, character_length)

        # Get records
        records = get_recent_records(limit=10)
        assert len(records) == 2
        assert records[0]["filename"] in ["doc1.pdf", "doc2.pdf"]

    def test_get_database_statistics(self, temp_database):
        """Test getting database statistics"""
        init_database()

        # Initially should be empty
        total_records, total_words, total_chars = get_database_statistics()
        assert total_records == 0
        assert total_words == 0
        assert total_chars == 0

        # Add some data
        content = "Test content with five words"
        word_count, character_length = calculate_text_metrics(content)
        save_extracted_text("test.pdf", content, word_count, character_length)

        # Check statistics
        total_records, total_words, total_chars = get_database_statistics()
        assert total_records == 1
        assert total_words == word_count
        assert total_chars == character_length
