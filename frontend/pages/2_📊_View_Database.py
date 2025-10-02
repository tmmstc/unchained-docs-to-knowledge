#!/usr/bin/env python3
"""
Data Viewing and Querying Page - Display database records table,
detail view with delete and summarize buttons.
"""

import streamlit as st
import pandas as pd
from frontend.api_client import (
    get_records_from_backend,
    generate_summary_for_record,
    delete_record,
)
from frontend.data_transforms import (
    shorten_hash,
    filter_records,
    sort_records,
    prepare_dataframe_data,
)
from frontend.state_manager import (
    init_delete_confirmation_state,
    reset_delete_confirmation_on_selection_change,
    is_in_confirmation_mode,
    set_confirmation_mode,
    clear_delete_state,
)


def render_generate_summary_button(selected_record: dict):
    has_summary = bool(selected_record.get("summary"))
    button_label = "Regenerate Summary" if has_summary else "Generate Summary"

    generate_btn = st.button(
        button_label, type="secondary", key="generate_summary_btn"
    )
    if generate_btn:
        with st.spinner("Generating summary..."):
            record_id = selected_record["id"]
            result = generate_summary_for_record(record_id)

            if result.get("success"):
                st.success("Summary generated successfully!")
                st.rerun()
            else:
                st.error(f"Failed to generate summary: {result.get('error', '')}")


def render_delete_button(selected_record: dict):
    init_delete_confirmation_state(st.session_state)

    current_record_id = selected_record["id"]

    reset_delete_confirmation_on_selection_change(
        st.session_state, current_record_id
    )

    in_confirmation_mode = is_in_confirmation_mode(
        st.session_state, current_record_id
    )

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
            set_confirmation_mode(st.session_state, current_record_id)
            st.rerun()
        else:
            with st.spinner("Deleting record..."):
                result = delete_record(current_record_id)

                if result.get("success"):
                    st.success("Record deleted successfully!")
                    clear_delete_state(st.session_state)
                    st.rerun()
                else:
                    st.error(f"Failed to delete record: {result.get('error', '')}")


def render_record_details(selected_record: dict):
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
    records = get_records_from_backend(limit=100)

    if not records:
        st.info("No processed files found in database.")
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

    filtered_records = filter_records(records, filename_filter, summary_filter)
    filtered_records = sort_records(filtered_records, sort_by)

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

            render_record_details(selected_record)


def main():
    st.set_page_config(
        page_title="View Database - PDF OCR Processor",
        page_icon="📊",
        layout="wide",
    )

    st.title("📊 View Database")
    st.markdown("Browse and manage processed PDF documents")

    st.markdown("---")

    render_database_records()


if __name__ == "__main__":
    main()
