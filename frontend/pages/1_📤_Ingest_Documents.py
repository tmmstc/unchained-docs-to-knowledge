#!/usr/bin/env python3
"""
Document Ingestion Page - Handle folder selection, file upload,
and processing with optional summarization.
"""

import streamlit as st
from frontend.file_operations import get_pdf_files_from_directory
from frontend.data_processing import process_pdf_batch, process_uploaded_files


def render_process_pdf_batch_ui(pdf_files, generate_summary: bool):
    progress_bar = st.progress(0)
    status_text = st.empty()

    batch_result = process_pdf_batch(pdf_files, generate_summary)

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
    progress_bar = st.progress(0)
    status_text = st.empty()

    upload_result = process_uploaded_files(uploaded_files, generate_summary)

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
    st.set_page_config(
        page_title="Ingest Documents - PDF OCR Processor",
        page_icon="📤",
        layout="wide",
    )

    st.title("📤 Ingest Documents")
    st.markdown("Process PDF files with OCR and store results in the database")

    st.markdown("---")

    tab1, tab2 = st.tabs(["📂 Process from Folder", "📤 Upload Files"])

    with tab1:
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
            if not directory_path:
                st.warning("Please enter a directory path")
            else:
                st.info(f"Scanning directory: {directory_path}")
                pdf_files = get_pdf_files_from_directory(directory_path)

                if not pdf_files:
                    st.warning("No PDF files found in the specified directory")
                else:
                    st.success(f"Found {len(pdf_files)} PDF file(s)")
                    render_process_pdf_batch_ui(pdf_files, generate_summary_folder)

    with tab2:
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
            st.success(f"Selected {len(uploaded_files)} file(s)")

            if st.button("🚀 Process Uploaded Files", type="primary"):
                render_process_uploaded_files_ui(
                    uploaded_files, generate_summary_upload
                )


if __name__ == "__main__":
    main()
