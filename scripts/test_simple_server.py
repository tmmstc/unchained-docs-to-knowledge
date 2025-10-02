#!/usr/bin/env python3
"""
Simple HTTP server test to verify basic functionality.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        response = {
            "status": "ok",
            "message": "Test server is running",
            "path": self.path,
        }

        self.wfile.write(json.dumps(response).encode("utf-8"))

    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


def run_server():
    """Run simple HTTP server for testing."""
    print("Starting test HTTP server...")
    print("Server running on http://127.0.0.1:8080")
    print("Press Ctrl+C to stop\n")

    server_address = ("127.0.0.1", 8080)
    httpd = HTTPServer(server_address, SimpleHandler)

    try:
        # Test request
        print("Making test request...")
        import requests

        response = requests.get("http://127.0.0.1:8080/test", timeout=5)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
        print("\nOK Test server working correctly")

    except Exception:
        print("ERROR Test request failed")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nOK Server stopped")
        httpd.shutdown()


if __name__ == "__main__":
    import sys

    run_server()
    sys.exit(0)
