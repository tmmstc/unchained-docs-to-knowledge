#!/usr/bin/env python3
"""
Streamlit app for PDF OCR processing with directory input and SQLite storage.
"""

import streamlit as st
import sqlite3
import os
import glob
import datetime
import pytesseract
import pdf2image
import tempfile
import traceback

# Database configuration
DATABASE_PATH = "pdf_ocr_database.db"


def init_database():
    """Initialize SQLite database with required schema"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pdf_extracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            extracted_text TEXT,
            created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()


def save_extracted_text(filename, extracted_text):
    """Save extracted text to SQLite database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO pdf_extracts (filename, extracted_text,
                                    created_timestamp)
            VALUES (?, ?, ?)
        """,
            (filename, extracted_text, datetime.datetime.now()),
        )

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using Tesseract OCR"""
    try:
        # Convert PDF to images
        with tempfile.TemporaryDirectory() as temp_dir:
            images = pdf2image.convert_from_path(
                pdf_path, output_folder=temp_dir, dpi=200
            )

            extracted_text = ""
            for i, image in enumerate(images):
                # Extract text from each page using Tesseract
                page_text = pytesseract.image_to_string(image, lang="eng")
                extracted_text += (
                    f"\n--- Page {i+1} ---\n{page_text}\n"
                )

            return extracted_text.strip()

    except Exception as e:
        raise Exception(f"OCR processing failed: {str(e)}")


def get_pdf_files_from_directory(directory_path):
    """Get all PDF files from the specified directory"""
    try:
        pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
        return pdf_files
    except Exception as e:
        st.error(f"Error reading directory: {str(e)}")
        return []


def display_database_records():
    """Display recent records from the database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT filename, created_timestamp,
                   SUBSTR(extracted_text, 1, 200) || '...' as preview
            FROM pdf_extracts
            ORDER BY created_timestamp DESC
            LIMIT 10
        """
        )

        records = cursor.fetchall()
        conn.close()

        if records:
            st.subheader("Recent Processed Files")
            for filename, timestamp, preview in records:
                with st.expander(f"{filename} - {timestamp}"):
                    st.text(preview)
        else:
            st.info("No processed files found in database.")

    except Exception as e:
        st.error(f"Error reading from database: {str(e)}")


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="PDF OCR Processor", page_icon="📄", layout="wide"
    )

    st.title("📄 PDF OCR Text Extractor")
    st.markdown(
        "Extract text from PDF files using Tesseract OCR and store in "
        "SQLite database"
    )

    # Initialize database
    init_database()

    # Directory input section
    st.header("Select Directory")
    directory_path = st.text_input(
        "Enter directory path containing PDF files:",
        placeholder="C:/path/to/pdf/directory",
    )

    if directory_path and os.path.exists(directory_path):
        pdf_files = get_pdf_files_from_directory(directory_path)

        if pdf_files:
            st.success(
                f"Found {len(pdf_files)} PDF files in the directory"
            )

            # Display found PDF files
            with st.expander("PDF Files Found"):
                for pdf_file in pdf_files:
                    st.text(os.path.basename(pdf_file))

            # Process files button
            if st.button("Process All PDF Files", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                successful_processes = 0
                failed_processes = 0

                for i, pdf_file in enumerate(pdf_files):
                    filename = os.path.basename(pdf_file)
                    status_text.text(f"Processing: {filename}")

                    try:
                        # Extract text from PDF
                        extracted_text = extract_text_from_pdf(pdf_file)

                        # Save to database
                        if save_extracted_text(filename, extracted_text):
                            successful_processes += 1
                            st.success(f"✅ Successfully processed: {filename}")
                        else:
                            failed_processes += 1
                            st.error(f"❌ Database save failed: {filename}")

                    except Exception as e:
                        failed_processes += 1
                        st.error(
                            f"❌ Processing failed for {filename}: {str(e)}"
                        )
                        with st.expander(f"Error details for {filename}"):
                            st.code(traceback.format_exc())

                    # Update progress
                    progress_bar.progress((i + 1) / len(pdf_files))

                # Final status
                status_text.text("Processing completed!")
                st.success(
                    f"Processing complete! ✅ {successful_processes} "
                    f"successful, ❌ {failed_processes} failed"
                )

        else:
            st.warning("No PDF files found in the specified directory")

    elif directory_path:
        st.error(
            "Directory does not exist. Please enter a valid directory path."
        )

    # Database viewer section
    st.header("Database Records")
    display_database_records()

    # Database statistics
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pdf_extracts")
        total_records = cursor.fetchone()[0]
        conn.close()

        st.metric("Total Processed Files", total_records)
    except Exception as e:
        st.error(f"Error getting database statistics: {str(e)}")


if __name__ == "__main__":
    main()
