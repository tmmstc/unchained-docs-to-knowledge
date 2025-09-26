import re


def calculate_text_metrics(text):
    """Calculate word count and character length for extracted text"""
    if not text:
        return 0, 0

    # Character length (including whitespace and punctuation)
    character_length = len(text)

    # Word count - split by whitespace and filter out empty strings
    # This properly handles multiple spaces, tabs, newlines, and punctuation
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)

    return word_count, character_length


def test_calculate_text_metrics_empty():
    """Test metrics for empty text"""
    word_count, char_length = calculate_text_metrics("")
    assert word_count == 0
    assert char_length == 0


def test_calculate_text_metrics_none():
    """Test metrics for None text"""
    word_count, char_length = calculate_text_metrics(None)
    assert word_count == 0
    assert char_length == 0


def test_calculate_text_metrics_simple():
    """Test metrics for simple text"""
    text = "Hello world"
    word_count, char_length = calculate_text_metrics(text)
    assert word_count == 2
    assert char_length == 11


def test_calculate_text_metrics_with_punctuation():
    """Test metrics with punctuation"""
    text = "Hello, world! How are you?"
    word_count, char_length = calculate_text_metrics(text)
    assert word_count == 5  # punctuation should not count as words
    assert char_length == 26  # punctuation should count as characters


def test_calculate_text_metrics_multiple_whitespace():
    """Test metrics with multiple spaces, tabs, newlines"""
    text = "Hello    world\t\ttest\n\nnewline"
    word_count, char_length = calculate_text_metrics(text)
    assert word_count == 4
    assert char_length == len(text)


def test_calculate_text_metrics_numbers():
    """Test metrics with numbers mixed with words"""
    text = "There are 123 items and 456 more"
    word_count, char_length = calculate_text_metrics(text)
    assert word_count == 7  # numbers should count as words
    assert char_length == len(text)


def test_calculate_text_metrics_hyphenated():
    """Test metrics with hyphenated words"""
    text = "This is a well-formed sentence"
    word_count, char_length = calculate_text_metrics(text)
    # hyphenated words should be treated as separate words
    assert word_count == 6
    assert char_length == len(text)


def test_calculate_text_metrics_special_chars():
    """Test metrics with special characters"""
    text = "Email: user@example.com and phone: 555-1234"
    word_count, char_length = calculate_text_metrics(text)
    assert (
        word_count == 8
    )  # regex extracts: Email, user, example, com, and, phone, 555, 1234
    assert char_length == len(text)
