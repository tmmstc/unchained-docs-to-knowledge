"""
PDF processing module for reading PDFs and extracting text using OCR.
"""

import pytesseract
import pdf2image
import tempfile
import re
from typing import Tuple


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
                extracted_text += f"\n--- Page {i + 1} ---\n{page_text}\n"

            return extracted_text.strip()

    except Exception as e:
        raise Exception(f"OCR processing failed: {str(e)}")


def calculate_text_metrics(text: str) -> Tuple[int, int]:
    """
    Calculate word count and character length for extracted text.

    Args:
        text: The text to analyze

    Returns:
        Tuple of (word_count, character_length)
    """
    if not text:
        return 0, 0

    # Character length (including whitespace and punctuation)
    character_length = len(text)

    # Word count - split by whitespace and filter out empty strings
    # This properly handles multiple spaces, tabs, newlines, and punctuation
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)

    return word_count, character_length
