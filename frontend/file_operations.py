import glob
import os
import tempfile
import logging
from typing import List

logger = logging.getLogger(__name__)


def get_pdf_files_from_directory(directory_path: str) -> List[str]:
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
        return []


def create_temp_file_from_upload(uploaded_file) -> str:
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_file_path = temp_file.name
            logger.info(f"Saved uploaded file to temp path: {temp_file_path}")
    except Exception as e:
        logger.error(f"Error creating temp file: {e}")
        raise
    return temp_file_path


def cleanup_temp_file(temp_file_path: str):
    if temp_file_path and os.path.exists(temp_file_path):
        try:
            os.unlink(temp_file_path)
            logger.info(f"Cleaned up temp file: {temp_file_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temp file {temp_file_path}: {e}")
