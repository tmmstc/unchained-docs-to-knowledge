"""
Manual verification script to test hash functionality.
This script can be run to verify that hashes are being stored correctly.
"""

import tempfile
import os
from pathlib import Path


def create_test_pdf():
    """Create a simple test PDF file"""
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=False) as f:
        # Simple PDF content
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Document) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000214 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
308
%%EOF
"""
        f.write(pdf_content)
        return f.name


def test_hash_in_database():
    """Test that hash values are correctly stored in database"""
    from app.pdf_processor import calculate_md5_hash, calculate_text_metrics
    from app.database import init_database, save_extracted_text, get_recent_records
    import app.database

    # Create temporary database
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(temp_db_fd)

    original_db_path = app.database.DATABASE_PATH
    app.database.DATABASE_PATH = temp_db_path

    try:
        # Initialize database
        init_database()

        # Create test PDF
        test_pdf = create_test_pdf()

        try:
            # Calculate hash
            md5_hash = calculate_md5_hash(test_pdf)
            print(f"[OK] Hash calculated: {md5_hash}")

            # Simulate extracted text
            extracted_text = "This is a test document for hash verification."
            word_count, character_length = calculate_text_metrics(extracted_text)

            # Save to database
            success = save_extracted_text(
                filename="test_verification.pdf",
                extracted_text=extracted_text,
                word_count=word_count,
                character_length=character_length,
                md5_hash=md5_hash,
            )

            if not success:
                print("[FAIL] Failed to save to database")
                return False

            print("[OK] Saved to database")

            # Retrieve and verify
            records = get_recent_records(limit=1)

            if not records:
                print("[FAIL] No records found")
                return False

            record = records[0]

            # Verify hash is present
            if record.get("md5_hash") == md5_hash:
                print(f"[OK] Hash correctly stored in database: {record['md5_hash']}")
            else:
                print(
                    f"[FAIL] Hash mismatch! Expected: {md5_hash}, Got: {record.get('md5_hash')}"
                )
                return False

            # Verify other fields
            if record["filename"] == "test_verification.pdf":
                print(f"[OK] Filename correct: {record['filename']}")
            else:
                print(f"[FAIL] Filename mismatch: {record['filename']}")
                return False

            if record["word_count"] == word_count:
                print(f"[OK] Word count correct: {record['word_count']}")
            else:
                print(f"[FAIL] Word count mismatch: {record['word_count']}")
                return False

            print("\n[OK] All verifications passed!")
            print("\nRecord details:")
            print(f"  ID: {record['id']}")
            print(f"  Filename: {record['filename']}")
            print(f"  MD5 Hash: {record['md5_hash']}")
            print(f"  Word Count: {record['word_count']}")
            print(f"  Character Length: {record['character_length']}")

            return True

        finally:
            os.unlink(test_pdf)

    finally:
        app.database.DATABASE_PATH = original_db_path
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


if __name__ == "__main__":
    print("Testing hash storage in database...\n")
    success = test_hash_in_database()

    if success:
        print("\n=== TEST PASSED ===")
    else:
        print("\n=== TEST FAILED ===")
