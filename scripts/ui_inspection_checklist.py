#!/usr/bin/env python3
"""
UI Inspection Script - Analyzes streamlit_app.py for rendering issues
"""

import re
import sys
from pathlib import Path


def analyze_ui_structure(file_path=None):
    if file_path is None:
        file_path = Path(__file__).parent.parent / "frontend" / "streamlit_app.py"

    sys.stdout.reconfigure(encoding="utf-8")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    print("=" * 80)
    print("STREAMLIT UI RENDERING ANALYSIS")
    print("=" * 80)

    # Find main() function
    main_start = content.find("def main():")
    if main_start == -1:
        print("[ERROR] Could not find main() function!")
        return

    main_content = content[main_start:]

    print("\n1. CHECKING ELEMENT RENDERING ORDER IN main()")
    print("-" * 80)

    # Track order of UI elements
    ui_elements = []

    # st.title
    title_match = re.search(r'st\.title\("([^"]+)"\)', main_content)
    if title_match:
        ui_elements.append(
            ("st.title", main_content.find(title_match.group(0), main_start), title_match.group(1))
        )

    # st.header - Select Directory
    header_match = re.search(r'st\.header\("Select Directory"\)', main_content)
    if header_match:
        ui_elements.append(
            ("st.header", main_content.find(header_match.group(0), main_start), "Select Directory")
        )

    # Checkbox
    checkbox_match = re.search(r"enable_summarization = st\.checkbox", main_content)
    if checkbox_match:
        pos = main_content.find(checkbox_match.group(0))
        ui_elements.append(("st.checkbox", pos, "enable_summarization"))

    # Directory path check
    dir_check = re.search(
        r"if directory_path and os\.path\.exists\(directory_path\):", main_content
    )
    if dir_check:
        pos = main_content.find(dir_check.group(0))
        ui_elements.append(("conditional", pos, "if directory_path exists"))

    # Process button
    button_match = re.search(r'st\.button\("Process All PDF Files"', main_content)
    if button_match:
        pos = main_content.find(button_match.group(0))
        ui_elements.append(("st.button", pos, "Process All PDF Files"))

    # Database Records header
    db_header = re.search(r'st\.header\("Database Records"\)', main_content)
    if db_header:
        pos = main_content.find(db_header.group(0))
        ui_elements.append(("st.header", pos, "Database Records"))

    # Sort by position
    ui_elements.sort(key=lambda x: x[1])

    print("\nUI Element Order:")
    for i, (element_type, position, label) in enumerate(ui_elements, 1):
        print(f"  {i}. {element_type:20} at position {position:6} - {label}")

    print("\n2. CHECKBOX ANALYSIS")
    print("-" * 80)

    # Find checkbox location
    checkbox_start = content.find("enable_summarization = st.checkbox")
    if checkbox_start == -1:
        print("[ERROR] Checkbox not found!")
        return

    # Check what comes before checkbox
    before_checkbox = content[max(0, checkbox_start - 500) : checkbox_start]

    # Check for conditional statements wrapping checkbox
    if_count = before_checkbox.count("if ")

    print(f"\nCheckbox location: position {checkbox_start}")
    print(f"'if' statements in 500 chars before: {if_count}")

    # Check indentation level
    lines_before = before_checkbox.split("\n")
    if lines_before:
        last_line = lines_before[-1]
        indent = len(last_line) - len(last_line.lstrip())
        print(f"Indentation level: {indent} spaces")
        if indent > 4:
            print("  [WARNING] Checkbox appears to be inside a nested block!")

    # Extract checkbox definition
    checkbox_end = content.find(")", checkbox_start + 100)
    checkbox_code = content[checkbox_start : checkbox_end + 1]
    print("\nCheckbox definition:")
    for line in checkbox_code.split("\n"):
        print(f"  {line}")

    print("\n3. GENERATE SUMMARY BUTTON ANALYSIS")
    print("-" * 80)

    # Find display_database_records function
    display_func_start = content.find("def display_database_records():")
    display_func_content = content[display_func_start : display_func_start + 5000]

    # Find the button
    button_pattern = r'if st\.button\(f"Generate Summary"'
    button_matches = list(re.finditer(button_pattern, display_func_content))

    if button_matches:
        match = button_matches[0]
        button_pos = match.start()

        # Get context before button
        context_before = display_func_content[max(0, button_pos - 300) : button_pos]
        context_after = display_func_content[button_pos : button_pos + 300]

        print(f"\nButton found at position {button_pos} in display_database_records()")
        print("\nConditional logic before button:")

        # Count nested ifs
        if_statements = re.findall(r"if .+:", context_before)
        print(f"  Found {len(if_statements)} 'if' statements before button")

        for i, stmt in enumerate(if_statements[-3:], 1):  # Last 3
            print(f"    {i}. {stmt.strip()}")

        # Check for else clause
        else_match = re.search(r"else:\s+if SUMMARIZER_AVAILABLE", display_func_content)
        if else_match:
            print("\n[OK] Button is in 'else' clause (when summary is None)")

        # Extract button code
        button_lines = context_after.split("\n")[:8]
        print("\nButton code structure:")
        for line in button_lines:
            print(f"  {line}")
    else:
        print("[ERROR] Generate Summary button not found!")

    print("\n4. CONDITIONAL LOGIC FLOW")
    print("-" * 80)

    # Analyze the if/else structure for summary display
    summary_logic = re.search(
        r"if summary:.*?else:.*?if SUMMARIZER_AVAILABLE", display_func_content, re.DOTALL
    )

    if summary_logic:
        logic_text = summary_logic.group(0)
        lines = logic_text.split("\n")[:15]  # First 15 lines
        print("\nSummary display logic:")
        for line in lines:
            print(f"  {line}")

    print("\n5. POTENTIAL RENDERING ISSUES")
    print("-" * 80)

    issues = []

    # Check 1: Checkbox inside conditional
    checkbox_context = content[checkbox_start - 200 : checkbox_start]
    if "if directory_path" in checkbox_context:
        issues.append(
            "Checkbox may be inside directory_path conditional (won't show until path entered)"
        )

    # Check 2: Button key uniqueness
    button_keys = re.findall(r'key=f"gen_summary_\{([^}]+)\}"', content)
    if len(button_keys) != len(set(button_keys)):
        issues.append("Duplicate button keys detected")

    # Check 3: SUMMARIZER_AVAILABLE flag
    if "SUMMARIZER_AVAILABLE = False" in content:
        issues.append("SUMMARIZER_AVAILABLE is set to False - buttons won't appear")

    # Check 4: Missing st.rerun()
    if "st.rerun()" not in display_func_content:
        issues.append("st.rerun() not found after summary generation - page won't refresh")

    if issues:
        print("\n[WARNING] Potential issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n[OK] No obvious rendering issues detected")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nRECOMMENDATIONS:")
    print("1. Manually test in browser at localhost:8501")
    print("2. Check browser console (F12) for errors")
    print("3. Verify database has records with and without summaries")
    print("4. Test checkbox state changes")
    print("5. Test Generate Summary button click behavior")
    print()


if __name__ == "__main__":
    analyze_ui_structure()
