"""
Tests for FastAPI endpoints.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_database
import pytest

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Setup database for tests."""
    init_database()


def test_read_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "PDF OCR Processing API" in response.json()["message"]


def test_process_pdf():
    """Test the PDF processing endpoint."""
    test_data = {
        "filename": "test.pdf",
        "extracted_text": "This is test text",
        "word_count": 4,
        "character_length": 17,
        "generate_summary": False,
    }

    response = client.post("/process-pdf", json=test_data)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "test.pdf" in response.json()["message"]


def test_process_pdf_with_summary():
    """Test the PDF processing endpoint with summary generation."""
    test_data = {
        "filename": "test_summary.pdf",
        "extracted_text": (
            "This is a longer test text that should be summarized."
        ),
        "word_count": 10,
        "character_length": 54,
        "generate_summary": True,
    }

    response = client.post("/process-pdf", json=test_data)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "test_summary.pdf" in response.json()["message"]


def test_get_records():
    """Test the records retrieval endpoint."""
    response = client.get("/records")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_records_with_limit():
    """Test the records retrieval endpoint with limit."""
    response = client.get("/records?limit=5")
    assert response.status_code == 200
    records = response.json()
    assert isinstance(records, list)
    assert len(records) <= 5


def test_get_records_with_limit_10():
    """Test the records retrieval endpoint with limit=10."""
    response = client.get("/records?limit=10")
    assert response.status_code == 200
    records = response.json()
    assert isinstance(records, list)
    assert len(records) <= 10
    for record in records:
        assert "id" in record
        assert "filename" in record
        assert "created_timestamp" in record
        assert "word_count" in record
        assert "character_length" in record


def test_get_stats():
    """Test the statistics endpoint."""
    response = client.get("/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total_records" in stats
    assert "total_words" in stats
    assert "total_characters" in stats
    assert isinstance(stats["total_records"], int)
    assert isinstance(stats["total_words"], int)
    assert isinstance(stats["total_characters"], int)


def test_get_records_without_summary():
    """Test the endpoint for retrieving records without summaries."""
    test_data = {
        "filename": "test_no_summary.pdf",
        "extracted_text": "This is test text without summary",
        "word_count": 6,
        "character_length": 34,
        "generate_summary": False,
    }

    client.post("/process-pdf", json=test_data)

    response = client.get("/records/no-summary")
    assert response.status_code == 200
    records = response.json()
    assert isinstance(records, list)


def test_update_record_summary():
    """Test updating a record's summary."""
    test_data = {
        "filename": "test_update_summary.pdf",
        "extracted_text": "This is test text for summary update",
        "word_count": 7,
        "character_length": 37,
        "generate_summary": False,
    }

    response = client.post("/process-pdf", json=test_data)
    assert response.status_code == 200

    records_response = client.get("/records?limit=1")
    records = records_response.json()
    if records:
        record_id = records[0]["id"]

        update_response = client.put(
            f"/records/{record_id}/summary", params={"generate": True}
        )
        assert update_response.status_code == 200
        result = update_response.json()
        assert result["success"] is True
        assert "summary" in result


def test_update_nonexistent_record_summary():
    """Test updating summary for a non-existent record."""
    response = client.put(
        "/records/999999/summary",
        params={"generate": True}
    )
    assert response.status_code == 404


def test_process_pdf_with_md5_hash():
    """Test the PDF processing endpoint with MD5 hash."""
    import uuid
    test_data = {
        "filename": "test_with_hash.pdf",
        "extracted_text": "This is test text with hash",
        "word_count": 6,
        "character_length": 27,
        "generate_summary": False,
        "md5_hash": uuid.uuid4().hex,
    }

    response = client.post("/process-pdf", json=test_data)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["skipped"] is False


def test_process_duplicate_pdf():
    """Test that duplicate PDFs are detected and skipped."""
    import uuid
    test_hash = uuid.uuid4().hex

    test_data = {
        "filename": "original.pdf",
        "extracted_text": "This is original text",
        "word_count": 4,
        "character_length": 21,
        "generate_summary": False,
        "md5_hash": test_hash,
    }

    response1 = client.post("/process-pdf", json=test_data)
    assert response1.status_code == 200
    assert response1.json()["success"] is True
    assert response1.json()["skipped"] is False

    test_data["filename"] = "duplicate.pdf"
    response2 = client.post("/process-pdf", json=test_data)
    assert response2.status_code == 200
    assert response2.json()["success"] is True
    assert response2.json()["skipped"] is True
    assert "already exists" in response2.json()["message"]


def test_delete_record():
    """Test deleting a record."""
    test_data = {
        "filename": "test_delete.pdf",
        "extracted_text": "This is test text for deletion",
        "word_count": 6,
        "character_length": 31,
        "generate_summary": False,
    }

    response = client.post("/process-pdf", json=test_data)
    assert response.status_code == 200

    records_response = client.get("/records?limit=1")
    records = records_response.json()
    if records:
        record_id = records[0]["id"]

        delete_response = client.delete(f"/records/{record_id}")
        assert delete_response.status_code == 200
        result = delete_response.json()
        assert result["success"] is True


def test_delete_nonexistent_record():
    """Test deleting a non-existent record."""
    response = client.delete("/records/999999")
    assert response.status_code == 404
