"""
=============================================================================
FILE: tests/test_documents.py
PURPOSE: Unit tests for the /api/v1/projects/{project_id}/documents endpoint.
WHAT IT DOES:
  1. Tests that uploading a non-PDF file is rejected (400 failure case).
  2. Tests that uploading to a non-existent project returns 404.
WHY IT'S HERE:
  - Verifies the validation guards in doc_uploader.py work correctly.
  - We do NOT test actual PDF embedding (that requires Pinecone + model).
    Validation tests are fast and don't need external services.
=============================================================================
"""

import io
from tests.conftest import client


def test_upload_non_pdf_file():
    # Create a project first
    proj_response = client.post("/api/v1/projects/", json={"name": "Doc Test Project"})
    project_id = proj_response.json()["id"]

    # Try to upload a .txt file (not a PDF) — should be rejected
    fake_txt_file = io.BytesIO(b"This is not a PDF file")
    response = client.post(
        f"/api/v1/projects/{project_id}/documents",
        files={"file": ("notes.txt", fake_txt_file, "text/plain")}
    )

    assert response.status_code == 400              # Bad Request
    assert "PDF" in response.json()["detail"]       # Error message mentions PDF


def test_upload_to_invalid_project():
    # Try to upload a PDF to a project that doesn't exist
    fake_pdf = io.BytesIO(b"fake pdf content")
    response = client.post(
        "/api/v1/projects/non-existent-id/documents",
        files={"file": ("study.pdf", fake_pdf, "application/pdf")}
    )

    assert response.status_code == 404              # Project not found
