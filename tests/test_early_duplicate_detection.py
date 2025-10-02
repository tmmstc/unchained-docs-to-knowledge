"""
Tests for early duplicate detection before OCR/text extraction.
Verifies that MD5 hash is computed immediately and duplicate check prevents unnecessary processing.
"""

import os
import tempfile
import pytest
from unittest import mock
from frontend.data_processing import (
    process_single_pdf,
    process_pdf_batch,
    process_uploaded_files,
)


def test_early_duplicate_detection_skips_ocr():
    """Test that duplicate detection happens before OCR extraction."""
    
    with mock.patch("frontend.data_processing.calculate_md5_hash") as mock_hash, \
         mock.patch("frontend.data_processing.check_duplicate_hash") as mock_check, \
         mock.patch("frontend.data_processing.extract_text_from_pdf") as mock_extract:
        
        mock_hash.return_value = "duplicate_hash_123"
        mock_check.return_value = True
        
        result = process_single_pdf("/path/to/test.pdf", "test.pdf", True)
        
        # Verify hash was calculated
        mock_hash.assert_called_once()
        
        # Verify duplicate check was performed
        mock_check.assert_called_once_with("duplicate_hash_123")
        
        # Verify OCR was NOT called (processing was skipped)
        mock_extract.assert_not_called()
        
        # Verify result indicates skip
        assert result["success"] is True
        assert result["skipped"] is True
        assert "duplicate" in result["message"].lower()


def test_non_duplicate_proceeds_to_ocr():
    """Test that non-duplicate files proceed to full OCR processing."""
    
    with mock.patch("frontend.data_processing.calculate_md5_hash") as mock_hash, \
         mock.patch("frontend.data_processing.check_duplicate_hash") as mock_check, \
         mock.patch("frontend.data_processing.extract_text_from_pdf") as mock_extract, \
         mock.patch("frontend.data_processing.calculate_text_metrics") as mock_metrics, \
         mock.patch("frontend.data_processing.save_extracted_text_to_backend") as mock_save:
        
        mock_hash.return_value = "unique_hash_456"
        mock_check.return_value = False
        mock_extract.return_value = "Extracted text content"
        mock_metrics.return_value = (3, 23)
        mock_save.return_value = {"success": True, "skipped": False}
        
        result = process_single_pdf("/path/to/test.pdf", "test.pdf", True)
        
        # Verify hash was calculated
        mock_hash.assert_called_once()
        
        # Verify duplicate check was performed
        mock_check.assert_called_once_with("unique_hash_456")
        
        # Verify OCR WAS called (processing proceeded)
        mock_extract.assert_called_once()
        
        # Verify result indicates success
        assert result["success"] is True
        assert result.get("skipped", False) is False


def test_batch_processing_with_duplicates():
    """Test batch folder processing with mix of duplicates and new files."""
    
    with mock.patch("frontend.data_processing.calculate_md5_hash") as mock_hash, \
         mock.patch("frontend.data_processing.check_duplicate_hash") as mock_check, \
         mock.patch("frontend.data_processing.extract_text_from_pdf") as mock_extract, \
         mock.patch("frontend.data_processing.calculate_text_metrics") as mock_metrics, \
         mock.patch("frontend.data_processing.save_extracted_text_to_backend") as mock_save:
        
        # Setup mocks to return different results for different files
        mock_hash.side_effect = ["hash1", "hash2", "hash3"]
        mock_check.side_effect = [False, True, False]  # file2 is duplicate
        mock_extract.return_value = "Text"
        mock_metrics.return_value = (1, 4)
        mock_save.return_value = {"success": True, "skipped": False}
        
        pdf_files = ["/path/file1.pdf", "/path/file2.pdf", "/path/file3.pdf"]
        result = process_pdf_batch(pdf_files, generate_summary=True)
        
        # Verify results
        assert result["successful"] == 2  # file1 and file3
        assert result["skipped"] == 1     # file2
        assert result["failed"] == 0
        
        # Verify OCR was called only for non-duplicates (2 times, not 3)
        assert mock_extract.call_count == 2


