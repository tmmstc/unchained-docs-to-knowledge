#!/usr/bin/env python3
"""
Streamlit app for PDF OCR processing with directory input and FastAPI backend.
Main entry point with navigation and statistics dashboard.
"""

import streamlit as st
import logging
import sys
from frontend.api_client import get_stats_from_backend

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


def main():
    st.set_page_config(
        page_title="PDF OCR Processor",
        page_icon="📄",
        layout="wide",
    )

    st.title("📄 PDF OCR Processor")
    st.markdown("Process PDF files with OCR and store results in a database")

    st.markdown("---")

    st.subheader("📈 Dashboard Statistics")

    stats = get_stats_from_backend()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", stats.get("total_records", 0))
    with col2:
        st.metric("Total Words", f"{stats.get('total_words', 0):,}")
    with col3:
        st.metric("Total Characters", f"{stats.get('total_characters', 0):,}")

    st.markdown("---")

    st.markdown("### Navigation")
    st.markdown("Use the sidebar to navigate between pages:")
    st.markdown("- **📤 Ingest Documents**: Upload or process PDF files from a folder")
    st.markdown("- **📊 View Database**: Browse, search, and manage processed documents")


if __name__ == "__main__":
    main()
