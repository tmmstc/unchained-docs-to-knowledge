"""
Create test database with sample records for UI testing
"""
import sqlite3
import datetime

DATABASE_PATH = "pdf_ocr_database.db"

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS pdf_extracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        extracted_text TEXT,
        word_count INTEGER,
        character_length INTEGER,
        summary TEXT,
        created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insert test record WITHOUT summary
cursor.execute("""
    INSERT INTO pdf_extracts (filename, extracted_text, word_count, character_length, created_timestamp)
    VALUES (?, ?, ?, ?, ?)
""", (
    'test_without_summary.pdf',
    'This is a test document for verifying the Generate Summary button appears correctly in the Streamlit UI. The button should only appear for documents that do not yet have a summary.',
    30,
    180,
    datetime.datetime.now()
))

# Insert test record WITH summary
cursor.execute("""
    INSERT INTO pdf_extracts (filename, extracted_text, word_count, character_length, summary, created_timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
""", (
    'test_with_summary.pdf',
    'This is another test document that already has a summary.',
    10,
    65,
    'This document already has a summary, so the Generate Summary button should NOT appear.',
    datetime.datetime.now()
))

# Insert another record WITHOUT summary
cursor.execute("""
    INSERT INTO pdf_extracts (filename, extracted_text, word_count, character_length, created_timestamp)
    VALUES (?, ?, ?, ?, ?)
""", (
    'another_test.pdf',
    'Another document without a summary to test multiple Generate Summary buttons with unique keys.',
    15,
    95,
    datetime.datetime.now()
))

conn.commit()

# Verify records
cursor.execute("SELECT id, filename, summary FROM pdf_extracts")
records = cursor.fetchall()

print("Test database created successfully!")
print("\nRecords in database:")
for record_id, filename, summary in records:
    summary_status = "HAS SUMMARY" if summary else "NO SUMMARY"
    print(f"  ID {record_id}: {filename} - {summary_status}")

conn.close()
