#!/usr/bin/env python3
"""
Test script to verify Streamlit UI components are properly configured.
This script checks the streamlit_app.py for UI component issues.
"""

import re
import sys
from pathlib import Path


def check_ui_components(file_path=None):
    """Check if UI components are properly defined in the Streamlit app."""
    if file_path is None:
        file_path = Path(__file__).parent.parent / "frontend" / "streamlit_app.py"

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    print("=" * 80)
    print("STREAMLIT UI COMPONENT VERIFICATION")
    print("=" * 80)

    # Check 1: Summarization checkbox
    checkbox_pattern = r'st\.checkbox\s*\(\s*"Enable summarization during processing"'
    checkbox_matches = re.findall(checkbox_pattern, content)
    print(f"\n[OK] Found {len(checkbox_matches)} 'Enable summarization' checkbox(es)")

    if checkbox_matches:
        # Get context around checkbox
        checkbox_start = content.find("enable_summarization = st.checkbox")
        if checkbox_start != -1:
            context = content[checkbox_start : checkbox_start + 200]
            print("  Context:")
            print("  " + "\n  ".join(context.split("\n")[:5]))

    # Check 2: Generate Summary button
    button_pattern = r'st\.button\s*\(\s*f?"Generate Summary"'
    button_matches = re.findall(button_pattern, content)
    print(f"\n[OK] Found {len(button_matches)} 'Generate Summary' button(s)")

    if button_matches:
        button_start = content.find('st.button(f"Generate Summary"')
        if button_start != -1:
            context = content[button_start - 50 : button_start + 200]
            print("  Context:")
            print("  " + "\n  ".join(context.split("\n")))

    # Check 3: Conditional rendering logic
    print("\n" + "=" * 80)
    print("CONDITIONAL RENDERING CHECKS")
    print("=" * 80)

    # Check if checkbox is used in processing
    if "enable_summarization" in content:
        usage_count = content.count("enable_summarization")
        print(f"\n[OK] 'enable_summarization' variable used {usage_count} time(s)")

        # Find usages
        for match in re.finditer(r"if.*enable_summarization", content):
            start = match.start()
            context = content[start : start + 150]
            print(f"\n  Usage at position {start}:")
            print("  " + "\n  ".join(context.split("\n")[:3]))

    # Check if SUMMARIZER_AVAILABLE is used
    if "SUMMARIZER_AVAILABLE" in content:
        usage_count = content.count("SUMMARIZER_AVAILABLE")
        print(f"\n[OK] 'SUMMARIZER_AVAILABLE' variable used {usage_count} time(s)")

        # Find usages
        for match in re.finditer(r"if.*SUMMARIZER_AVAILABLE", content):
            start = match.start()
            context = content[start : start + 200]
            print(f"\n  Usage at position {start}:")
            print("  " + "\n  ".join(context.split("\n")[:4]))

    # Check 4: Summary display logic
    print("\n" + "=" * 80)
    print("SUMMARY DISPLAY CHECKS")
    print("=" * 80)

    summary_display = re.findall(r"if\s+summary:", content)
    print(f"\n[OK] Found {len(summary_display)} 'if summary:' conditional(s)")

    # Check 5: Button keys for uniqueness
    print("\n" + "=" * 80)
    print("BUTTON KEY UNIQUENESS CHECK")
    print("=" * 80)

    button_keys = re.findall(r'key\s*=\s*f?"([^"]+)"', content)
    unique_keys = set(button_keys)
    print(f"\n[OK] Total button keys found: {len(button_keys)}")
    print(f"[OK] Unique button keys: {len(unique_keys)}")

    if len(button_keys) != len(unique_keys):
        print("  WARNING: Duplicate keys detected!")
        from collections import Counter

        duplicates = [k for k, v in Counter(button_keys).items() if v > 1]
        print(f"  Duplicates: {duplicates}")
    else:
        print("  All keys are unique [OK]")

    # Check 6: State variables initialization
    print("\n" + "=" * 80)
    print("STATE VARIABLE INITIALIZATION")
    print("=" * 80)

    if "st.session_state" in content:
        session_state_count = content.count("st.session_state")
        print(f"\n[OK] 'st.session_state' used {session_state_count} time(s)")
    else:
        print("\n  No session state usage found")

    # Check 7: Import statements
    print("\n" + "=" * 80)
    print("IMPORT CHECKS")
    print("=" * 80)

    if "from app.summarizer import" in content:
        print("\n[OK] Summarizer module imported correctly")
        import_start = content.find("from app.summarizer import")
        context = content[import_start : import_start + 150]
        print("  " + "\n  ".join(context.split("\n")[:5]))
    else:
        print("\n[ERROR] Summarizer module import not found!")

    # Check 8: SUMMARIZER_AVAILABLE initialization
    if "SUMMARIZER_AVAILABLE = True" in content:
        print("\n[OK] SUMMARIZER_AVAILABLE flag properly set")

    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    print("\nSummary:")
    print(f"  - Summarization checkbox: {'FOUND' if checkbox_matches else 'MISSING'}")
    print(f"  - Generate Summary button: {'FOUND' if button_matches else 'MISSING'}")
    print(f"  - Conditional logic: {'FOUND' if 'enable_summarization' in content else 'MISSING'}")
    print(
        f"  - Summarizer import: {'FOUND' if 'from app.summarizer import' in content else 'MISSING'}"
    )
    print("\n")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    check_ui_components()
