#!/usr/bin/env python3
"""
Data Viewing and Querying Page - Display database records table,
detail view with delete and summarize buttons.
"""

import sys
import os
import traceback
import logging
from datetime import datetime

print("=" * 80)
print("PAGE MODULE LOADING: 2_📊_View_Database.py")
print("=" * 80)
print(f"Timestamp: {datetime.now().isoformat()}")
print(f"Module: View Database (Record Browser & Management)")
print("=" * 80)

logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("PAGE MODULE: 2_📊_View_Database.py")
logger.info("=" * 80)
logger.info("Description: Database record viewing and management")
logger.info("Features: Record browsing, filtering, sorting, deletion, summarization")
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
    logger.info("Importing pandas...")
    import pandas as pd

    logger.info("✓ pandas imported successfully")
except Exception as e:
    logger.error(f"✗ Failed to import pandas: {e}")
    logger.error(traceback.format_exc())
    raise

try:
    logger.info("Importing frontend.api_client...")
    from frontend.api_client import (
        get_records_from_backend,
        generate_summary_for_record,
        delete_record,
    )

    logger.info("✓ frontend.api_client imported successfully")
except Exception as e:
    logger.error(f"✗ Failed to import frontend.api_client: {e}")
    logger.error(traceback.format_exc())
    raise

try:
    logger.info("Importing frontend.data_transforms...")
    from frontend.data_transforms import (
        shorten_hash,
        filter_records,
        sort_records,
        prepare_dataframe_data,
    )

    logger.info("✓ frontend.data_transforms imported successfully")
except Exception as e:
    logger.error(f"✗ Failed to import frontend.data_transforms: {e}")
    logger.error(traceback.format_exc())
    raise

try:
    logger.info("Importing frontend.state_manager...")
    from frontend.state_manager import (
        init_delete_confirmation_state,
        reset_delete_confirmation_on_selection_change,
        is_in_confirmation_mode,
        set_confirmation_mode,
        clear_delete_state,
    )

    logger.info("✓ frontend.state_manager imported successfully")
except Exception as e:
    logger.error(f"✗ Failed to import frontend.state_manager: {e}")
    logger.error(traceback.format_exc())
    raise

logger.info("=" * 80)
logger.info("✓ All imports successful - Page module ready")
logger.info("=" * 80)

print(f"✓ Page module loaded: 2_📊_View_Database.py")
print("=" * 80)
print()


def render_generate_summary_button(selected_record: dict):
    logger.info(f"Rendering summary button for record {selected_record['id']}")

    has_summary = bool(selected_record.get("summary"))
    button_label = "Regenerate Summary" if has_summary else "Generate Summary"

    generate_btn = st.button(button_label, type="secondary", key="generate_summary_btn")
    if generate_btn:
        logger.info(
            f"Generate summary button clicked for record {selected_record['id']}"
        )
        with st.spinner("Generating summary..."):
            record_id = selected_record["id"]
            result = generate_summary_for_record(record_id)

            if result.get("success"):
                st.success("Summary generated successfully!")
                logger.info(f"Summary generated successfully for record {record_id}")
                st.rerun()
            else:
                error_msg = result.get("error", "Unknown error")
                st.error(f"Failed to generate summary: {error_msg}")
                logger.error(
                    f"Failed to generate summary for record {record_id}: {error_msg}"
                )


