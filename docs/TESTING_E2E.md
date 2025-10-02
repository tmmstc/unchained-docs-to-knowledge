# End-to-End Testing Guide for Streamlit PDF OCR Application

## Overview

This document describes the end-to-end (E2E) testing suite for the Streamlit PDF OCR application with document summarization features. The tests use Selenium WebDriver to simulate real user interactions with the Streamlit interface.

## Test File

**Location**: `tests/test_streamlit_playwright.py`

Despite the filename suggesting Playwright, these tests use Selenium with Microsoft Edge WebDriver for better compatibility with Windows ARM64 architecture.

## Test Coverage

### 1. Opt-in Summarization During Processing
**Test**: `test_opt_in_summarization_during_processing`

Simulates the workflow:
1. Navigate to Streamlit app
2. Enter directory path containing PDF files
3. Enable "Enable summarization during processing" checkbox
4. Click "Process All PDF Files" button
5. Wait for processing to complete (up to 60 seconds)
6. Verify summaries appear in the UI's record display
7. Verify summaries are stored in the database

**Assertions**:
- Processing completion message appears
- "Recent Processed Files" section displays
- Document expanders contain "Summary:" sections
- Summary content is non-empty
- Database contains summary records for processed documents

### 2. On-Demand Summarization Workflow
**Test**: `test_on_demand_summarization_workflow`

Simulates the workflow:
1. Pre-populate database with a document without summary
2. Navigate to Streamlit app
3. Find the document in the "Recent Processed Files" section
4. Click the document expander to open it
5. Click "Generate Summary" button
6. Wait for "Generating summary..." spinner
7. Wait for success message (up to 60 seconds)
8. Verify summary appears in the UI after page refresh

**Assertions**:
- Document without summary is displayed
- "Generate Summary" button is visible and clickable
- Processing spinner appears during generation
- Success message "Summary generated and saved!" appears
- Summary is displayed in UI after refresh
- Database contains the generated summary

### 3. Summary Content Validation
**Test**: `test_summary_content_validation`

Tests that:
1. Pre-populated summaries display correctly in the UI
2. Summary content is meaningful and non-empty
3. UI elements correctly show summary data

**Assertions**:
- "Summary:" label is visible
- Summary text content appears in the document expander
- Summary content length is substantial (>20 characters)

### 4. Multiple Documents Summarization
**Test**: `test_multiple_documents_summarization`

Tests batch processing:
1. Process multiple PDFs with summarization enabled
2. Verify all documents receive summaries
3. Check database consistency

**Assertions**:
- All processed documents have summaries in database
- Summary count matches total document count
- At least 2 test documents are processed

### 5. UI Summary Display Elements
**Test**: `test_ui_summary_display_elements`

Validates UI structure:
1. Word Count metric is displayed
2. Characters metric is displayed
3. Summary markdown section appears
4. Preview textarea is visible and accessible

**Assertions**:
- All UI elements are present and visible
- Elements are properly structured in document expanders

### 6. Processing Without Summarization
**Test**: `test_processing_without_summarization`

Tests that:
1. Documents can be processed without summaries
2. Unchecked summarization checkbox works correctly
3. No summaries are generated when disabled

**Assertions**:
- All processed documents have NULL summaries in database
- Processing completes successfully without summarization

### 7. Generate Summary Button Availability
**Test**: `test_generate_summary_button_availability`

Tests conditional button display:
1. Documents with summaries do NOT show "Generate Summary" button
2. Documents without summaries DO show "Generate Summary" button

**Assertions**:
- Button visibility correctly reflects summary presence
- Documents with summaries show summary content instead

## Prerequisites

### 1. System Requirements
- Windows (tested on Windows ARM64)
- Python 3.8+
- Microsoft Edge browser installed
- Tesseract OCR installed and in PATH
- Poppler installed and in PATH

### 2. Python Dependencies
```bash
pip install selenium webdriver-manager pytest pytest-asyncio
```

### 3. Running Services
The Streamlit app must be running on `http://localhost:8501` before executing tests.

**Start the Streamlit app**:
```bash
.\venv\Scripts\python.exe -m streamlit run streamlit_app.py --server.port 8501
```

Or use the run script:
```bash
python run_both.py
```

## Running the Tests

### Run All E2E Tests
```bash
.\venv\Scripts\python.exe -m pytest tests/test_streamlit_playwright.py -v
```

### Run Specific Test
```bash
.\venv\Scripts\python.exe -m pytest tests/test_streamlit_playwright.py::test_opt_in_summarization_during_processing -v
```

### Run Tests with Markers
```bash
# Run only e2e tests
.\venv\Scripts\python.exe -m pytest -m e2e -v

# Skip e2e tests
.\venv\Scripts\python.exe -m pytest -m "not e2e" -v
```

### Run Tests with Visible Browser (Non-headless)
To debug tests visually, modify the `browser` fixture in the test file:

```python
@pytest.fixture(scope="function")
def browser():
    edge_options = Options()
    # edge_options.add_argument("--headless=new")  # Comment this out
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Edge(options=edge_options)
    driver.set_page_load_timeout(60)
    yield driver
    driver.quit()
```

