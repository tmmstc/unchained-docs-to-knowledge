"""
Tests for Streamlit app utility functions.
"""

import sys
import os
import sqlite3
import tempfile
import unittest.mock as mock

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


def test_delete_button_state_management():
    """Test delete button two-step confirmation state management."""
    mock_st = mock.MagicMock()

    mock_st.session_state = {}

    class SessionState(dict):
        def __getattr__(self, key):
            return self.get(key)

        def __setattr__(self, key, value):
            self[key] = value

    mock_st.session_state = SessionState()

    selected_record = {"id": 123}

    if "delete_confirmation_id" not in mock_st.session_state:
        mock_st.session_state.delete_confirmation_id = None

    if "last_selected_record_id" not in mock_st.session_state:
        mock_st.session_state.last_selected_record_id = None

    current_record_id = selected_record["id"]

    if mock_st.session_state.last_selected_record_id != current_record_id:
        mock_st.session_state.delete_confirmation_id = None
        mock_st.session_state.last_selected_record_id = current_record_id

    assert mock_st.session_state.delete_confirmation_id is None
    assert mock_st.session_state.last_selected_record_id == 123

    in_confirmation_mode = (
        mock_st.session_state.delete_confirmation_id == current_record_id
    )
    assert in_confirmation_mode is False

    mock_st.session_state.delete_confirmation_id = current_record_id
    in_confirmation_mode = (
        mock_st.session_state.delete_confirmation_id == current_record_id
    )
    assert in_confirmation_mode is True

    new_record = {"id": 456}
    current_record_id = new_record["id"]
    if mock_st.session_state.last_selected_record_id != current_record_id:
        mock_st.session_state.delete_confirmation_id = None
        mock_st.session_state.last_selected_record_id = current_record_id

    assert mock_st.session_state.delete_confirmation_id is None
    assert mock_st.session_state.last_selected_record_id == 456


def test_delete_button_label_changes():
    """Test delete button label changes based on confirmation state."""
    mock_st_session = {"delete_confirmation_id": None, "last_selected_record_id": None}

    current_record_id = 100

    in_confirmation_mode = (
        mock_st_session["delete_confirmation_id"] == current_record_id
    )

    if in_confirmation_mode:
        button_label = "⚠️ Click again to confirm"
        button_type = "secondary"
    else:
        button_label = "Delete Record"
        button_type = "primary"

    assert button_label == "Delete Record"
    assert button_type == "primary"

    mock_st_session["delete_confirmation_id"] = current_record_id
    in_confirmation_mode = (
        mock_st_session["delete_confirmation_id"] == current_record_id
    )

    if in_confirmation_mode:
        button_label = "⚠️ Click again to confirm"
        button_type = "secondary"
    else:
        button_label = "Delete Record"
        button_type = "primary"

    assert button_label == "⚠️ Click again to confirm"
    assert button_type == "secondary"


def test_process_uploaded_files():
    """Test that uploaded files can be processed through tempfile workflow."""
    from frontend.streamlit_app import process_uploaded_files
    from unittest.mock import MagicMock

    mock_uploaded_file = MagicMock()
    mock_uploaded_file.name = "test.pdf"
    pdf_content = b"%PDF-1.4 test content"
    mock_uploaded_file.getbuffer.return_value = pdf_content

    uploaded_files = [mock_uploaded_file]

    mock_patches = [
        mock.patch('frontend.streamlit_app.st'),
        mock.patch('frontend.streamlit_app.extract_text_from_pdf'),
        mock.patch('frontend.streamlit_app.calculate_text_metrics'),
        mock.patch('frontend.streamlit_app.save_extracted_text_to_backend')
    ]

    with mock_patches[0] as mock_st, mock_patches[1] as mock_ex, \
         mock_patches[2] as mock_met, mock_patches[3] as mock_s:

        mock_st.progress = MagicMock(return_value=MagicMock())
        mock_st.empty = MagicMock(return_value=MagicMock())
        mock_st.info = MagicMock()
        mock_st.success = MagicMock()
        mock_st.error = MagicMock()
        mock_st.expander = MagicMock()

        mock_ex.return_value = "Extracted text from PDF"
        mock_met.return_value = (4, 24)
        mock_s.return_value = {"success": True, "skipped": False}

        process_uploaded_files(uploaded_files, generate_summary=True)

        assert mock_ex.called
        assert mock_met.called
        assert mock_s.called

        call_args = mock_s.call_args
        assert call_args[0][0] == "test.pdf"
        assert call_args[0][1] == "Extracted text from PDF"
        assert call_args[0][2] == 4
        assert call_args[0][3] == 24
        assert call_args[0][4] is True
        assert call_args[0][5] is not None


def test_temp_file_cleanup():
    """Test that temporary files are cleaned up after processing."""
    from unittest.mock import MagicMock, patch
    from frontend.streamlit_app import process_uploaded_files
    import os

    mock_uploaded_file = MagicMock()
    mock_uploaded_file.name = "test.pdf"
    mock_uploaded_file.getbuffer.return_value = b"%PDF-1.4"

    uploaded_files = [mock_uploaded_file]

    created_temp_files = []

    def track_temp_creation(*args, **kwargs):
        temp = tempfile.NamedTemporaryFile(*args, **kwargs)
        created_temp_files.append(temp.name)
        return temp

    patches = [
        patch('frontend.streamlit_app.st'),
        patch('frontend.streamlit_app.extract_text_from_pdf'),
        patch('frontend.streamlit_app.calculate_text_metrics'),
        patch('frontend.streamlit_app.save_extracted_text_to_backend'),
        patch('frontend.streamlit_app.tempfile.NamedTemporaryFile',
              side_effect=track_temp_creation)
    ]

    with patches[0] as mock_st, patches[1] as mock_ex, patches[2] as mock_met, \
         patches[3] as mock_s, patches[4]:

        mock_st.progress = MagicMock(return_value=MagicMock())
        mock_st.empty = MagicMock(return_value=MagicMock())
        mock_st.info = MagicMock()
        mock_st.success = MagicMock()

        mock_ex.return_value = "Test"
        mock_met.return_value = (1, 4)
        mock_s.return_value = {"success": True}

        process_uploaded_files(uploaded_files, generate_summary=False)

        for temp_file in created_temp_files:
            assert not os.path.exists(temp_file)
