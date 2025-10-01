#!/usr/bin/env python3
"""
Streamlit app for PDF OCR processing with directory input and FastAPI backend.
"""

import streamlit as st
import os
import glob
import traceback
import requests
import logging
import sys
from typing import List
from shared.pdf_processor import (
    extract_text_from_pdf,
    calculate_text_metrics,
    calculate_md5_hash,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# FastAPI backend configuration
BACKEND_URL = "http://localhost:8000"

logger.info("Streamlit PDF OCR Frontend starting up")
logger.info(f"Backend URL configured: {BACKEND_URL}")
logger.info("Application: PDF OCR processing with FastAPI backend integration")


def get_pdf_files_from_directory(directory_path: str) -> List[str]:
    """Get all PDF files from the specified directory."""
    logger.info(f"Scanning directory for PDF files: {directory_path}")

    try:
        pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in directory")

        if pdf_files:
            for pdf_file in pdf_files:
                logger.info(f"- {os.path.basename(pdf_file)}")

        return pdf_files
    except Exception as e:
        logger.error(f"Error reading directory {directory_path}: {e}")
        st.error(f"Error reading directory: {str(e)}")
        return []


def save_extracted_text_to_backend(
    filename: str,
    extracted_text: str,
    word_count: int,
    character_length: int,
    generate_summary: bool = True,
    md5_hash: str = None,
) -> dict:
    """Save extracted text to backend via API."""
    logger.info(f"Sending PDF data to backend: {filename}")
    logger.info(f"Data size: {word_count} words, {character_length} characters")
    logger.info(f"Generate summary: {generate_summary}")
    if md5_hash:
        logger.info(f"MD5 hash: {md5_hash}")

    try:
        response = requests.post(
            f"{BACKEND_URL}/process-pdf",
            json={
                "filename": filename,
                "extracted_text": extracted_text,
                "word_count": word_count,
                "character_length": character_length,
                "generate_summary": generate_summary,
                "md5_hash": md5_hash,
            },
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"Backend response for {filename}: {result}")
        return result
    except Exception as e:
        logger.error(f"Backend API error for {filename}: {e}")
        st.error(f"Backend API error: {str(e)}")
        return {"success": False, "error": str(e)}


def get_records_from_backend(limit: int = 10) -> List[dict]:
    """Get records from backend via API."""
    logger.info(f"Requesting {limit} records from backend")

    try:
        response = requests.get(
            f"{BACKEND_URL}/records", params={"limit": limit}, timeout=10
        )
        response.raise_for_status()
        records = response.json()
        logger.info(f"Received {len(records)} records from backend")
        return records
    except Exception as e:
        logger.error(f"Error fetching records from backend: {e}")
        st.error(f"Error fetching records: {str(e)}")
        return []


def get_stats_from_backend() -> dict:
    """Get statistics from backend via API."""
    logger.info("Requesting statistics from backend")

    try:
        response = requests.get(f"{BACKEND_URL}/stats", timeout=10)
        response.raise_for_status()
        stats = response.json()
        logger.info(
            f"Backend statistics: {stats.get('total_records', 0)} records, "
            f"{stats.get('total_words', 0)} words, "
            f"{stats.get('total_characters', 0)} chars"
        )
        return stats
    except Exception as e:
        logger.error(f"Error fetching statistics from backend: {e}")
        st.error(f"Error fetching statistics: {str(e)}")
        return {
            "total_records": 0,
            "total_words": 0,
            "total_characters": 0,
        }


def display_database_records():
    """Display recent records from the backend."""
    records = get_records_from_backend()

    if records:
        st.subheader("Recent Processed Files")
        for record in records:
            with st.expander(f"{record['filename']} - {record['created_timestamp']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Word Count", record["word_count"] or 0)
                with col2:
                    st.metric("Characters", record["character_length"] or 0)
                if record.get("summary"):
                    st.text_area("Summary:", record["summary"], height=150)
                if record.get("preview"):
                    st.text_area("Preview:", record["preview"], height=100)
    else:
        st.info("No processed files found in database.")


def main():
    """Main Streamlit application."""
    logger.info("Main application page loaded")
    logger.info("Setting up page configuration")

    st.set_page_config(page_title="PDF OCR Processor", page_icon="📄", layout="wide")

    st.title("📄 PDF OCR Text Extractor")
    st.markdown(
        "Extract text from PDF files using Tesseract OCR and store "
        "via FastAPI backend"
    )

    logger.info("Testing backend connectivity...")

    # Check backend connectivity
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if response.status_code == 200:
            logger.info("Backend API connection successful")
            st.success("Connected to backend API")
        else:
            logger.error(f"Backend API returned status {response.status_code}")
            st.error("Backend API not responding correctly")
            return
    except Exception as e:
        logger.error(f"Cannot connect to backend API: {e}")
        st.error("Cannot connect to backend API. Please ensure it's running.")
        return

    # Directory input section
    st.header("Select Directory")
    directory_path = st.text_input(
        "Enter directory path containing PDF files:",
        placeholder="C:/path/to/pdf/directory",
    )

    if directory_path and os.path.exists(directory_path):
        logger.info(f"User selected directory: {directory_path}")
        pdf_files = get_pdf_files_from_directory(directory_path)

        if pdf_files:
            st.success(f"Found {len(pdf_files)} PDF files")

            # Display found PDF files
            with st.expander("PDF Files Found"):
                for pdf_file in pdf_files:
                    st.text(os.path.basename(pdf_file))

            # Summarization control
            st.subheader("Summarization Options")
            generate_summary = st.checkbox(
                "Generate AI summaries for processed files",
                value=True,
                help="Use OpenAI to generate summaries of extracted text. "
                "Requires OPENAI_API_KEY environment variable.",
            )

            # Process files button
            if st.button("Process All PDF Files", type="primary"):
                logger.info(
                    f"Starting batch processing of " f"{len(pdf_files)} PDF files"
                )
                progress_bar = st.progress(0)
                status_text = st.empty()

                successful_processes = 0
                failed_processes = 0
                skipped_processes = 0

                for i, pdf_file in enumerate(pdf_files):
                    filename = os.path.basename(pdf_file)
                    status_text.text(f"Processing: {filename}")
                    logger.info(
                        f"Processing file {i+1}/{len(pdf_files)}: " f"{filename}"
                    )

                    try:
                        # Calculate MD5 hash
                        logger.info(f"Calculating MD5 hash for: {filename}")
                        md5_hash = calculate_md5_hash(pdf_file)

                        # Extract text from PDF
                        logger.info(f"Extracting text from: {filename}")
                        extracted_text = extract_text_from_pdf(pdf_file)

                        # Calculate metrics
                        word_count, character_length = calculate_text_metrics(
                            extracted_text
                        )
                        logger.info(
                            f"Text metrics for {filename}: "
                            f"{word_count} words, {character_length} chars"
                        )

                        # Save to backend
                        result = save_extracted_text_to_backend(
                            filename,
                            extracted_text,
                            word_count,
                            character_length,
                            generate_summary,
                            md5_hash,
                        )

                        if result.get("success"):
                            if result.get("skipped"):
                                skipped_processes += 1
                                logger.info(f"Skipped duplicate: {filename}")
                                st.info(f"Skipped (duplicate): {filename}")
                            else:
                                successful_processes += 1
                                logger.info(f"Successfully processed: {filename}")
                                st.success(f"Processed: {filename}")
                        else:
                            failed_processes += 1
                            logger.error(f"Backend save failed for: {filename}")
                            st.error(f"Backend save failed: {filename}")

                    except Exception as e:
                        failed_processes += 1
                        logger.error(f"Processing failed for {filename}: {e}")
                        st.error(f"Failed for {filename}: {str(e)}")
                        with st.expander(f"Error details for {filename}"):
                            st.code(traceback.format_exc())

                    # Update progress
                    progress_bar.progress((i + 1) / len(pdf_files))

                # Final status
                status_text.text("Processing completed!")
                logger.info(
                    f"Batch processing complete: "
                    f"{successful_processes} successful, "
                    f"{skipped_processes} skipped, "
                    f"{failed_processes} failed"
                )
                st.success(
                    f"Processing complete! {successful_processes} "
                    f"successful, {skipped_processes} skipped (duplicates), "
                    f"{failed_processes} failed"
                )

        else:
            logger.info(f"No PDF files found in directory: {directory_path}")
            st.warning("No PDF files found in the specified directory")

    elif directory_path:
        logger.warning(f"Invalid directory path: {directory_path}")
        st.error("Directory does not exist. Please enter a valid path.")

    # Database viewer section
    st.header("Database Records")
    logger.info("Loading database records section")
    display_database_records()

    # Database statistics
    logger.info("Loading database statistics section")
    stats = get_stats_from_backend()

    # Display metrics in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Processed Files", stats["total_records"])
    with col2:
        st.metric("Total Words Extracted", stats["total_words"])
    with col3:
        st.metric("Total Characters Extracted", stats["total_characters"])


if __name__ == "__main__":
    main()
