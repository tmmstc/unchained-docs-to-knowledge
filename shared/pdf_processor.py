"""
PDF processing module for reading PDFs and extracting text using OCR.
"""

import pytesseract
import pdf2image
import tempfile
import re
import logging
import os
from typing import Tuple

# Configure module logger
logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF using Tesseract OCR.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text from all pages

    Raises:
        Exception: If OCR processing fails
    """
    logger.info(
        f"Starting OCR extraction for: {os.path.basename(pdf_path)}"
    )

    try:
        # Convert PDF to images
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info("Converting PDF to images...")
            images = pdf2image.convert_from_path(
                pdf_path, output_folder=temp_dir, dpi=200
            )
            logger.info(f"PDF converted to {len(images)} images")

            extracted_text = ""
            for i, image in enumerate(images):
                logger.info(f"Processing page {i+1}/{len(images)}")
                # Extract text from each page using Tesseract
                page_text = pytesseract.image_to_string(image, lang="eng")
                extracted_text += f"\n--- Page {i + 1} ---\n{page_text}\n"

            logger.info(
                f"OCR extraction completed for: "
                f"{os.path.basename(pdf_path)}"
            )
            return extracted_text.strip()

    except Exception as e:
        logger.error(f"OCR processing failed for {pdf_path}: {e}")
        raise Exception(f"OCR processing failed: {str(e)}")


def calculate_text_metrics(text: str) -> Tuple[int, int]:
    """
    Calculate word count and character length for extracted text.

    Args:
        text: The text to analyze

    Returns:
        Tuple of (word_count, character_length)
    """
    logger.info("Calculating text metrics")

    if not text:
        logger.info("Empty text - returning zero metrics")
        return 0, 0

    # Character length (including whitespace and punctuation)
    character_length = len(text)

    # Word count - split by whitespace and filter out empty strings
    # This properly handles multiple spaces, tabs, newlines, and punctuation
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)

    logger.info(
        f"Metrics calculated: {word_count} words, "
        f"{character_length} characters"
    )

    return word_count, character_length
