import logging
import traceback
from typing import List
from app.pdf_processor import (
    extract_text_from_pdf,
    calculate_text_metrics,
    calculate_md5_hash,
)
from frontend.api_client import (
    save_extracted_text_to_backend,
    check_duplicate_hash,
)
from frontend.file_operations import create_temp_file_from_upload, cleanup_temp_file

logger = logging.getLogger(__name__)


def process_single_pdf(
    pdf_path: str, filename: str, generate_summary: bool
) -> dict:
    try:
        logger.info(f"Processing file: {filename}")

        logger.info(f"Calculating MD5 hash for: {filename}")
        md5_hash = calculate_md5_hash(pdf_path)

        logger.info(f"Checking for duplicate with hash: {md5_hash}")
        if check_duplicate_hash(md5_hash):
            logger.info(f"Duplicate detected, skipping: {filename}")
            return {
                "success": True,
                "skipped": True,
                "message": f"File {filename} already exists (duplicate)",
            }

        logger.info(f"Extracting text from: {filename}")
        extracted_text = extract_text_from_pdf(pdf_path)

        word_count, character_length = calculate_text_metrics(extracted_text)
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

        return result

    except Exception as e:
        logger.error(f"Processing failed for {filename}: {e}")
        error_trace = traceback.format_exc()
        return {
            "success": False,
            "error": str(e),
            "traceback": error_trace,
        }


def process_pdf_batch(pdf_files: List[str], generate_summary: bool) -> dict:
    logger.info(f"Starting batch processing of {len(pdf_files)} PDF files")

    successful_processes = 0
    failed_processes = 0
    skipped_processes = 0
    results = []

    for pdf_file in pdf_files:
        filename = pdf_file.split("/")[-1].split("\\")[-1]

        result = process_single_pdf(pdf_file, filename, generate_summary)

        if result.get("success"):
            if result.get("skipped"):
                skipped_processes += 1
                logger.info(f"Skipped duplicate: {filename}")
            else:
                successful_processes += 1
                logger.info(f"Successfully processed: {filename}")
        else:
            failed_processes += 1
            logger.error(f"Processing failed for: {filename}")

        results.append({"filename": filename, "result": result})

    logger.info(
        f"Batch processing complete: "
        f"{successful_processes} successful, "
        f"{skipped_processes} skipped, "
        f"{failed_processes} failed"
    )

    return {
        "successful": successful_processes,
        "skipped": skipped_processes,
        "failed": failed_processes,
        "results": results,
    }


def process_uploaded_files(uploaded_files, generate_summary: bool) -> dict:
    logger.info(f"Starting processing of {len(uploaded_files)} uploaded files")

    successful_processes = 0
    failed_processes = 0
    skipped_processes = 0
    results = []

    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        logger.info(f"Processing uploaded file: {filename}")

        temp_file_path = None
        try:
            temp_file_path = create_temp_file_from_upload(uploaded_file)

            result = process_single_pdf(temp_file_path, filename, generate_summary)

            if result.get("success"):
                if result.get("skipped"):
                    skipped_processes += 1
                    logger.info(f"Skipped duplicate: {filename}")
                else:
                    successful_processes += 1
                    logger.info(f"Successfully processed: {filename}")
            else:
                failed_processes += 1
                logger.error(f"Processing failed for: {filename}")

            results.append({"filename": filename, "result": result})

        except Exception as e:
            failed_processes += 1
            logger.error(f"Processing failed for {filename}: {e}")
            error_trace = traceback.format_exc()
            results.append(
                {
                    "filename": filename,
                    "result": {
                        "success": False,
                        "error": str(e),
                        "traceback": error_trace,
                    },
                }
            )

        finally:
            if temp_file_path:
                cleanup_temp_file(temp_file_path)

    logger.info(
        f"Upload processing complete: "
        f"{successful_processes} successful, "
        f"{skipped_processes} skipped, "
        f"{failed_processes} failed"
    )

    return {
        "successful": successful_processes,
        "skipped": skipped_processes,
        "failed": failed_processes,
        "results": results,
    }
