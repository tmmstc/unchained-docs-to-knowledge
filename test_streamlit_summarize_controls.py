#!/usr/bin/env python3
"""
Test script to verify summarization controls are present in Streamlit app.
"""

import re


def test_summarization_controls():
    """Verify summarization controls exist in streamlit_app.py."""
    with open("frontend/streamlit_app.py", "r", encoding="utf-8") as f:
        content = f.read()

    print("Checking for summarization controls...")

    # Check for checkbox control
    checkbox_pattern = r'st\.checkbox\(\s*["\']Generate AI summaries'
    if re.search(checkbox_pattern, content):
        print("✓ Found summarization checkbox control")
    else:
        print("✗ Missing summarization checkbox control")
        return False

    # Check for generate_summary variable
    if "generate_summary = st.checkbox" in content:
        print("✓ Found generate_summary variable assignment")
    else:
        print("✗ Missing generate_summary variable")
        return False

    # Check for generate_summary parameter in backend call
    if "generate_summary," in content:
        print("✓ Found generate_summary passed to backend")
    else:
        print("✗ Missing generate_summary in backend call")
        return False

    # Check for generate_summary parameter in function signature
    if "generate_summary: bool = True" in content:
        print("✓ Found generate_summary parameter in function signature")
    else:
        print("✗ Missing generate_summary in function signature")
        return False

    # Check for summary display in records
    if 'record.get("summary")' in content:
        print("✓ Found summary display in records viewer")
    else:
        print("✗ Missing summary display")
        return False

    print("\nAll summarization controls verified successfully!")
    return True


if __name__ == "__main__":
    success = test_summarization_controls()
    exit(0 if success else 1)
