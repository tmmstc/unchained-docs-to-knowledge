"""
Tests for Streamlit app utility functions.
"""

import sys
import os
import sqlite3
import tempfile

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import functions from streamlit_app
# Note: We need to be careful with imports since streamlit_app uses st commands


def test_calculate_text_metrics():
    """Test text metrics calculation function."""
    # Import the function directly from the deprecated standalone app
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "streamlit_app",
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "deprecated",
            "streamlit_app.py"
        )
    )
    module = importlib.util.module_from_spec(spec)

    # Mock streamlit to avoid errors
    sys.modules['streamlit'] = type(sys)('streamlit')
    sys.modules['streamlit'].set_page_config = lambda **kwargs: None

    spec.loader.exec_module(module)

    # Test empty text
    word_count, char_length = module.calculate_text_metrics("")
    assert word_count == 0
    assert char_length == 0

    # Test simple text
    word_count, char_length = module.calculate_text_metrics("Hello world")
    assert word_count == 2
    assert char_length == 11

    # Test text with punctuation
    text = "Hello, world! How are you?"
    word_count, char_length = module.calculate_text_metrics(text)
    assert word_count == 5
    assert char_length == len(text)


def test_update_document_summary():
    """Test update_document_summary function."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "streamlit_app",
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "deprecated",
            "streamlit_app.py"
        )
    )
    module = importlib.util.module_from_spec(spec)

    # Mock streamlit to avoid errors
    sys.modules['streamlit'] = type(sys)('streamlit')
    sys.modules['streamlit'].set_page_config = lambda **kwargs: None

    spec.loader.exec_module(module)

    # Create a temporary database
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(temp_db_fd)

    # Override DATABASE_PATH
    original_db_path = module.DATABASE_PATH
    module.DATABASE_PATH = temp_db_path

    try:
        # Initialize database
        module.init_database()

        # Insert a test record
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO pdf_extracts
            (filename, extracted_text, word_count, character_length)
            VALUES (?, ?, ?, ?)
            """,
            ("test.pdf", "Test text", 2, 9)
        )
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()

        # Update the summary
        result = module.update_document_summary(
            record_id,
            "This is a test summary"
        )
        assert result is True

        # Verify the update
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT summary FROM pdf_extracts WHERE id = ?",
            (record_id,)
        )
        summary = cursor.fetchone()[0]
        conn.close()

        assert summary == "This is a test summary"

    finally:
        # Restore original path and cleanup
        module.DATABASE_PATH = original_db_path
        os.unlink(temp_db_path)
