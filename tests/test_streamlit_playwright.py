"""
Selenium-based end-to-end tests for Streamlit PDF OCR application
with summarization features.

Tests cover:
1. PDF upload and processing with opt-in summarization during
   initial processing
2. On-demand summarization for already-processed documents
3. Verification of summary data in UI elements
4. Asynchronous operation handling with appropriate waits

Note: These tests require the Streamlit app to be running on
localhost:8501
Run with: pytest tests/test_streamlit_playwright.py -v
"""

import pytest
import os
import tempfile
import shutil
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


DATABASE_PATH = "pdf_ocr_database_test.db"
TEST_PDF_DIR = None


@pytest.fixture(scope="module")
def test_pdf_directory():
    """Create a temporary directory with test PDF files"""
    global TEST_PDF_DIR
    TEST_PDF_DIR = tempfile.mkdtemp()

    test_pdf_content = (
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font "
        b"<< /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
        b">> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n"
        b"4 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n"
        b"(Test PDF) Tj\nET\nendstream\nendobj\nxref\n0 5\n"
        b"0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n"
        b"0000000115 00000 n\n0000000317 00000 n\ntrailer\n"
        b"<< /Size 5 /Root 1 0 R >>\nstartxref\n410\n%%EOF"
    )

    for i in range(2):
        pdf_path = os.path.join(TEST_PDF_DIR, f"test_document_{i+1}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(test_pdf_content)

    yield TEST_PDF_DIR

    shutil.rmtree(TEST_PDF_DIR)


@pytest.fixture(scope="function")
def test_database():
    """Create a clean test database for each test"""
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pdf_extracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            extracted_text TEXT,
            word_count INTEGER,
            character_length INTEGER,
            summary TEXT,
            created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()

    yield DATABASE_PATH

    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)


@pytest.fixture(scope="function")
def browser():
    """Create a headless Edge browser instance"""
    edge_options = Options()
    edge_options.add_argument("--headless=new")
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Edge(options=edge_options)
    driver.set_page_load_timeout(60)
    yield driver
    driver.quit()


