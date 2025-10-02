import logging
from datetime import datetime
from typing import List

logger = logging.getLogger(__name__)


def shorten_hash(hash_str: str, prefix_length: int = 8) -> str:
    if not hash_str:
        return "N/A"
    return hash_str[:prefix_length]


def filter_records(
    records: List[dict], filename_filter: str = "", summary_filter: str = "All"
) -> List[dict]:
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

    return filtered_records


def sort_records(records: List[dict], sort_by: str) -> List[dict]:
    if sort_by == "ID (Desc)":
        records.sort(key=lambda x: x.get("id", 0), reverse=True)
    elif sort_by == "ID (Asc)":
        records.sort(key=lambda x: x.get("id", 0))
    elif sort_by == "Filename":
        records.sort(key=lambda x: x.get("filename", ""))
    elif sort_by == "Words (Desc)":
        records.sort(key=lambda x: x.get("word_count", 0), reverse=True)
    elif sort_by == "Chars (Desc)":
        records.sort(key=lambda x: x.get("character_length", 0), reverse=True)

    return records


def format_timestamp(timestamp_str: str) -> str:
    if isinstance(timestamp_str, str):
        try:
            created_dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            return created_dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return timestamp_str
    else:
        return str(timestamp_str)


def prepare_dataframe_data(records: List[dict]) -> List[dict]:
    df_data = []
    for record in records:
        created_str = format_timestamp(record.get("created_timestamp", ""))
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

    return df_data
