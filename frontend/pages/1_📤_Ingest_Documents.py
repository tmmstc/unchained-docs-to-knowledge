#!/usr/bin/env python3
"""
Document Ingestion Page - Handle folder selection, file upload,
and processing with optional summarization.
"""

import sys
import os
import traceback
import logging
from datetime import datetime

print("=" * 80)
print("PAGE MODULE LOADING: 1_📤_Ingest_Documents.py")
print("=" * 80)
print(f"Timestamp: {datetime.now().isoformat()}")
print(f"Module: Ingest Documents (File Upload & Folder Processing)")
print("=" * 80)

logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("PAGE MODULE: 1_📤_Ingest_Documents.py")
logger.info("=" * 80)
logger.info("Description: Document ingestion with OCR processing")
logger.info("Features: Folder scanning, file upload, batch processing")
logger.info("=" * 80)

try:
    logger.info("Importing streamlit...")
    import streamlit as st

    logger.info("✓ streamlit imported successfully")
except Exception as e:
    logger.error(f"✗ Failed to import streamlit: {e}")
    logger.error(traceback.format_exc())
    raise

try:
    logger.info("Importing frontend.file_operations...")
    from frontend.file_operations import get_pdf_files_from_directory

    logger.info("✓ frontend.file_operations imported successfully")
except Exception as e:
    logger.error(f"✗ Failed to import frontend.file_operations: {e}")
    logger.error(traceback.format_exc())
    raise

try:
    logger.info("Importing frontend.data_processing...")
    from frontend.data_processing import process_pdf_batch, process_uploaded_files

    logger.info("✓ frontend.data_processing imported successfully")
except Exception as e:
    logger.error(f"✗ Failed to import frontend.data_processing: {e}")
    logger.error(traceback.format_exc())
    raise

logger.info("=" * 80)
logger.info("✓ All imports successful - Page module ready")
logger.info("=" * 80)

print(f"✓ Page module loaded: 1_📤_Ingest_Documents.py")
print("=" * 80)
print()


def render_process_pdf_batch_ui(pdf_files, generate_summary: bool):
    logger.info(f"Rendering batch processing UI for {len(pdf_files)} files")
    logger.info(f"Generate summary enabled: {generate_summary}")

    progress_bar = st.progress(0)
    status_text = st.empty()

    logger.info("Starting batch processing...")
    batch_result = process_pdf_batch(pdf_files, generate_summary)
    logger.info(
        f"Batch processing completed: {batch_result['successful']} successful, "
        f"{batch_result['skipped']} skipped, {batch_result['failed']} failed"
    )

    for i, item in enumerate(batch_result["results"]):
        filename = item["filename"]
        result = item["result"]

        status_text.text(f"Processing: {filename}")

        if result.get("success"):
            if result.get("skipped"):
                st.info(f"Skipped (duplicate): {filename}")
            else:
                st.success(f"Processed: {filename}")
        else:
            st.error(f"Failed for {filename}: {result.get('error', 'Unknown error')}")
            if result.get("traceback"):
                with st.expander(f"Error details for {filename}", expanded=False):
                    st.code(result["traceback"])

        progress_bar.progress((i + 1) / len(batch_result["results"]))

    status_text.text("Processing complete!")

    st.info(
        f"**Summary:** {batch_result['successful']} processed, "
        f"{batch_result['skipped']} skipped (duplicates), "
        f"{batch_result['failed']} failed"
    )


def render_process_uploaded_files_ui(uploaded_files, generate_summary: bool):
    logger.info(f"Rendering file upload processing UI for {len(uploaded_files)} files")
    logger.info(f"Generate summary enabled: {generate_summary}")

    progress_bar = st.progress(0)
    status_text = st.empty()

    logger.info("Starting uploaded files processing...")
    upload_result = process_uploaded_files(uploaded_files, generate_summary)
    logger.info(
        f"Upload processing completed: {upload_result['successful']} successful, "
        f"{upload_result['skipped']} skipped, {upload_result['failed']} failed"
    )

    for i, item in enumerate(upload_result["results"]):
        filename = item["filename"]
        result = item["result"]

        status_text.text(f"Processing: {filename}")

        if result.get("success"):
            if result.get("skipped"):
                st.info(f"Skipped (duplicate): {filename}")
            else:
                st.success(f"Processed: {filename}")
        else:
            st.error(f"Failed for {filename}: {result.get('error', 'Unknown error')}")
            if result.get("traceback"):
                with st.expander(f"Error details for {filename}", expanded=False):
                    st.code(result["traceback"])

        progress_bar.progress((i + 1) / len(upload_result["results"]))

    status_text.text("Processing complete!")

    st.info(
        f"**Summary:** {upload_result['successful']} processed, "
        f"{upload_result['skipped']} skipped (duplicates), "
        f"{upload_result['failed']} failed"
    )