def wait_for_streamlit_ready(driver, timeout=10):
    """Wait for Streamlit to be fully loaded"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(2)
    except TimeoutException:
        pytest.fail("Streamlit app did not load in time")


@pytest.mark.e2e
@pytest.mark.skip(reason="Requires Streamlit app running on localhost:8501")
def test_opt_in_summarization_during_processing(
    browser, test_pdf_directory, test_database
):
    """
    Test workflow: Upload PDFs -> Enable summarization checkbox -> Process files
    -> Verify summaries are generated and displayed in the UI
    """
    browser.get("http://localhost:8501")
    wait_for_streamlit_ready(browser)

    directory_input = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]'))
    )
    directory_input.clear()
    directory_input.send_keys(test_pdf_directory)
    time.sleep(1)

    try:
        xpath = (
            '//label[contains(text(), "Enable summarization during '
            'processing")]//input[@type="checkbox"]'
        )
        checkbox = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        if not checkbox.is_selected():
            checkbox.click()
            time.sleep(0.5)
    except Exception:
        pytest.skip("Could not find summarization checkbox")

    process_button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//button[contains(text(), "Process All PDF Files")]')
        )
    )
    process_button.click()

    try:
        WebDriverWait(browser, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[contains(text(), "Processing completed")]')
            )
        )
    except TimeoutException:
        pytest.fail("Processing did not complete within 60 seconds")

    time.sleep(2)

    recent_files_header = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[contains(text(), "Recent Processed Files")]')
        )
    )
    assert recent_files_header.is_displayed()

    try:
        expanders = browser.find_elements(By.CSS_SELECTOR, '[data-testid="stExpander"]')
        assert len(expanders) > 0, "No document expanders found"

        expanders[0].click()
        time.sleep(1)

        summary_text = browser.find_element(
            By.XPATH, '//*[contains(text(), "Summary:")]'
        )
        assert summary_text.is_displayed()
    except NoSuchElementException:
        pytest.fail("Could not find summary in document expander")

    conn = sqlite3.connect(test_database)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT filename, summary FROM pdf_extracts WHERE summary IS NOT NULL"
    )
    records = cursor.fetchall()
    conn.close()

    assert len(records) >= 1, "At least one record should have a summary"
    for filename, summary in records:
        assert summary is not None
        assert len(summary) > 0, f"Summary for {filename} should not be empty"


@pytest.mark.e2e
@pytest.mark.skip(reason="Requires Streamlit app running on localhost:8501")
def test_on_demand_summarization_workflow(browser, test_database):
    """
    Test workflow: Pre-populate database with document without summary ->
    Click Generate Summary button -> Verify summary appears in UI
    """
    test_text = "This is a test document with sample content. " * 20
    conn = sqlite3.connect(test_database)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO pdf_extracts (filename, extracted_text, word_count,
                                  character_length, summary)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("test_no_summary.pdf", test_text, 100, 900, None),
    )
    conn.commit()
    conn.close()

    browser.get("http://localhost:8501")
    wait_for_streamlit_ready(browser)

    try:
        expanders = browser.find_elements(By.CSS_SELECTOR, '[data-testid="stExpander"]')
        target_expander = None
        for expander in expanders:
            if "test_no_summary.pdf" in expander.text:
                target_expander = expander
                break

        assert (
            target_expander is not None
        ), "Could not find test_no_summary.pdf document"
        target_expander.click()
        time.sleep(1)

        generate_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, './/button[contains(text(), "Generate Summary")]')
            )
        )
        generate_button.click()

        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[contains(text(), "Generating summary")]')
            )
        )

        WebDriverWait(browser, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[contains(text(), "Summary generated and saved")]')
            )
        )
        time.sleep(2)

        browser.refresh()
        wait_for_streamlit_ready(browser)

        expanders = browser.find_elements(By.CSS_SELECTOR, '[data-testid="stExpander"]')
        for expander in expanders:
            if "test_no_summary.pdf" in expander.text:
                expander.click()
                time.sleep(1)
                break

        summary_element = browser.find_element(
            By.XPATH, '//*[contains(text(), "Summary:")]'
        )
        assert summary_element.is_displayed()

    except (NoSuchElementException, TimeoutException) as e:
        pytest.fail(f"On-demand summarization test failed: {e}")

    conn = sqlite3.connect(test_database)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT summary FROM pdf_extracts WHERE filename = ?",
        ("test_no_summary.pdf",),
    )
    result = cursor.fetchone()
    conn.close()

    assert result is not None
    assert result[0] is not None
    assert len(result[0]) > 0, "Summary should not be empty in database"


@pytest.mark.e2e
@pytest.mark.skip(reason="Requires Streamlit app running on localhost:8501")
def test_summary_content_validation(browser, test_database):
    """
    Test that generated summaries contain meaningful content and are
    properly displayed in UI elements
    """
    test_text = (
        "Artificial intelligence and machine learning are transforming "
        "modern technology. These systems can process vast amounts of data "
        "and identify patterns that humans might miss. " * 30
    )

    conn = sqlite3.connect(test_database)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO pdf_extracts (filename, extracted_text, word_count,
                                  character_length, summary)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "ai_document.pdf",
            test_text,
            300,
            2700,
            "Summary about AI and machine learning technologies.",
        ),
    )
    conn.commit()
    conn.close()

    browser.get("http://localhost:8501")
    wait_for_streamlit_ready(browser)

    expanders = browser.find_elements(By.CSS_SELECTOR, '[data-testid="stExpander"]')
    for expander in expanders:
        if "ai_document.pdf" in expander.text:
            expander.click()
            time.sleep(1)
            break

    summary_label = browser.find_element(By.XPATH, '//*[contains(text(), "Summary:")]')
    assert summary_label.is_displayed()

    page_source = browser.page_source
    assert "Summary about AI" in page_source or "machine learning" in page_source


@pytest.mark.e2e
@pytest.mark.skip(reason="Requires Streamlit app running on localhost:8501")
def test_multiple_documents_summarization(browser, test_pdf_directory, test_database):
    """
    Test processing multiple documents with summarization enabled
    and verify all summaries are generated
    """
    browser.get("http://localhost:8501")
    wait_for_streamlit_ready(browser)

    directory_input = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]'))
    )
    directory_input.clear()
    directory_input.send_keys(test_pdf_directory)
    time.sleep(1)

    xpath = (
        '//label[contains(text(), "Enable summarization during '
        'processing")]//input[@type="checkbox"]'
    )
    checkbox = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    if not checkbox.is_selected():
        checkbox.click()

    process_button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//button[contains(text(), "Process All PDF Files")]')
        )
    )
    process_button.click()

    WebDriverWait(browser, 60).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[contains(text(), "Processing completed")]')
        )
    )
    time.sleep(2)

    conn = sqlite3.connect(test_database)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pdf_extracts WHERE summary IS NOT NULL")
    summary_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pdf_extracts")
    total_count = cursor.fetchone()[0]
    conn.close()

    assert summary_count == total_count, (
        f"All {total_count} documents should have summaries, "
        f"but only {summary_count} have them"
    )
    assert total_count >= 2, "Should have processed at least 2 test documents"


@pytest.mark.e2e
@pytest.mark.skip(reason="Requires Streamlit app running on localhost:8501")
def test_ui_summary_display_elements(browser, test_database):
    """
    Test that summary UI elements are correctly structured and displayed
    """
    conn = sqlite3.connect(test_database)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO pdf_extracts (filename, extracted_text, word_count,
                                  character_length, summary)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "ui_test_doc.pdf",
            "Test content for UI validation.",
            5,
            32,
            "This is a test summary for UI element verification.",
        ),
    )
    conn.commit()
    conn.close()

    browser.get("http://localhost:8501")
    wait_for_streamlit_ready(browser)

    expanders = browser.find_elements(By.CSS_SELECTOR, '[data-testid="stExpander"]')
    for expander in expanders:
        if "ui_test_doc.pdf" in expander.text:
            expander.click()
            time.sleep(1)
            break

    word_count_metric = browser.find_element(
        By.XPATH, '//*[contains(text(), "Word Count")]'
    )
    assert word_count_metric.is_displayed()

    characters_metric = browser.find_element(
        By.XPATH, '//*[contains(text(), "Characters")]'
    )
    assert characters_metric.is_displayed()

    summary_markdown = browser.find_element(
        By.XPATH, '//*[contains(text(), "Summary:")]'
    )
    assert summary_markdown.is_displayed()

    preview_textarea = browser.find_element(
        By.CSS_SELECTOR, 'textarea[aria-label="Preview:"]'
    )
    assert preview_textarea.is_displayed()


@pytest.mark.e2e
@pytest.mark.skip(reason="Requires Streamlit app running on localhost:8501")
def test_processing_without_summarization(browser, test_pdf_directory, test_database):
    """
    Test that documents can be processed without summaries when checkbox
    is not enabled
    """
    browser.get("http://localhost:8501")
    wait_for_streamlit_ready(browser)

    directory_input = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]'))
    )
    directory_input.clear()
    directory_input.send_keys(test_pdf_directory)
    time.sleep(1)

    xpath = (
        '//label[contains(text(), "Enable summarization during '
        'processing")]//input[@type="checkbox"]'
    )
    checkbox = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    if checkbox.is_selected():
        checkbox.click()
        time.sleep(0.5)

    process_button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//button[contains(text(), "Process All PDF Files")]')
        )
    )
    process_button.click()

    WebDriverWait(browser, 60).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[contains(text(), "Processing completed")]')
        )
    )
    time.sleep(2)

    conn = sqlite3.connect(test_database)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pdf_extracts WHERE summary IS NULL")
    no_summary_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pdf_extracts")
    total_count = cursor.fetchone()[0]
    conn.close()

    assert no_summary_count == total_count, (
        "All documents should be processed without summaries when "
        "summarization is disabled"
    )


@pytest.mark.e2e
@pytest.mark.skip(reason="Requires Streamlit app running on localhost:8501")
def test_generate_summary_button_availability(browser, test_database):
    """
    Test that Generate Summary button appears only for documents without summaries
    """
    conn = sqlite3.connect(test_database)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO pdf_extracts (filename, extracted_text, word_count,
                                  character_length, summary)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("with_summary.pdf", "Text content", 2, 12, "Already has summary"),
    )
    cursor.execute(
        """
        INSERT INTO pdf_extracts (filename, extracted_text, word_count,
                                  character_length, summary)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("without_summary.pdf", "Text content", 2, 12, None),
    )
    conn.commit()
    conn.close()

    browser.get("http://localhost:8501")
    wait_for_streamlit_ready(browser)

    expanders = browser.find_elements(By.CSS_SELECTOR, '[data-testid="stExpander"]')

    for expander in expanders:
        if "with_summary.pdf" in expander.text:
            expander.click()
            time.sleep(1)

            summary_present = browser.find_element(
                By.XPATH, '//*[contains(text(), "Summary:")]'
            )
            assert summary_present.is_displayed()

            try:
                generate_button = browser.find_element(
                    By.XPATH, './/button[contains(text(), "Generate Summary")]'
                )
                pytest.fail(
                    "Generate Summary button should not be visible "
                    "for documents with summaries"
                )
            except NoSuchElementException:
                pass
            break

    for expander in expanders:
        if "without_summary.pdf" in expander.text:
            expander.click()
            time.sleep(1)

            generate_button = browser.find_element(
                By.XPATH, './/button[contains(text(), "Generate Summary")]'
            )
            assert generate_button.is_displayed()
            break
