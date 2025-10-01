"""
Check if summarizer module can be imported
"""
import sys

print("Python path:")
for p in sys.path:
    print(f"  - {p}")

print("\nTrying to import summarizer...")

try:
    from app.summarizer import summarize_document
    print("✓ SUCCESS: Summarizer imported correctly")
    print(f"  summarize_document function: {summarize_document}")
    SUMMARIZER_AVAILABLE = True
except ImportError as e:
    print(f"✗ FAILED: Could not import summarizer")
    print(f"  Error: {e}")
    SUMMARIZER_AVAILABLE = False

print(f"\nSUMMARIZER_AVAILABLE = {SUMMARIZER_AVAILABLE}")
