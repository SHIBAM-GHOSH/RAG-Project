"""
=============================================================================
FILE: tests/conftest.py
PURPOSE: Shared test setup for the entire test suite.
WHAT IT DOES:
  1. Imports the FastAPI app from backend.
  2. Creates a TestClient that simulates HTTP requests without a real server.
  3. Makes 'client' available to ALL test files automatically (no import needed).
WHY IT'S HERE:
  - pytest auto-loads conftest.py before running any test.
  - Avoids repeating setup code in every test file.
=============================================================================
"""


import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

# Create a test client that wraps your FastAPI app.
# This lets you make HTTP requests without starting a real server.
client = TestClient(app)
