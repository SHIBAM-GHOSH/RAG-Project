"""
=============================================================================
FILE: tests/test_projects.py
PURPOSE: Unit tests for the /api/v1/projects/ endpoints.
WHAT IT DOES:
  1. Tests creating a new project (success case).
  2. Tests listing all projects (success case).
  3. Tests creating a project with missing name (validation failure case).
WHY IT'S HERE:
  - Ensures the Projects API and DB integration works correctly.
  - Catches regressions if db_models or project_creator.py is changed.
=============================================================================
"""

from tests.conftest import client


def test_create_project():
    # Send POST request to create a project
    response = client.post("/api/v1/projects/", json={"name": "Physics-101"})

    assert response.status_code == 200          # Request succeeded
    assert response.json()["name"] == "Physics-101"  # Name saved correctly
    assert "id" in response.json()              # UUID id was generated


def test_list_projects():
    # Send GET request to list all projects
    response = client.get("/api/v1/projects/")

    assert response.status_code == 200          # Request succeeded
    assert isinstance(response.json(), list)    # Response is a list


def test_create_project_missing_name():
    # Send POST with no name field — Pydantic should reject it
    response = client.post("/api/v1/projects/", json={})

    assert response.status_code == 422          # Unprocessable Entity (validation error)
