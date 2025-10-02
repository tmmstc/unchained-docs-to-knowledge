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
from datetime import datetime
from shared.pdf_processor import (
    extract_text_from_pdf,
    calculate_text_metrics,
    calculate_md5_hash,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

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


def shorten_hash(hash_str: str, prefix_length: int = 8) -> str:
    """Shorten MD5 hash for display."""
    if not hash_str:
        return "N/A"
    return hash_str[:prefix_length]


def display_database_records():
    """Display records from the backend in a tabular format with clickable selection."""
    import pandas as pd

    records = get_records_from_backend(limit=100)

    if not records:
        st.info("No processed files found in database.")
        return

    st.subheader("Database Records")

    col1, col2, col3 = st.columns(3)

    with col1:
        filename_filter = st.text_input(
            "Filter by filename",
            placeholder="Enter text to filter...",
            key="filename_filter",
        )

    with col2:
        summary_filter = st.selectbox(
            "Filter by summary",
            options=["All", "With Summary", "Without Summary"],
            key="summary_filter",
        )

    with col3:
        sort_by = st.selectbox(
            "Sort by",
            options=[
                "ID (Desc)",
                "ID (Asc)",
                "Filename",
                "Words (Desc)",
                "Chars (Desc)",
                "Date (Recent)",
            ],
            key="sort_by",
        )

    filtered_records = []
    for record in records:
        if (
            filename_filter
            and filename_filter.lower() not in record.get("filename", "").lower()
        ):
            continue

        has_summary = bool(record.get("summary"))
        if summary_filter == "With Summary" and not has_summary:
            continue
        if summary_filter == "Without Summary" and has_summary:
            continue

        filtered_records.append(record)

    if sort_by == "ID (Desc)":
        filtered_records.sort(key=lambda x: x.get("id", 0), reverse=True)
    elif sort_by == "ID (Asc)":
        filtered_records.sort(key=lambda x: x.get("id", 0))
    elif sort_by == "Filename":
        filtered_records.sort(key=lambda x: x.get("filename", ""))
    elif sort_by == "Words (Desc)":
        filtered_records.sort(key=lambda x: x.get("word_count", 0), reverse=True)
    elif sort_by == "Chars (Desc)":
        filtered_records.sort(key=lambda x: x.get("character_length", 0), reverse=True)

    st.markdown(f"**Showing {len(filtered_records)} of " f"{len(records)} records**")

    st.markdown("### Records Table")
    st.markdown(
        "Click on a row to view full details including extracted text and summary"
    )

    df_data = []
    for record in filtered_records:
        created_dt = record.get("created_timestamp", "")
        if isinstance(created_dt, str):
            try:
                created_dt = datetime.fromisoformat(created_dt.replace("Z", "+00:00"))
                created_str = created_dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                created_str = created_dt
        else:
            created_str = str(created_dt)

        md5_hash = record.get("md5_hash")
        has_summary = "Yes" if record.get("summary") else "No"

        df_data.append(
            {
                "ID": record.get("id", ""),
                "Hash": shorten_hash(md5_hash),
                "Filename": record.get("filename", ""),
                "Words": record.get("word_count", 0),
                "Chars": record.get("character_length", 0),
                "Processed": created_str,
                "Summary": has_summary,
            }
        )

    if df_data:
        df = pd.DataFrame(df_data)

        selection = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="records_table",
        )

        if selection and selection.selection.rows:
            selected_row_idx = selection.selection.rows[0]
            selected_record = filtered_records[selected_row_idx]

            st.markdown("---")
            st.markdown(f"### Details for: {selected_record['filename']}")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Word Count", selected_record.get("word_count", 0))
            with col2:
                st.metric("Characters", selected_record.get("character_length", 0))
            with col3:
                st.metric(
                    "Has Summary", "Yes" if selected_record.get("summary") else "No"
                )
            with col4:
                full_hash = selected_record.get("md5_hash", "N/A")
                st.metric("Hash", shorten_hash(full_hash))

            if full_hash != "N/A":
                with st.expander("View Full MD5 Hash"):
                    st.code(full_hash)

            extracted_text = selected_record.get("extracted_text", "")
            if extracted_text:
                with st.expander("View Extracted Text", expanded=False):
                    st.text_area(
                        "Full Extracted Text",
                        extracted_text,
                        height=300,
                        key=f"text_{selected_record.get('id')}",
                    )
            else:
                preview = selected_record.get("preview", "")
                if preview:
                    with st.expander("View Text Preview", expanded=False):
                        st.text_area(
                            "Text Preview",
                            preview,
                            height=150,
                            key=f"preview_{selected_record.get('id')}",
                        )

            summary = selected_record.get("summary")
            if summary:
                with st.expander("View Summary", expanded=True):
                    st.text_area(
                        "Summary",
                        summary,
                        height=200,
                        key=f"summary_{selected_record.get('id')}",
                    )
            else:
                st.info("No summary available for this record.")


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

            with st.expander("PDF Files Found"):
                for idx, pdf_file in enumerate(pdf_files):
                    st.text(os.path.basename(pdf_file))

            st.subheader("Summarization Options")
            generate_summary = st.checkbox(
                "Generate AI summaries for processed files",
                value=True,
                help="Use OpenAI to generate summaries of extracted text. "
                "Requires OPENAI_API_KEY environment variable.",
            )

            if st.button("Process All PDF Files", type="primary"):
                logger.info(f"Starting batch processing of {len(pdf_files)} PDF files")
                progress_bar = st.progress(0)
                status_text = st.empty()

                successful_processes = 0
                failed_processes = 0
                skipped_processes = 0

                for i, pdf_file in enumerate(pdf_files):
                    filename = os.path.basename(pdf_file)
                    status_text.text(f"Processing: {filename}")
                    logger.info(f"Processing file {i+1}/{len(pdf_files)}: {filename}")

                    try:
                        logger.info(f"Calculating MD5 hash for: {filename}")
                        md5_hash = calculate_md5_hash(pdf_file)

                        logger.info(f"Extracting text from: {filename}")
                        extracted_text = extract_text_from_pdf(pdf_file)

                        word_count, character_length = calculate_text_metrics(
                            extracted_text
                        )
                        logger.info(
                            f"Text metrics for {filename}: "
                            f"{word_count} words, {character_length} chars"
                        )

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
                        with st.expander(
                            f"Error details for {filename}", expanded=False
                        ):
                            st.code(traceback.format_exc())

                    progress_bar.progress((i + 1) / len(pdf_files))

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

    st.header("Database Records")
    logger.info("Loading database records section")
    display_database_records()

    logger.info("Loading database statistics section")
    stats = get_stats_from_backend()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Processed Files", stats["total_records"])
    with col2:
        st.metric("Total Words Extracted", stats["total_words"])
    with col3:
        st.metric("Total Characters Extracted", stats["total_characters"])


if __name__ == "__main__":
    main()