## Test Database

Tests use a separate database file: `pdf_ocr_database_test.db`

This database:
- Is created fresh for each test function
- Is automatically cleaned up after each test
- Does not interfere with the main application database

## Test Fixtures

### `test_pdf_directory`
- Scope: module
- Creates a temporary directory with 2 test PDF files
- Files are minimal valid PDFs for testing OCR processing
- Cleaned up after all tests complete

### `test_database`
- Scope: function
- Creates a fresh SQLite database for each test
- Ensures test isolation
- Cleaned up after each test

### `browser`
- Scope: function
- Creates a headless Edge WebDriver instance
- Configured with optimal settings for testing
- Automatically quits after each test

## Waits and Timeouts

The tests use explicit waits to handle asynchronous operations:

| Operation | Timeout | Description |
|-----------|---------|-------------|
| Page load | 60s | Initial Streamlit app loading |
| Element presence | 10s | Standard UI element wait |
| Processing completion | 60s | PDF processing and summarization |
| Spinner appearance | 5s | Loading indicators |
| Page refresh | 2s | Post-action UI stabilization |

## Common Issues and Troubleshooting

### Issue: Tests Fail with "Connection Refused"
**Solution**: Ensure Streamlit app is running on localhost:8501 before executing tests.

### Issue: Tests Timeout Waiting for Elements
**Causes**:
- Streamlit not fully loaded
- UI elements changed
- Network issues

**Solutions**:
- Increase timeout values in `WebDriverWait`
- Check Streamlit console for errors
- Inspect page source to verify element selectors

### Issue: Browser Opens But Tests Fail
**Causes**:
- Element selectors changed in Streamlit version
- Timing issues with dynamic content

**Solutions**:
- Run tests in non-headless mode to debug visually
- Add explicit waits before interactions
- Check Streamlit testid attributes

### Issue: Database Errors
**Causes**:
- Test database not cleaned up
- File permissions
- Database schema mismatch

**Solutions**:
- Delete `pdf_ocr_database_test.db` manually
- Ensure write permissions in test directory
- Verify database schema in fixtures

### Issue: WebDriver Not Found
**Error**: `selenium.common.exceptions.SessionNotCreatedException`

**Solutions**:
```bash
# Install/update webdriver-manager
pip install --upgrade webdriver-manager

# Or manually install Edge WebDriver
# Download from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
```

## Environment Variables for Testing

Set these in your environment or `.env` file:

```bash
# For summarization tests
OPENAI_API_KEY=your-test-api-key
OPENAI_API_BASE_URL=https://api.openai.com/v1
SUMMARIZATION_MODEL=gpt-3.5-turbo

# For test database path (optional)
DATABASE_PATH=pdf_ocr_database_test.db
```

## CI/CD Considerations

For continuous integration:

1. **Skip E2E Tests by Default**:
   ```bash
   pytest -m "not e2e"
   ```

2. **Run E2E Tests in Separate Pipeline**:
   - Start services in background
   - Wait for health check
   - Execute E2E tests
   - Tear down services

3. **Use Docker for Consistency**:
   ```dockerfile
   FROM python:3.13-slim
   RUN apt-get update && apt-get install -y \
       tesseract-ocr \
       poppler-utils \
       chromium-driver
   # ... rest of Dockerfile
   ```

4. **Parallel Execution**:
   ```bash
   pytest tests/test_streamlit_playwright.py -n 4
   ```

## Test Maintenance

### Updating Tests After UI Changes

1. **Element Selectors**: If Streamlit updates change element structure, update XPath/CSS selectors
2. **Timeouts**: Adjust based on performance characteristics
3. **Assertions**: Verify expected text matches current UI labels

### Adding New Tests

Follow this template:

```python
@pytest.mark.e2e
@pytest.mark.skip(reason="Requires Streamlit app running on localhost:8501")
def test_new_feature(browser, test_database):
    """
    Test description
    """
    browser.get("http://localhost:8501")
    wait_for_streamlit_ready(browser)
    
    # Test implementation
    # ...
    
    # Assertions
    assert expected_condition
```

## Performance Benchmarks

Expected test execution times:

| Test | Duration | Notes |
|------|----------|-------|
| `test_opt_in_summarization_during_processing` | 60-90s | Depends on PDF processing + summarization |
| `test_on_demand_summarization_workflow` | 30-60s | Depends on summarization API response |
| `test_summary_content_validation` | 5-10s | No processing, just UI validation |
| `test_multiple_documents_summarization` | 90-120s | Batch processing multiple PDFs |
| `test_ui_summary_display_elements` | 5-10s | UI-only test |
| `test_processing_without_summarization` | 30-45s | PDF processing without summarization |
| `test_generate_summary_button_availability` | 5-10s | UI-only test |

Total suite execution: ~4-6 minutes

## Related Documentation

- [SUMMARY_FEATURE.md](SUMMARY_FEATURE.md) - Summarization feature overview
- [TESTING_SUMMARY.md](TESTING_SUMMARY.md) - Unit and integration tests
- [README.md](README.md) - General setup and usage
- [AGENTS.md](AGENTS.md) - Repository-specific agent instructions
