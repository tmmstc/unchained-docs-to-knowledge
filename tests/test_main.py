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
        "extracted_text": "This is a longer test text that should be summarized.",
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
