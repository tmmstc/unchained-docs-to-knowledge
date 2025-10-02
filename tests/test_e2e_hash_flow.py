"""
End-to-end test for hash calculation and duplicate detection in PDF processing pipeline.
This test simulates the actual workflow from file upload through database storage.
"""

import os
import tempfile
import pytest
import httpx
from pathlib import Path
from app.main import app
from shared.pdf_processor import calculate_md5_hash, calculate_text_metrics


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

        # Initialize the database
        app.database.init_database()

        yield temp_db_path

    finally:
        if original_db_path:
            app.database.DATABASE_PATH = original_db_path
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_pdf_processing_with_hash(temp_database):
    """End-to-end test: Process a PDF with hash calculation and storage"""

    # Create a test PDF file
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=False) as f:
        test_content = b"%PDF-1.4\nTest PDF content for E2E testing"
        f.write(test_content)
        temp_pdf_path = f.name

    try:
        # Step 1: Calculate hash (simulating what frontend does)
        md5_hash = calculate_md5_hash(temp_pdf_path)
        assert md5_hash is not None
        assert len(md5_hash) == 32

        # Step 2: Simulate text extraction
        extracted_text = "This is test text extracted from the PDF document."
        word_count, character_length = calculate_text_metrics(extracted_text)

        # Step 3: Send to API (simulating what frontend does)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/process-pdf",
                json={
                    "filename": "test_e2e.pdf",
                    "extracted_text": extracted_text,
                    "word_count": word_count,
                    "character_length": character_length,
                    "generate_summary": False,
                    "md5_hash": md5_hash,
                },
            )

            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert result.get("skipped") is False

            # Step 4: Verify record was saved with hash
            response = await client.get("/records?limit=10")
            assert response.status_code == 200
            records = response.json()

            assert len(records) == 1
            record = records[0]
            assert record["filename"] == "test_e2e.pdf"
            assert record["md5_hash"] == md5_hash
            assert record["word_count"] == word_count
            assert record["character_length"] == character_length

            # Step 5: Try to process the same file again (should be detected as duplicate)
            response = await client.post(
                "/process-pdf",
                json={
                    "filename": "test_e2e_duplicate.pdf",  # Different filename
                    "extracted_text": extracted_text,
                    "word_count": word_count,
                    "character_length": character_length,
                    "generate_summary": False,
                    "md5_hash": md5_hash,  # Same hash
                },
            )

            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert result.get("skipped") is True  # Should be skipped as duplicate
            assert "duplicate" in result["message"].lower()

            # Step 6: Verify no new record was created
            response = await client.get("/records?limit=10")
            assert response.status_code == 200
            records = response.json()
            assert len(records) == 1  # Still only one record

    finally:
        os.unlink(temp_pdf_path)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_multiple_different_files(temp_database):
    """Test processing multiple different files with different hashes"""

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Process first file
        response = await client.post(
            "/process-pdf",
            json={
                "filename": "file1.pdf",
                "extracted_text": "Content of first file",
                "word_count": 4,
                "character_length": 21,
                "generate_summary": False,
                "md5_hash": "hash1_abc123def456789",
            },
        )
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result.get("skipped") is False

        # Process second file with different hash
        response = await client.post(
            "/process-pdf",
            json={
                "filename": "file2.pdf",
                "extracted_text": "Content of second file",
                "word_count": 4,
                "character_length": 22,
                "generate_summary": False,
                "md5_hash": "hash2_xyz987uvw654321",
            },
        )
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result.get("skipped") is False

        # Verify both records exist
        response = await client.get("/records?limit=10")
        assert response.status_code == 200
        records = response.json()
        assert len(records) == 2

        # Verify each has correct hash
        filenames_and_hashes = {r["filename"]: r["md5_hash"] for r in records}
        assert filenames_and_hashes["file1.pdf"] == "hash1_abc123def456789"
        assert filenames_and_hashes["file2.pdf"] == "hash2_xyz987uvw654321"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_processing_without_hash_backwards_compatibility(temp_database):
    """Test that processing still works without hash (backwards compatibility)"""

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/process-pdf",
            json={
                "filename": "no_hash_file.pdf",
                "extracted_text": "Content without hash",
                "word_count": 3,
                "character_length": 20,
                "generate_summary": False,
                # md5_hash not provided
            },
        )

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True

        # Verify record was saved
        response = await client.get("/records?limit=10")
        assert response.status_code == 200
        records = response.json()
        assert len(records) == 1

        record = records[0]
        assert record["filename"] == "no_hash_file.pdf"
        assert record["md5_hash"] is None or record["md5_hash"] == ""
