"""
Test the text metrics calculation functionality from the PDF processor.
This tests the calculate_text_metrics function that extracts word count
and character length from processed PDF text.
"""

from shared.pdf_processor import calculate_text_metrics


class TestTextMetrics:
    def test_empty_text(self):
        """Test with empty string"""
        word_count, character_length = calculate_text_metrics("")
        assert word_count == 0
        assert character_length == 0

    def test_none_text(self):
        """Test with None input"""
        word_count, character_length = calculate_text_metrics(None)
        assert word_count == 0
        assert character_length == 0

    def test_simple_text(self):
        """Test with simple text"""
        text = "Hello world"
        word_count, character_length = calculate_text_metrics(text)
        assert word_count == 2
        assert character_length == 11

    def test_text_with_punctuation(self):
        """Test text with punctuation marks"""
        text = "Hello, world! How are you?"
        word_count, character_length = calculate_text_metrics(text)
        assert word_count == 5  # "Hello", "world", "How", "are", "you"
        assert character_length == 26

    def test_text_with_multiple_spaces(self):
        """Test text with multiple consecutive spaces"""
        text = "Hello    world   test"
        word_count, character_length = calculate_text_metrics(text)
        assert word_count == 3  # "Hello", "world", "test"
        assert character_length == 21  # All characters including extra spaces

    def test_text_with_newlines_and_tabs(self):
        """Test text with newlines and tabs"""
        text = "Hello\nworld\ttest"
        word_count, character_length = calculate_text_metrics(text)
        assert word_count == 3
        assert character_length == 16

    def test_text_with_numbers(self):
        """Test text with numbers mixed in"""
        text = "There are 123 items and 456 more"
        word_count, character_length = calculate_text_metrics(text)
        # "There", "are", "123", "items", "and", "456", "more"
        assert word_count == 7
        assert character_length == len(text)

    def test_only_punctuation(self):
        """Test with only punctuation marks"""
        text = "!@#$%^&*()"
        word_count, character_length = calculate_text_metrics(text)
        assert word_count == 0
        assert character_length == 10

    def test_only_whitespace(self):
        """Test with only whitespace characters"""
        text = "   \t\n   "
        word_count, character_length = calculate_text_metrics(text)
        assert word_count == 0
        assert character_length == 8

    def test_pdf_like_text(self):
        """Test with PDF-like text with page markers"""
        text = """
        --- Page 1 ---
        This is the first page with some content.

        --- Page 2 ---
        This is the second page with more content.
        """
        word_count, character_length = calculate_text_metrics(text)
        # Should count all words including "Page", "1", "2", etc.
        assert word_count > 10
        assert character_length == len(text)
