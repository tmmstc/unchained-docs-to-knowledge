"""
Tests for Streamlit app utility functions.
"""

import sys
import os
import tempfile
import unittest.mock as mock
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_shorten_hash():
    """Test hash shortening function."""
    from frontend.data_transforms import shorten_hash

    full_hash = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
    short = shorten_hash(full_hash, 8)
    assert short == "a1b2c3d4"

    assert shorten_hash(None) == "N/A"
    assert shorten_hash("") == "N/A"


def test_filter_records():
    """Test record filtering."""
    from frontend.data_transforms import filter_records

    records = [
        {"filename": "test1.pdf", "summary": "Summary 1"},
        {"filename": "test2.pdf", "summary": None},
        {"filename": "document.pdf", "summary": "Summary 2"},
    ]

    filtered = filter_records(records, filename_filter="test")
    assert len(filtered) == 2

    filtered = filter_records(records, summary_filter="With Summary")
    assert len(filtered) == 2

    filtered = filter_records(records, summary_filter="Without Summary")
    assert len(filtered) == 1


def test_sort_records():
    """Test record sorting."""
    from frontend.data_transforms import sort_records

    records = [
        {"id": 3, "filename": "c.pdf", "word_count": 100},
        {"id": 1, "filename": "a.pdf", "word_count": 300},
        {"id": 2, "filename": "b.pdf", "word_count": 200},
    ]

    sorted_records = sort_records(records.copy(), "ID (Asc)")
    assert sorted_records[0]["id"] == 1

    sorted_records = sort_records(records.copy(), "ID (Desc)")
    assert sorted_records[0]["id"] == 3

    sorted_records = sort_records(records.copy(), "Filename")
    assert sorted_records[0]["filename"] == "a.pdf"

    sorted_records = sort_records(records.copy(), "Words (Desc)")
    assert sorted_records[0]["word_count"] == 300


def test_state_manager_init():
    """Test state manager initialization."""
    from frontend.state_manager import init_delete_confirmation_state

    mock_session = {}
    init_delete_confirmation_state(mock_session)

    assert "delete_confirmation_id" in mock_session
    assert "last_selected_record_id" in mock_session
    assert mock_session["delete_confirmation_id"] is None
    assert mock_session["last_selected_record_id"] is None


def test_state_manager_confirmation_mode():
    """Test confirmation mode checking."""
    from frontend.state_manager import (
        is_in_confirmation_mode,
        set_confirmation_mode,
    )

    mock_session = {"delete_confirmation_id": None}

    assert is_in_confirmation_mode(mock_session, 123) is False

    set_confirmation_mode(mock_session, 123)
    assert is_in_confirmation_mode(mock_session, 123) is True


def test_state_manager_reset_on_change():
    """Test state reset on selection change."""
    from frontend.state_manager import (
        reset_delete_confirmation_on_selection_change,
    )

    mock_session = {
        "delete_confirmation_id": 100,
        "last_selected_record_id": 100,
    }

    reset_delete_confirmation_on_selection_change(mock_session, 200)

    assert mock_session["delete_confirmation_id"] is None
    assert mock_session["last_selected_record_id"] == 200


def test_file_operations_get_pdf_files():
    """Test getting PDF files from directory."""
    from frontend.file_operations import get_pdf_files_from_directory

    with tempfile.TemporaryDirectory() as temp_dir:
        test_file1 = os.path.join(temp_dir, "test1.pdf")
        test_file2 = os.path.join(temp_dir, "test2.pdf")
        other_file = os.path.join(temp_dir, "test.txt")

        open(test_file1, "w").close()
        open(test_file2, "w").close()
        open(other_file, "w").close()

        pdf_files = get_pdf_files_from_directory(temp_dir)

        assert len(pdf_files) == 2
        assert all(f.endswith(".pdf") for f in pdf_files)


def test_data_processing_single_pdf():
    """Test single PDF processing logic."""
    from frontend.data_processing import process_single_pdf

    with mock.patch("frontend.data_processing.calculate_md5_hash") as mock_hash, \
         mock.patch("frontend.data_processing.extract_text_from_pdf") as mock_extract, \
         mock.patch("frontend.data_processing.calculate_text_metrics") as mock_metrics, \
         mock.patch("frontend.data_processing.save_extracted_text_to_backend") as mock_save:

        mock_hash.return_value = "abc123"
        mock_extract.return_value = "Extracted text"
        mock_metrics.return_value = (2, 14)
        mock_save.return_value = {"success": True, "skipped": False}

        result = process_single_pdf("/path/to/test.pdf", "test.pdf", True)

        assert result["success"] is True
        mock_hash.assert_called_once()
        mock_extract.assert_called_once()
        mock_metrics.assert_called_once()
        mock_save.assert_called_once()


def test_process_uploaded_files():
    """Test that uploaded files can be processed through tempfile workflow."""
    from frontend.data_processing import process_uploaded_files

    mock_uploaded_file = MagicMock()
    mock_uploaded_file.name = "test.pdf"
    pdf_content = b"%PDF-1.4 test content"
    mock_uploaded_file.getbuffer.return_value = pdf_content

    uploaded_files = [mock_uploaded_file]

    with mock.patch("frontend.data_processing.create_temp_file_from_upload") as mock_create, \
         mock.patch("frontend.data_processing.process_single_pdf") as mock_process, \
         mock.patch("frontend.data_processing.cleanup_temp_file") as mock_cleanup:

        mock_create.return_value = "/tmp/test.pdf"
        mock_process.return_value = {"success": True, "skipped": False}

        result = process_uploaded_files(uploaded_files, generate_summary=True)

        assert result["successful"] == 1
        assert result["failed"] == 0
        assert result["skipped"] == 0

        mock_create.assert_called_once()
        mock_process.assert_called_once()
        mock_cleanup.assert_called_once()


def test_temp_file_cleanup():
    """Test that temporary files are cleaned up after processing."""
    from frontend.file_operations import create_temp_file_from_upload, cleanup_temp_file

    mock_uploaded_file = MagicMock()
    mock_uploaded_file.getbuffer.return_value = b"%PDF-1.4"

    temp_path = create_temp_file_from_upload(mock_uploaded_file)

    assert os.path.exists(temp_path)

    cleanup_temp_file(temp_path)

    assert not os.path.exists(temp_path)


def test_api_client_functions():
    """Test API client wrapper functions."""
    from frontend.api_client import (
        save_extracted_text_to_backend,
        get_records_from_backend,
        get_stats_from_backend,
    )

    with mock.patch("frontend.api_client.requests.post") as mock_post, \
         mock.patch("frontend.api_client.requests.get") as mock_get:

        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        result = save_extracted_text_to_backend(
            "test.pdf", "text", 1, 4, True, "hash123"
        )
        assert result["success"] is True

        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        records = get_records_from_backend(10)
        assert records == []

        mock_response.json.return_value = {
            "total_records": 5,
            "total_words": 100,
            "total_characters": 500,
        }
        mock_get.return_value = mock_response

        stats = get_stats_from_backend()
        assert stats["total_records"] == 5
