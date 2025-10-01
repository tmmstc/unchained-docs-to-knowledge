"""
Tests for PDF processor functionality.
"""

import tempfile
import os
from shared.pdf_processor import calculate_text_metrics, calculate_md5_hash


class TestTextMetrics:
    """Test text metrics calculation."""

    def test_calculate_text_metrics_empty_text(self):
        """Test metrics calculation for empty text."""
        word_count, character_length = calculate_text_metrics("")
        assert word_count == 0
        assert character_length == 0

    def test_calculate_text_metrics_none_text(self):
        """Test metrics calculation for None text."""
        word_count, character_length = calculate_text_metrics(None)
        assert word_count == 0
        assert character_length == 0

    def test_calculate_text_metrics_simple_text(self):
        """Test metrics calculation for simple text."""
        text = "Hello world"
        word_count, character_length = calculate_text_metrics(text)
        assert word_count == 2
        assert character_length == 11

    def test_calculate_text_metrics_text_with_punctuation(self):
        """Test metrics calculation for text with punctuation."""
        text = "Hello, world! How are you?"
        word_count, character_length = calculate_text_metrics(text)
        assert word_count == 5
        assert character_length == 26

    def test_calculate_text_metrics_text_with_multiple_spaces(self):
        """Test metrics calculation for text with multiple spaces."""
        text = "Hello    world   test"
        word_count, character_length = calculate_text_metrics(text)
        assert word_count == 3
        assert character_length == 21


class TestMD5Hash:
    """Test MD5 hash calculation."""

    def test_calculate_md5_hash_same_content(self):
        """Test that same content produces same hash."""
        content = b"Test content for MD5 hash"

        with tempfile.NamedTemporaryFile(delete=False) as f1:
            f1.write(content)
            f1_path = f1.name

        with tempfile.NamedTemporaryFile(delete=False) as f2:
            f2.write(content)
            f2_path = f2.name

        try:
            hash1 = calculate_md5_hash(f1_path)
            hash2 = calculate_md5_hash(f2_path)
            assert hash1 == hash2
        finally:
            os.unlink(f1_path)
            os.unlink(f2_path)

    def test_calculate_md5_hash_different_content(self):
        """Test that different content produces different hash."""
        content1 = b"Test content 1"
        content2 = b"Test content 2"

        with tempfile.NamedTemporaryFile(delete=False) as f1:
            f1.write(content1)
            f1_path = f1.name

        with tempfile.NamedTemporaryFile(delete=False) as f2:
            f2.write(content2)
            f2_path = f2.name

        try:
            hash1 = calculate_md5_hash(f1_path)
            hash2 = calculate_md5_hash(f2_path)
            assert hash1 != hash2
        finally:
            os.unlink(f1_path)
            os.unlink(f2_path)

    def test_calculate_md5_hash_format(self):
        """Test that MD5 hash is in correct format."""
        content = b"Test content"

        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(content)
            f_path = f.name

        try:
            hash_value = calculate_md5_hash(f_path)
            assert len(hash_value) == 32
            assert all(c in '0123456789abcdef' for c in hash_value)
        finally:
            os.unlink(f_path)
