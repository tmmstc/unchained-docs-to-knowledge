# Document Summarization Feature

## Overview
This feature adds AI-powered summarization capabilities to the PDF OCR processing application. Users can generate summaries during document processing or on-demand for previously processed documents.

## Features Added

### 1. Streamlit Interface Enhancements

#### Batch Processing with Summarization
- **Checkbox Control**: Added "Enable summarization during processing" checkbox in the folder processing section
- **Conditional Processing**: When enabled, the application generates summaries for each PDF during batch processing
- **Status Updates**: UI provides feedback when summaries are being generated
- **Error Handling**: Gracefully handles summarization failures and continues processing without summary

#### On-Demand Summary Generation
- **Document List View**: Displays previously processed documents with summary status
- **Generate Summary Button**: Available for documents without summaries
- **Real-time Updates**: UI refreshes after summary generation to show the new summary
- **Summary Display**: Shows generated summaries in expandable document cards

### 2. Backend API Enhancements

#### New Endpoints

**GET /records/no-summary**
- Retrieves documents that don't have summaries yet
- Supports pagination with `limit` parameter (default: 100, max: 1000)
- Returns list of PDFRecord objects without summaries

**PUT /records/{record_id}/summary**
- Updates a specific document record with a newly generated summary
- Requires `generate=true` parameter
- Validates record exists and has extracted text
- Returns success status and generated summary

**Modified POST /process-pdf**
- Now accepts `generate_summary` boolean parameter (default: True)
- Conditionally invokes summarization logic based on parameter
- Stores summary in database during initial processing

### 3. Database Schema Updates

#### Migration Support
- Added `summary TEXT` column to `pdf_extracts` table
- Automatic migration if column doesn't exist
- Backward compatible with existing database records

#### New Database Functions
- `get_records_without_summary()`: Query records missing summaries
- `get_record_by_id()`: Retrieve specific record by ID
- `update_record_summary()`: Update summary for existing record

### 4. Summarization Pipeline

#### Langchain Integration
- Uses existing `summarizer.py` module with OpenAI-compatible API
- Supports text chunking for long documents
- Configurable model via environment variable
- Graceful fallback when API key not configured

## Usage

### Environment Configuration
```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE_URL=https://api.openai.com/v1  # Optional
SUMMARIZATION_MODEL=gpt-3.5-turbo  # Optional
```

### Streamlit Application

1. **Enable Summarization During Processing**:
   - Check "Enable summarization during processing" before clicking "Process All PDF Files"
   - Summaries will be generated and saved automatically

2. **Generate Summary On-Demand**:
   - Navigate to "Database Records" section
   - Find documents without summaries
   - Click "Generate Summary" button next to the document
   - Wait for summary generation (may take a few seconds)

### API Usage

1. **Process PDF with Summary**:
```python
import requests

response = requests.post("http://localhost:8000/process-pdf", json={
    "filename": "document.pdf",
    "extracted_text": "Document content here...",
    "word_count": 100,
    "character_length": 500,
    "generate_summary": True
})
```

2. **Get Documents Without Summaries**:
```python
response = requests.get("http://localhost:8000/records/no-summary?limit=50")
documents = response.json()
```

3. **Generate Summary for Existing Document**:
```python
response = requests.put(
    "http://localhost:8000/records/123/summary?generate=true"
)
summary_data = response.json()
```

## Testing

### Test Coverage
- Added 5 new tests for API endpoints
- Added 2 tests for Streamlit utility functions
- All existing tests continue to pass
- Total: 39 tests passing

### Run Tests
```bash
.\venv\Scripts\python.exe -m pytest tests/ -v
```

## Technical Implementation

### Asynchronous Processing
- Uses `asyncio.run()` for async summarization in Streamlit
- Backend endpoints use `async/await` for non-blocking operations

### Error Handling
- Graceful degradation when summarization fails
- Detailed logging for debugging
- User-friendly error messages

### Performance Considerations
- Summaries generated asynchronously
- Chunking for large documents to handle API limits
- Configurable timeouts and retries in httpx client

## Future Enhancements

Potential improvements for future versions:
- Batch summary generation endpoint
- Custom prompt templates for summaries
- Summary quality ratings
- Multi-language summary support
- Summary regeneration with different models
