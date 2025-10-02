"""
Test the complete flow of hash calculation and storage.
This test verifies that PDF processing correctly calculates and stores MD5 hashes.
"""

import os
import tempfile
import pytest
from pathlib import Path
from shared.pdf_processor import (
    calculate_md5_hash,
    extract_text_from_pdf,
    calculate_text_metrics,
)
from app.database import (
    init_database,
    save_extracted_text,
    get_recent_records,
    check_duplicate_by_hash,
)


@pytest.fixture
def temp_database():
    """Create a temporary database for testing"""
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(temp_db_fd)

    original_db_path = None
    try:
        import app.database

        original_db_path = app.database.DATABASE_PATH
        app.database.DATABASE_PATH = temp_db_path

        yield temp_db_path

    finally:
        if original_db_path:
            app.database.DATABASE_PATH = original_db_path
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


@pytest.fixture
def sample_pdf():
    """Create a simple PDF for testing"""
    # For this test, we'll use a mock/test PDF path
    # In real usage, you'd need an actual PDF file
    pdf_path = Path(__file__).parent / "fixtures" / "sample.pdf"
    if pdf_path.exists():
        return str(pdf_path)
    return None


def test_hash_calculation():
    """Test that MD5 hash calculation works"""
    # Create a temporary file with known content
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=False) as f:
        test_content = b"Test PDF content"
        f.write(test_content)
        temp_path = f.name

    try:
        # Calculate hash
        hash_value = calculate_md5_hash(temp_path)

        # Verify hash is not empty and has correct format
        assert hash_value is not None
        assert len(hash_value) == 32  # MD5 hash is 32 hex characters
        assert all(c in "0123456789abcdef" for c in hash_value.lower())

        # Calculate again to verify consistency
        hash_value2 = calculate_md5_hash(temp_path)
        assert hash_value == hash_value2

    finally:
        os.unlink(temp_path)


def test_complete_processing_flow_with_hash(temp_database):
    """Test complete flow: calculate hash, process text, save to database"""
    init_database()

    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=False) as f:
        test_content = b"Test PDF content for hash verification"
        f.write(test_content)
        temp_path = f.name

    try:
        filename = "test_document.pdf"

        # Step 1: Calculate MD5 hash
        md5_hash = calculate_md5_hash(temp_path)
        assert md5_hash is not None
        assert len(md5_hash) == 32

        # Step 2: Check for duplicates (should be False initially)
        is_duplicate = check_duplicate_by_hash(md5_hash)
        assert is_duplicate is False

        # Step 3: Process text (mock extracted text)
        extracted_text = "This is mock extracted text from the PDF"
        word_count, character_length = calculate_text_metrics(extracted_text)

        # Step 4: Save to database with hash
        success = save_extracted_text(
            filename=filename,
            extracted_text=extracted_text,
            word_count=word_count,
            character_length=character_length,
            md5_hash=md5_hash,
        )
        assert success is True

        # Step 5: Verify the record was saved with hash
        records = get_recent_records(limit=10)
        assert len(records) == 1

        record = records[0]
        assert record["filename"] == filename
        assert record["md5_hash"] == md5_hash
        assert record["word_count"] == word_count
        assert record["character_length"] == character_length

        # Step 6: Verify duplicate detection now works
        is_duplicate = check_duplicate_by_hash(md5_hash)
        assert is_duplicate is True

    finally:
        os.unlink(temp_path)


def test_processing_without_hash_still_works(temp_database):
    """Test that processing works even without providing a hash"""
    init_database()

    filename = "no_hash_document.pdf"
    extracted_text = "Document without hash"
    word_count, character_length = calculate_text_metrics(extracted_text)

    # Save without hash
    success = save_extracted_text(
        filename=filename,
        extracted_text=extracted_text,
        word_count=word_count,
        character_length=character_length,
        md5_hash=None,
    )
    assert success is True

    # Verify it was saved
    records = get_recent_records(limit=10)
    assert len(records) == 1

    record = records[0]
    assert record["filename"] == filename
    assert record["md5_hash"] is None


def test_duplicate_prevention(temp_database):
    """Test that duplicate detection prevents re-processing same file"""
    init_database()

    with tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=False) as f:
        test_content = b"Duplicate test content"
        f.write(test_content)
        temp_path = f.name

    try:
        md5_hash = calculate_md5_hash(temp_path)

        # First save should succeed
        success1 = save_extracted_text(
            filename="file1.pdf",
            extracted_text="Content 1",
            word_count=2,
            character_length=9,
            md5_hash=md5_hash,
        )
        assert success1 is True

        # Check duplicate before second save
        is_duplicate = check_duplicate_by_hash(md5_hash)
        assert is_duplicate is True

        # Second save with same hash should fail due to unique constraint
        success2 = save_extracted_text(
            filename="file2.pdf",
            extracted_text="Content 2",
            word_count=2,
            character_length=9,
            md5_hash=md5_hash,
        )
        assert success2 is False

        # Verify only one record exists
        records = get_recent_records(limit=10)
        assert len(records) == 1

    finally:
        os.unlink(temp_path)
