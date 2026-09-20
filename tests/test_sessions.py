"""
=============================================================================
FILE: tests/test_sessions.py
PURPOSE: Unit tests for the /api/v1/projects/{project_id}/sessions endpoints.
WHAT IT DOES:
  1. Tests creating a session inside a valid project (success case).
  2. Tests listing sessions for a valid project (success case).
  3. Tests creating a session in a non-existent project (404 failure case).
WHY IT'S HERE:
  - Sessions require a valid project_id (foreign key constraint).
  - These tests verify the full project → session chain works end-to-end.
=============================================================================
"""

from tests.conftest import client


def test_create_session():
    # Step 1: Create a project first to get a valid project_id
    proj_response = client.post("/api/v1/projects/", json={"name": "Session Test Project"})
    project_id = proj_response.json()["id"]

    # Step 2: Create a session inside that project
    response = client.post(
        f"/api/v1/projects/{project_id}/sessions",
        json={"name": "s1"}
    )

    assert response.status_code == 200                      # Request succeeded
    assert response.json()["name"] == "s1"                  # Session name saved correctly
    assert response.json()["project_id"] == project_id      # Linked to correct project


def test_list_sessions():
    # Create a project and a session, then list sessions
    proj_response = client.post("/api/v1/projects/", json={"name": "List Sessions Project"})
    project_id = proj_response.json()["id"]

    client.post(f"/api/v1/projects/{project_id}/sessions", json={"name": "s1"})

    response = client.get(f"/api/v1/projects/{project_id}/sessions")

    assert response.status_code == 200              # Request succeeded
    assert isinstance(response.json(), list)        # Response is a list
    assert len(response.json()) >= 1                # At least 1 session exists


def test_create_session_invalid_project():
    # Try to create a session in a project that doesn't exist
    response = client.post(
        "/api/v1/projects/non-existent-id/sessions",
        json={"name": "s1"}
    )

    assert response.status_code == 404              # Project not found
