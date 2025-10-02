import requests
import logging

logger = logging.getLogger(__name__)

BACKEND_URL = "http://localhost:8000"


def check_duplicate_hash(md5_hash: str) -> bool:
    logger.info(f"Checking duplicate hash with backend: {md5_hash}")

    try:
        response = requests.get(
            f"{BACKEND_URL}/check-duplicate/{md5_hash}",
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
        is_duplicate = result.get("is_duplicate", False)
        logger.info(f"Duplicate check result: {is_duplicate}")
        return is_duplicate
    except Exception as e:
        logger.error(f"Error checking duplicate hash: {e}")
        return False


def save_extracted_text_to_backend(
    filename: str,
    extracted_text: str,
    word_count: int,
    character_length: int,
    generate_summary: bool = True,
    md5_hash: str = None,
) -> dict:
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
        return {"success": False, "error": str(e)}


def get_records_from_backend(limit: int = 10):
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
        return []


def get_stats_from_backend() -> dict:
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
        return {
            "total_records": 0,
            "total_words": 0,
            "total_characters": 0,
        }


def generate_summary_for_record(record_id: int) -> dict:
    logger.info(f"Requesting summary generation for record {record_id}")

    try:
        response = requests.put(
            f"{BACKEND_URL}/records/{record_id}/summary",
            params={"generate": True},
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"Summary generation result for record {record_id}: {result}")
        return result
    except Exception as e:
        logger.error(f"Error generating summary for record {record_id}: {e}")
        return {"success": False, "error": str(e)}


def delete_record(record_id: int) -> dict:
    logger.info(f"Requesting deletion of record {record_id}")

    try:
        response = requests.delete(
            f"{BACKEND_URL}/records/{record_id}",
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"Deletion result for record {record_id}: {result}")
        return result
    except Exception as e:
        logger.error(f"Error deleting record {record_id}: {e}")
        return {"success": False, "error": str(e)}