def render_delete_button(selected_record: dict):
    logger.info(f"Rendering delete button for record {selected_record['id']}")

    init_delete_confirmation_state(st.session_state)

    current_record_id = selected_record["id"]

    reset_delete_confirmation_on_selection_change(st.session_state, current_record_id)

    in_confirmation_mode = is_in_confirmation_mode(st.session_state, current_record_id)

    if in_confirmation_mode:
        button_label = "⚠️ Click again to confirm"
        button_type = "secondary"
        button_help = "This will permanently delete the record"
    else:
        button_label = "Delete Record"
        button_type = "primary"
        button_help = "Click to delete this record"

    delete_btn = st.button(
        button_label,
        type=button_type,
        key="delete_record_btn",
        help=button_help,
    )

    if delete_btn:
        if not in_confirmation_mode:
            logger.info(
                f"Delete confirmation mode activated for record {current_record_id}"
            )
            set_confirmation_mode(st.session_state, current_record_id)
            st.rerun()
        else:
            logger.info(f"Delete confirmed for record {current_record_id}")
            with st.spinner("Deleting record..."):
                result = delete_record(current_record_id)

                if result.get("success"):
                    st.success("Record deleted successfully!")
                    logger.info(f"Record {current_record_id} deleted successfully")
                    clear_delete_state(st.session_state)
                    st.rerun()
                else:
                    error_msg = result.get("error", "Unknown error")
                    st.error(f"Failed to delete record: {error_msg}")
                    logger.error(
                        f"Failed to delete record {current_record_id}: {error_msg}"
                    )


def render_record_details(selected_record: dict):
    logger.info(
        f"Rendering details for record {selected_record['id']}: {selected_record['filename']}"
    )

    st.markdown("---")
    st.markdown(f"### Details for: {selected_record['filename']}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Word Count", selected_record.get("word_count", 0))
    with col2:
        st.metric("Characters", selected_record.get("character_length", 0))
    with col3:
        st.metric("Has Summary", "Yes" if selected_record.get("summary") else "No")
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

    st.markdown("---")
    st.markdown("### Actions")

    col1, col2 = st.columns(2)

    with col1:
        render_generate_summary_button(selected_record)

    with col2:
        render_delete_button(selected_record)


def render_database_records():
    logger.info("Rendering database records view")

    try:
        logger.info("Fetching records from backend...")
        records = get_records_from_backend(limit=100)
        logger.info(f"Retrieved {len(records)} records from backend")
    except Exception as e:
        logger.error(f"Error fetching records: {e}")
        logger.error(traceback.format_exc())
        st.error(f"Error fetching records: {str(e)}")
        with st.expander("View Error Details"):
            st.code(traceback.format_exc())
        return

    if not records:
        st.info("No processed files found in database.")
        logger.info("No records found in database")
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

    logger.info(
        f"Applying filters - Filename: '{filename_filter}', Summary: '{summary_filter}', Sort: '{sort_by}'"
    )

    filtered_records = filter_records(records, filename_filter, summary_filter)
    filtered_records = sort_records(filtered_records, sort_by)

    logger.info(f"Filtered results: {len(filtered_records)} records")

    st.markdown(f"**Showing {len(filtered_records)} of {len(records)} records**")

    st.markdown("### Records Table")
    st.markdown(
        "Click on a row to view full details including extracted text and summary"
    )

    df_data = prepare_dataframe_data(filtered_records)

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
            logger.info(
                f"Record selected: ID={selected_record['id']}, Filename={selected_record['filename']}"
            )

            render_record_details(selected_record)


def main():
    """Main page function with comprehensive error handling."""
    try:
        logger.info("Executing main() function for View Database page")

        logger.info("Setting page configuration...")
        st.set_page_config(
            page_title="View Database - PDF OCR Processor",
            page_icon="📊",
            layout="wide",
        )
        logger.info("✓ Page configuration set successfully")

        logger.info("Rendering page header...")
        st.title("📊 View Database")
        st.markdown("Browse and manage processed PDF documents")
        st.markdown("---")

        render_database_records()

        logger.info("✓ View Database page rendered successfully")

    except Exception as e:
        logger.error(f"✗ CRITICAL ERROR in View Database page main(): {e}")
        logger.error(traceback.format_exc())

        st.error("⚠️ Page Error")
        st.error(f"An error occurred while loading this page: {str(e)}")

        with st.expander("View Error Details", expanded=True):
            st.code(traceback.format_exc())


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("EXECUTION: Running main() function for View Database page")
    logger.info("=" * 80)

    try:
        main()
    except Exception as e:
        logger.error("=" * 80)
        logger.error("FATAL ERROR: Uncaught exception in View Database page")
        logger.error("=" * 80)
        logger.error(f"Error: {e}")
        logger.error(traceback.format_exc())
        raise
