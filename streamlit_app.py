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
import re
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_PATH = "pdf_ocr_database.db"

logger.info("🌟 Streamlit PDF OCR Standalone App starting up")
logger.info(f"🗄️ Database path: {DATABASE_PATH}")
logger.info("📱 Application: PDF OCR processing with SQLite storage")


def init_database():
    """Initialize SQLite database with required schema"""
    logger.info("🗄️ Initializing SQLite database")
    logger.info(f"🗄️ Database location: {DATABASE_PATH}")
    
    try:
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
                created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


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


def save_extracted_text(filename, extracted_text):
    """Save extracted text to SQLite database with metrics"""
    logger.info(f"💾 Saving extracted text for: {filename}")
    
    try:
        # Calculate metrics
        word_count, character_length = calculate_text_metrics(extracted_text)
        logger.info(f"📊 Text metrics: {word_count} words, {character_length} characters")

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO pdf_extracts (filename, extracted_text, word_count,
                                    character_length, created_timestamp)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                filename,
                extracted_text,
                word_count,
                character_length,
                datetime.datetime.now(),
            ),
        )

        conn.commit()
        conn.close()
        logger.info(f"✅ Successfully saved to database: {filename}")
        return True
    except Exception as e:
        logger.error(f"❌ Database error for {filename}: {e}")
        st.error(f"Database error: {str(e)}")
        return False


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using Tesseract OCR"""
    logger.info(f"🔍 Starting OCR extraction for: {os.path.basename(pdf_path)}")
    
    try:
        # Convert PDF to images
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info("📄 Converting PDF to images...")
            images = pdf2image.convert_from_path(
                pdf_path, output_folder=temp_dir, dpi=200
            )
            logger.info(f"📄 PDF converted to {len(images)} images")

            extracted_text = ""
            for i, image in enumerate(images):
                logger.info(f"🔍 Processing page {i+1}/{len(images)}")
                # Extract text from each page using Tesseract
                page_text = pytesseract.image_to_string(image, lang="eng")
                extracted_text += f"\n--- Page {i+1} ---\n{page_text}\n"

            logger.info(f"✅ OCR extraction completed for: {os.path.basename(pdf_path)}")
            return extracted_text.strip()

    except Exception as e:
        logger.error(f"❌ OCR processing failed for {pdf_path}: {e}")
        raise Exception(f"OCR processing failed: {str(e)}")


def get_pdf_files_from_directory(directory_path):
    """Get all PDF files from the specified directory"""
    logger.info(f"📁 Scanning directory for PDF files: {directory_path}")
    
    try:
        pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
        logger.info(f"📄 Found {len(pdf_files)} PDF files in directory")
        
        if pdf_files:
            for pdf_file in pdf_files:
                logger.info(f"📄 - {os.path.basename(pdf_file)}")
        
        return pdf_files
    except Exception as e:
        logger.error(f"❌ Error reading directory {directory_path}: {e}")
        st.error(f"Error reading directory: {str(e)}")
        return []


def display_database_records():
    """Display recent records from the database"""
    logger.info("📋 Loading recent database records")
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT filename, created_timestamp, word_count, character_length,
                   SUBSTR(extracted_text, 1, 200) || '...' as preview
            FROM pdf_extracts
            ORDER BY created_timestamp DESC
            LIMIT 10
        """
        )

        records = cursor.fetchall()
        conn.close()

        if records:
            logger.info(f"📋 Displaying {len(records)} database records")
            st.subheader("Recent Processed Files")
            for (
                filename,
                timestamp,
                word_count,
                character_length,
                preview,
            ) in records:
                with st.expander(f"{filename} - {timestamp}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Word Count", word_count or 0)
                    with col2:
                        st.metric("Characters", character_length or 0)
                    st.text_area("Preview:", preview, height=100)
        else:
            logger.info("📋 No records found in database")
            st.info("No processed files found in database.")

    except Exception as e:
        logger.error(f"❌ Error reading from database: {e}")
        st.error(f"Error reading from database: {str(e)}")


def main():
    """Main Streamlit application"""
    logger.info("🏠 Main application page loaded")
    logger.info("🎨 Setting up page configuration")
    
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
        logger.info(f"📁 User selected directory: {directory_path}")
        pdf_files = get_pdf_files_from_directory(directory_path)

        if pdf_files:
            st.success(f"Found {len(pdf_files)} PDF files")

            # Display found PDF files
            with st.expander("PDF Files Found"):
                for pdf_file in pdf_files:
                    st.text(os.path.basename(pdf_file))

            # Process files button
            if st.button("Process All PDF Files", type="primary"):
                logger.info(f"🚀 Starting batch processing of {len(pdf_files)} PDF files")
                progress_bar = st.progress(0)
                status_text = st.empty()

                successful_processes = 0
                failed_processes = 0

                for i, pdf_file in enumerate(pdf_files):
                    filename = os.path.basename(pdf_file)
                    status_text.text(f"Processing: {filename}")
                    logger.info(f"🔄 Processing file {i+1}/{len(pdf_files)}: {filename}")

                    try:
                        # Extract text from PDF
                        extracted_text = extract_text_from_pdf(pdf_file)

                        # Save to database
                        if save_extracted_text(filename, extracted_text):
                            successful_processes += 1
                            logger.info(f"✅ Successfully processed: {filename}")
                            st.success(f"✅ Processed: {filename}")
                        else:
                            failed_processes += 1
                            logger.error(f"❌ Database save failed for: {filename}")
                            st.error(f"❌ Database save failed: {filename}")

                    except Exception as e:
                        failed_processes += 1
                        logger.error(f"❌ Processing failed for {filename}: {e}")
                        st.error(f"❌ Failed for {filename}: {str(e)}")
                        with st.expander(f"Error details for {filename}"):
                            st.code(traceback.format_exc())

                    # Update progress
                    progress_bar.progress((i + 1) / len(pdf_files))

                # Final status
                status_text.text("Processing completed!")
                logger.info(
                    f"📋 Batch processing complete: {successful_processes} successful, "
                    f"{failed_processes} failed"
                )
                st.success(
                    f"Processing complete! ✅ {successful_processes} "
                    f"successful, ❌ {failed_processes} failed"
                )

        else:
            logger.info(f"📁 No PDF files found in directory: {directory_path}")
            st.warning("No PDF files found in the specified directory")

    elif directory_path:
        logger.warning(f"📁 Invalid directory path: {directory_path}")
        st.error("Directory does not exist. Please enter a valid path.")

    # Database viewer section
    st.header("Database Records")
    logger.info("📋 Loading database records section")
    display_database_records()

    # Database statistics
    logger.info("📊 Loading database statistics section")
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Get total records
        cursor.execute("SELECT COUNT(*) FROM pdf_extracts")
        total_records = cursor.fetchone()[0]

        # Get total words and characters
        cursor.execute(
            "SELECT SUM(word_count), SUM(character_length) FROM pdf_extracts"
        )
        total_words, total_chars = cursor.fetchone()

        conn.close()

        logger.info(
            f"📊 Database statistics: {total_records} records, "
            f"{total_words or 0} words, {total_chars or 0} characters"
        )

        # Display metrics in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Processed Files", total_records)
        with col2:
            st.metric("Total Words Extracted", total_words or 0)
        with col3:
            st.metric("Total Characters Extracted", total_chars or 0)

    except Exception as e:
        logger.error(f"❌ Error getting database statistics: {e}")
        st.error(f"Error getting database statistics: {str(e)}")


if __name__ == "__main__":
    main()