def main():
    """Main page function with comprehensive error handling."""
    try:
        logger.info("Executing main() function for Ingest Documents page")

        logger.info("Setting page configuration...")
        st.set_page_config(
            page_title="Ingest Documents - PDF OCR Processor",
            page_icon="📤",
            layout="wide",
        )
        logger.info("✓ Page configuration set successfully")

        logger.info("Rendering page header...")
        st.title("📤 Ingest Documents")
        st.markdown("Process PDF files with OCR and store results in the database")
        st.markdown("---")

        logger.info("Creating tabs for folder and upload modes...")
        tab1, tab2 = st.tabs(["📂 Process from Folder", "📤 Upload Files"])

        with tab1:
            logger.info("Rendering folder processing tab...")
            st.header("Process PDFs from Folder")

            col1, col2 = st.columns([3, 1])

            with col1:
                directory_path = st.text_input(
                    "PDF Directory Path",
                    placeholder="Enter the path to the folder containing PDF files",
                    help="Enter the full path to a folder containing PDF files",
                )

            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                generate_summary_folder = st.checkbox(
                    "Generate Summaries",
                    value=True,
                    key="generate_summary_folder",
                    help="Generate AI summaries for each PDF",
                )

            if st.button("🔍 Process Folder", type="primary"):
                logger.info(
                    f"Process Folder button clicked - Directory: {directory_path}"
                )
                if not directory_path:
                    st.warning("Please enter a directory path")
                    logger.warning("Process attempt with empty directory path")
                else:
                    st.info(f"Scanning directory: {directory_path}")
                    logger.info(f"Scanning directory: {directory_path}")

                    try:
                        pdf_files = get_pdf_files_from_directory(directory_path)
                        logger.info(f"Found {len(pdf_files)} PDF files in directory")

                        if not pdf_files:
                            st.warning("No PDF files found in the specified directory")
                            logger.warning(f"No PDF files found in: {directory_path}")
                        else:
                            st.success(f"Found {len(pdf_files)} PDF file(s)")
                            render_process_pdf_batch_ui(
                                pdf_files, generate_summary_folder
                            )
                    except Exception as e:
                        logger.error(f"Error scanning directory: {e}")
                        logger.error(traceback.format_exc())
                        st.error(f"Error scanning directory: {str(e)}")
                        with st.expander("View Error Details"):
                            st.code(traceback.format_exc())

        with tab2:
            logger.info("Rendering file upload tab...")
            st.header("Upload PDF Files")

            col1, col2 = st.columns([3, 1])

            with col1:
                uploaded_files = st.file_uploader(
                    "Choose PDF files",
                    type=["pdf"],
                    accept_multiple_files=True,
                    help="Upload one or more PDF files for processing",
                )

            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                generate_summary_upload = st.checkbox(
                    "Generate Summaries",
                    value=True,
                    key="generate_summary_upload",
                    help="Generate AI summaries for each PDF",
                )

            if uploaded_files:
                logger.info(f"Files selected for upload: {len(uploaded_files)}")
                st.success(f"Selected {len(uploaded_files)} file(s)")

                if st.button("🚀 Process Uploaded Files", type="primary"):
                    logger.info(
                        f"Process Uploaded Files button clicked - {len(uploaded_files)} files"
                    )
                    try:
                        render_process_uploaded_files_ui(
                            uploaded_files, generate_summary_upload
                        )
                    except Exception as e:
                        logger.error(f"Error processing uploaded files: {e}")
                        logger.error(traceback.format_exc())
                        st.error(f"Error processing files: {str(e)}")
                        with st.expander("View Error Details"):
                            st.code(traceback.format_exc())

        logger.info("✓ Ingest Documents page rendered successfully")

    except Exception as e:
        logger.error(f"✗ CRITICAL ERROR in Ingest Documents page main(): {e}")
        logger.error(traceback.format_exc())

        st.error("⚠️ Page Error")
        st.error(f"An error occurred while loading this page: {str(e)}")

        with st.expander("View Error Details", expanded=True):
            st.code(traceback.format_exc())


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("EXECUTION: Running main() function for Ingest Documents page")
    logger.info("=" * 80)

    try:
        main()
    except Exception as e:
        logger.error("=" * 80)
        logger.error("FATAL ERROR: Uncaught exception in Ingest Documents page")
        logger.error("=" * 80)
        logger.error(f"Error: {e}")
        logger.error(traceback.format_exc())
        raise
