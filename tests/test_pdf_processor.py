"""
Tests for PDF processor functionality.
"""

from shared.pdf_processor import calculate_text_metrics


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
