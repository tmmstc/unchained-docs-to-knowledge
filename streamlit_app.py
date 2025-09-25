#!/usr/bin/env python3
"""
Simple Streamlit app to demonstrate FastAPI connectivity.
Uses httpx for HTTP requests to avoid Streamlit installation issues.
"""

import httpx
import json
import time

# FastAPI backend configuration
BACKEND_URL = "http://localhost:8000"

def test_backend_connection():
    """Test connection to FastAPI backend"""
    try:
        with httpx.Client(timeout=5) as client:
            response = client.get(f"{BACKEND_URL}/")
            
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Backend returned status code: {response.status_code}"
            
    except httpx.ConnectError:
        return False, "Could not connect to FastAPI backend. Is it running on http://localhost:8000?"
    
    except httpx.TimeoutException:
        return False, "Connection timed out. The backend might be slow to respond."
    
    except Exception as e:
        return False, f"Request failed: {str(e)}"

def main():
    """Main application"""
    print("🚀 FastAPI + Streamlit Integration Test")
    print("=" * 50)
    print("Testing connectivity to FastAPI backend...")
    
    # Test connection
    success, result = test_backend_connection()
    
    if success:
        print("✅ Successfully connected to FastAPI backend!")
        print("Response:", json.dumps(result, indent=2))
    else:
        print("❌ Connection failed:", result)
        print("💡 Make sure to start the FastAPI server with:")
        print("   .\venv\Scripts\python.exe -m uvicorn app.main:app --reload")
    
    print("\nBackend URL:", BACKEND_URL)
    print("Endpoint: GET /")

if __name__ == "__main__":
    # For environments where Streamlit isn't available, run as basic script
    try:
        import streamlit as st
        
        # Page configuration
        st.set_page_config(
            page_title="FastAPI + Streamlit Demo",
            page_icon="🚀",
            layout="wide"
        )

        st.title("🚀 FastAPI + Streamlit Integration")
        st.markdown("This app demonstrates connectivity between Streamlit frontend and FastAPI backend.")

        # Test connection section
        st.header("Backend Connectivity Test")

        if st.button("Test Connection to FastAPI"):
            success, result = test_backend_connection()
            
            if success:
                st.success("✅ Successfully connected to FastAPI backend!")
                st.json(result)
            else:
                st.error(f"❌ {result}")
                st.info("💡 Make sure to start the FastAPI server with: `.\venv\Scripts\python.exe -m uvicorn app.main:app --reload`")

        # Status indicator
        st.header("Backend Status")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Connection Details")
            st.info(f"**Backend URL:** {BACKEND_URL}")
            st.info("**Endpoint:** GET /")

        with col2:
            st.subheader("Quick Test")
            success, result = test_backend_connection()
            if success:
                st.success("🟢 Backend is online")
            else:
                st.error("🔴 Backend is offline")
    
    except ImportError:
        # Streamlit not available, run as basic script
        main()

# Instructions section
st.header("Getting Started")
st.markdown("""
### Running Both Services

1. **Start FastAPI Backend (Terminal 1):**
   ```bash
   .\venv\Scripts\python.exe -m uvicorn app.main:app --reload
   ```

2. **Start Streamlit Frontend (Terminal 2):**
   ```bash
   .\venv\Scripts\streamlit run streamlit_app.py
   ```

### Endpoints Available
- `GET /` - Returns a hello world message

### Error Handling
The app handles the following error cases:
- Backend server not running
- Connection timeouts
- Network errors
- Invalid responses
""")