def test_upload_processing_with_duplicates():
    """Test file upload processing with duplicate detection."""
    
    from unittest.mock import MagicMock
    
    mock_file1 = MagicMock()
    mock_file1.name = "upload1.pdf"
    mock_file1.getbuffer.return_value = b"%PDF-1.4 content1"
    
    mock_file2 = MagicMock()
    mock_file2.name = "upload2.pdf"
    mock_file2.getbuffer.return_value = b"%PDF-1.4 content2"
    
    with mock.patch("frontend.data_processing.create_temp_file_from_upload") as mock_create, \
         mock.patch("frontend.data_processing.calculate_md5_hash") as mock_hash, \
         mock.patch("frontend.data_processing.check_duplicate_hash") as mock_check, \
         mock.patch("frontend.data_processing.extract_text_from_pdf") as mock_extract, \
         mock.patch("frontend.data_processing.calculate_text_metrics") as mock_metrics, \
         mock.patch("frontend.data_processing.save_extracted_text_to_backend") as mock_save, \
         mock.patch("frontend.data_processing.cleanup_temp_file"):
        
        mock_create.side_effect = ["/tmp/upload1.pdf", "/tmp/upload2.pdf"]
        mock_hash.side_effect = ["hash_a", "hash_b"]
        mock_check.side_effect = [False, True]  # second file is duplicate
        mock_extract.return_value = "Text"
        mock_metrics.return_value = (1, 4)
        mock_save.return_value = {"success": True, "skipped": False}
        
        uploaded_files = [mock_file1, mock_file2]
        result = process_uploaded_files(uploaded_files, generate_summary=True)
        
        # Verify results
        assert result["successful"] == 1  # only first file
        assert result["skipped"] == 1     # second file is duplicate
        assert result["failed"] == 0
        
        # Verify OCR was called only once (for non-duplicate)
        assert mock_extract.call_count == 1


def test_processing_order():
    """Test that processing order is: hash -> check -> OCR -> save."""
    
    call_order = []
    
    def track_hash(*args, **kwargs):
        call_order.append("hash")
        return "test_hash"
    
    def track_check(*args, **kwargs):
        call_order.append("check")
        return False
    
    def track_extract(*args, **kwargs):
        call_order.append("extract")
        return "Text"
    
    def track_save(*args, **kwargs):
        call_order.append("save")
        return {"success": True, "skipped": False}
    
    with mock.patch("frontend.data_processing.calculate_md5_hash", side_effect=track_hash), \
         mock.patch("frontend.data_processing.check_duplicate_hash", side_effect=track_check), \
         mock.patch("frontend.data_processing.extract_text_from_pdf", side_effect=track_extract), \
         mock.patch("frontend.data_processing.calculate_text_metrics", return_value=(1, 4)), \
         mock.patch("frontend.data_processing.save_extracted_text_to_backend", side_effect=track_save):
        
        process_single_pdf("/path/test.pdf", "test.pdf", True)
        
        # Verify correct order: hash -> check -> extract -> save
        assert call_order == ["hash", "check", "extract", "save"]


def test_processing_order_duplicate_skips():
    """Test that duplicate detection stops processing before OCR."""
    
    call_order = []
    
    def track_hash(*args, **kwargs):
        call_order.append("hash")
        return "duplicate_hash"
    
    def track_check(*args, **kwargs):
        call_order.append("check")
        return True  # Indicates duplicate
    
    def track_extract(*args, **kwargs):
        call_order.append("extract")
        return "Text"
    
    with mock.patch("frontend.data_processing.calculate_md5_hash", side_effect=track_hash), \
         mock.patch("frontend.data_processing.check_duplicate_hash", side_effect=track_check), \
         mock.patch("frontend.data_processing.extract_text_from_pdf", side_effect=track_extract):
        
        process_single_pdf("/path/test.pdf", "test.pdf", True)
        
        # Verify processing stopped after duplicate check
        assert call_order == ["hash", "check"]
        # Extract should NOT have been called
        assert "extract" not in call_order
