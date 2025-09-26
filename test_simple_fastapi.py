#!/usr/bin/env python3
"""
Simple test to verify FastAPI can import and create app instance.
"""

def test_fastapi_import():
    """Test if FastAPI modules can be imported."""
    print("Testing FastAPI import...")
    
    try:
        import fastapi
        print("fastapi imported successfully")
        
        import uvicorn
        print("uvicorn imported successfully")
        
        from app.main import app
        print("app.main imported successfully")
        
        # Test basic app properties
        print(f"App title: {app.title}")
        print(f"App version: {app.version}")
        
        return True
    except Exception as e:
        print(f"Import failed: {e}")
        return False

if __name__ == "__main__":
    success = test_fastapi_import()
    print(f"Test {'PASSED' if success else 'FAILED'}")
    exit(0 if success else 1)