#!/usr/bin/env python3
"""
Streamlit app for PDF OCR processing with directory input and FastAPI backend.
"""

import streamlit as st
import os
import glob
import traceback
import requests
from typing import List
from shared.pdf_processor import extract_text_from_pdf, calculate_text_metrics


# FastAPI backend configuration
BACKEND_URL = "http://localhost:8000"


def get_pdf_files_from_directory(directory_path: str) -> List[str]:
    """Get all PDF files from the specified directory."""
    try:
        pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
        return pdf_files
    except Exception as e:
        st.error(f"Error reading directory: {str(e)}")
        return []


def save_extracted_text_to_backend(
    filename: str, extracted_text: str, word_count: int, character_length: int
) -> bool:
    """Save extracted text to backend via API."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/process-pdf",
            json={
                "filename": filename,
                "extracted_text": extracted_text,
                "word_count": word_count,
                "character_length": character_length,
            },
            timeout=30,
        )
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Backend API error: {str(e)}")
        return False


def get_records_from_backend(limit: int = 10) -> List[dict]:
    """Get records from backend via API."""
    try:
        response = requests.get(
            f"{BACKEND_URL}/records", params={"limit": limit}, timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching records: {str(e)}")
        return []


def get_stats_from_backend() -> dict:
    """Get statistics from backend via API."""
    try:
        response = requests.get(f"{BACKEND_URL}/stats", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching statistics: {str(e)}")
        return {"total_records": 0, "total_words": 0, "total_characters": 0}


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
                if record.get("preview"):
                    st.text_area("Preview:", record["preview"], height=100)
    else:
        st.info("No processed files found in database.")


def main():
    """Main Streamlit application."""
    st.set_page_config(page_title="PDF OCR Processor", page_icon="📄", layout="wide")

    st.title("📄 PDF OCR Text Extractor")
    st.markdown(
        "Extract text from PDF files using Tesseract OCR and store via FastAPI backend"
    )

    # Check backend connectivity
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if response.status_code == 200:
            st.success("✅ Connected to backend API")
        else:
            st.error("❌ Backend API not responding correctly")
            return
    except Exception:
        st.error("❌ Cannot connect to backend API. Please ensure it's running.")
        return

    # Directory input section
    st.header("Select Directory")
    directory_path = st.text_input(
        "Enter directory path containing PDF files:",
        placeholder="C:/path/to/pdf/directory",
    )

    if directory_path and os.path.exists(directory_path):
        pdf_files = get_pdf_files_from_directory(directory_path)

        if pdf_files:
            st.success(f"Found {len(pdf_files)} PDF files")

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

                        # Calculate metrics
                        word_count, character_length = calculate_text_metrics(
                            extracted_text
                        )

                        # Save to backend
                        if save_extracted_text_to_backend(
                            filename, extracted_text, word_count, character_length
                        ):
                            successful_processes += 1
                            st.success(f"✅ Processed: {filename}")
                        else:
                            failed_processes += 1
                            st.error(f"❌ Backend save failed: {filename}")

                    except Exception as e:
                        failed_processes += 1
                        st.error(f"❌ Failed for {filename}: {str(e)}")
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
        st.error("Directory does not exist. Please enter a valid path.")

    # Database viewer section
    st.header("Database Records")
    display_database_records()

    # Database statistics
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
