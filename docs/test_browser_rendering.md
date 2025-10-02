# Manual Browser Testing Guide for Streamlit UI

## Test Checklist

### 1. Initial Page Load (localhost:8501)
- [ ] Page loads without errors
- [ ] Title "PDF OCR Text Extractor" is visible
- [ ] Database statistics section appears at bottom

### 2. Summarization Controls - Folder Processing Section

#### Location: Below directory path input
Expected UI elements:
```
Select Directory
[Text Input: Enter directory path containing PDF files...]
[x] Enable summarization during processing
    Generate AI-powered summaries of extracted text (requires API key)
```

**Test Steps:**
1. Navigate to the directory input section
2. Verify checkbox is visible and labeled "Enable summarization during processing"
3. Verify help text shows on hover: "Generate AI-powered summaries..."
4. Test checkbox interaction (click to enable/disable)
5. Verify checkbox state persists while entering directory path

**Expected Behavior:**
- Checkbox appears BEFORE entering directory path
- Checkbox is UNchecked by default (value=False)
- Checkbox works independently of directory selection

### 3. On-Demand Summarization - Database Records Section

#### Location: Within "Recent Processed Files" expandable cards

**Test Steps for Records WITHOUT Summary:**
1. Scroll to "Database Records" section
2. Expand a record that doesn't have a summary
3. Look for "Generate Summary" button

Expected UI:
```
📄 filename.pdf - 2024-01-01 12:00:00
  > [Expanded]
    Word Count: 100     Characters: 500
    [Button: Generate Summary]
    Preview: [text area with preview]
```

**Expected Behavior:**
- Button only appears if:
  - Record has NO summary
  - SUMMARIZER_AVAILABLE is True
  - extracted_text exists
- Button has unique key: `gen_summary_{record_id}`
- Clicking button shows spinner with "Generating summary..."
- After success, shows "Summary generated and saved!" and page reloads

**Test Steps for Records WITH Summary:**
1. Expand a record that HAS a summary

Expected UI:
```
📄 filename.pdf - 2024-01-01 12:00:00
  > [Expanded]
    Word Count: 100     Characters: 500
    **Summary:**
    [Summary text content displayed here]
    Preview: [text area with preview]
```

**Expected Behavior:**
- No "Generate Summary" button appears
- Summary is displayed with bold "**Summary:**" header
- Summary text is shown using st.write()

### 4. Conditional Logic Tests

**Test Case A: Summarization Disabled**
1. Leave "Enable summarization during processing" UNchecked
2. Enter valid directory with PDFs
3. Click "Process All PDF Files"
4. Expected: No "Generating summary..." messages during processing

**Test Case B: Summarization Enabled**
1. Check "Enable summarization during processing"
2. Enter valid directory with PDFs
3. Click "Process All PDF Files"
4. Expected: Status shows "Generating summary for: filename.pdf" for each file
5. Expected: Success messages include "(with summary)" suffix

**Test Case C: Summarizer Not Available (no API key)**
1. Ensure no OPENAI_API_KEY in environment
2. Check "Enable summarization during processing"
3. Process files
4. Expected: Processing continues but summaries are truncated/fallback versions

### 5. Layout Tests

**Verify Element Ordering:**
1. Page Title
2. Description text
3. "Select Directory" header
4. Directory path input
5. **Summarization checkbox** ← Should be here
6. Directory validation / PDF list
7. "Process All PDF Files" button
8. "Database Records" header
9. Recent files with expand/collapse

**Verify No Hidden Elements:**
- Check browser inspector (F12) for any elements with:
  - `display: none`
  - `visibility: hidden`
  - Conditional rendering that might hide controls

### 6. State Management Tests

**Test Button Keys:**
- Multiple records with "Generate Summary" buttons should have unique keys
- Format: `gen_summary_{record_id}` where record_id is the database ID
- No key conflicts should occur

**Test Preview Text Areas:**
- Each preview should have unique key: `preview_{record_id}`
- Text areas should display first 200 chars + "..."

### 7. Error Conditions

**Test Missing Import:**
- Check logs for "Summarizer module not available" warning
- If SUMMARIZER_AVAILABLE = False, verify:
  - Checkbox still appears (user can check it)
  - "Generate Summary" buttons don't appear
  - Processing with checkbox enabled shows appropriate message

**Test API Failures:**
- Enable summarization with invalid/missing API key
- Verify graceful error handling
- Check that processing continues despite summary failures

## Browser Testing Commands

### Open Browser Console (F12)
Check for:
- JavaScript errors (red messages)
- Streamlit connection issues
- Warning messages

### Network Tab
Monitor:
- WebSocket connection to Streamlit server
- Any failed requests

### Elements Tab
Inspect:
- Checkbox input element exists in DOM
- Button elements with correct keys
- No conditional rendering hiding elements

## Expected Log Output

During processing with summarization enabled:
```
📁 User selected directory: C:/path/to/pdfs
🚀 Starting batch processing of X PDF files
🔄 Processing file 1/X: filename.pdf
🔍 Starting OCR extraction for: filename.pdf
📝 Generating summary for: filename.pdf
✅ Summary generated: 250 characters
💾 Saving extracted text for: filename.pdf
✅ Successfully processed: filename.pdf
```

## Issues to Watch For

1. **Checkbox not visible** - Check if it's accidentally inside a conditional block
2. **Button not appearing** - Verify SUMMARIZER_AVAILABLE flag and record has no summary
3. **Button click does nothing** - Check browser console for errors
4. **Page doesn't reload after summary** - st.rerun() might be failing
5. **Duplicate key warnings** - Multiple buttons/widgets with same key
6. **Layout broken** - CSS or Streamlit version issues

## Success Criteria

✅ All UI elements are visible without interaction
✅ Checkbox appears and functions correctly
✅ Generate Summary buttons appear for appropriate records
✅ Clicking buttons triggers summarization
✅ Page updates after summary generation
✅ No console errors or warnings
✅ Graceful error handling for API failures
