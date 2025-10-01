"""
Simple test to verify Streamlit layout rendering.
Run with: streamlit run test_streamlit_layout.py
"""

import streamlit as st

st.set_page_config(page_title="Layout Test", page_icon="🧪", layout="wide")

st.title("🧪 Streamlit UI Layout Test")
st.markdown("This page tests the rendering of summarization controls")

st.header("Test 1: Checkbox Rendering")
st.markdown("The checkbox below should be visible immediately:")

enable_test = st.checkbox(
    "Enable summarization during processing",
    value=False,
    help="Generate AI-powered summaries of extracted text (requires API key)"
)

st.write(f"Checkbox state: {enable_test}")

if enable_test:
    st.success("✅ Checkbox is ENABLED")
else:
    st.info("ℹ️ Checkbox is DISABLED")

st.header("Test 2: Button Rendering in Expander")
st.markdown("The button below should appear inside the expander:")

with st.expander("Sample Document - 2024-01-01 12:00:00"):
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Word Count", 100)
    with col2:
        st.metric("Characters", 500)
    
    st.markdown("**No Summary Available**")
    
    if st.button("Generate Summary", key="test_button_1"):
        st.success("✅ Button clicked!")
        st.balloons()
    
    st.text_area("Preview:", "This is a test preview...", height=100, key="preview_1")

st.header("Test 3: Conditional Rendering")
st.markdown("Test conditional display logic:")

show_button = st.checkbox("Show Generate Summary button", value=True)

with st.expander("Conditional Test Document"):
    st.metric("Word Count", 200)
    
    has_summary = st.checkbox("Simulate record HAS summary", value=False)
    
    if has_summary:
        st.markdown("**Summary:**")
        st.write("This is a sample summary that was already generated.")
    else:
        if show_button:
            if st.button("Generate Summary", key="test_button_2"):
                st.success("✅ Conditional button clicked!")
        else:
            st.info("Button hidden by checkbox")

st.header("Test 4: Multiple Buttons with Unique Keys")
st.markdown("Testing multiple buttons with unique keys:")

for i in range(3):
    with st.expander(f"Document {i+1}"):
        if st.button(f"Generate Summary", key=f"gen_summary_{i+1}"):
            st.success(f"✅ Clicked button for document {i+1}")

st.header("Test 5: Layout Order")
st.markdown("Elements should appear in this order:")
st.write("1. Title")
st.write("2. Checkbox")
st.write("3. Expanders with buttons")
st.write("4. This text")

st.success("✅ All tests rendered successfully!")
