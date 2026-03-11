"""Integration tests for the FastAPI endpoints."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure models are registered on Base before anything else
import app.models.models  # noqa: F401
from app.database import Base, get_db
from app.main import app

# Use an in-memory SQLite database shared across connections (StaticPool)
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables once on the test engine
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def reset_db():
    """Drop and recreate tables before each test for isolation."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# Goals API
# ---------------------------------------------------------------------------

class TestGoalsAPI:
    def test_create_goal(self, client):
        resp = client.post("/api/v1/goals/", json={"title": "Test goal"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Test goal"
        assert data["status"] == "pending"

    def test_create_goal_with_priority(self, client):
        resp = client.post("/api/v1/goals/", json={"title": "High priority", "priority": 9})
        assert resp.status_code == 201
        assert resp.json()["priority"] == 9

    def test_list_goals_empty(self, client):
        resp = client.get("/api/v1/goals/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_goals_after_create(self, client):
        client.post("/api/v1/goals/", json={"title": "Goal 1"})
        client.post("/api/v1/goals/", json={"title": "Goal 2"})
        resp = client.get("/api/v1/goals/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_goal(self, client):
        create_resp = client.post("/api/v1/goals/", json={"title": "Fetch me"})
        goal_id = create_resp.json()["id"]
        resp = client.get(f"/api/v1/goals/{goal_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == goal_id

    def test_get_goal_not_found(self, client):
        resp = client.get("/api/v1/goals/99999")
        assert resp.status_code == 404

    def test_update_goal(self, client):
        create_resp = client.post("/api/v1/goals/", json={"title": "Old title"})
        goal_id = create_resp.json()["id"]
        resp = client.patch(f"/api/v1/goals/{goal_id}", json={"title": "New title"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "New title"

    def test_delete_goal(self, client):
        create_resp = client.post("/api/v1/goals/", json={"title": "To be deleted"})
        goal_id = create_resp.json()["id"]
        del_resp = client.delete(f"/api/v1/goals/{goal_id}")
        assert del_resp.status_code == 204
        get_resp = client.get(f"/api/v1/goals/{goal_id}")
        assert get_resp.status_code == 404

    def test_run_goal_pipeline(self, client):
        create_resp = client.post("/api/v1/goals/", json={"title": "Invest 500 in stocks"})
        goal_id = create_resp.json()["id"]
        run_resp = client.post(f"/api/v1/goals/{goal_id}/run")
        assert run_resp.status_code == 200
        data = run_resp.json()
        assert "tasks" in data
        assert len(data["tasks"]) > 0

    def test_run_non_pending_goal_returns_400(self, client):
        create_resp = client.post("/api/v1/goals/", json={"title": "Running goal"})
        goal_id = create_resp.json()["id"]
        # First run
        client.post(f"/api/v1/goals/{goal_id}/run")
        # Second run should fail (not pending)
        run_resp = client.post(f"/api/v1/goals/{goal_id}/run")
        assert run_resp.status_code == 400


# ---------------------------------------------------------------------------
# Tasks API
# ---------------------------------------------------------------------------

class TestTasksAPI:
    def test_list_tasks_empty(self, client):
        resp = client.get("/api/v1/tasks/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_tasks_created_after_pipeline(self, client):
        create_resp = client.post("/api/v1/goals/", json={"title": "Finance goal for tasks"})
        goal_id = create_resp.json()["id"]
        client.post(f"/api/v1/goals/{goal_id}/run")
        resp = client.get("/api/v1/tasks/", params={"goal_id": goal_id})
        assert resp.status_code == 200
        assert len(resp.json()) > 0

    def test_get_goal_tasks(self, client):
        create_resp = client.post("/api/v1/goals/", json={"title": "Task goal"})
        goal_id = create_resp.json()["id"]
        client.post(f"/api/v1/goals/{goal_id}/run")
        resp = client.get(f"/api/v1/tasks/goal/{goal_id}")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


# ---------------------------------------------------------------------------
# Memory API
# ---------------------------------------------------------------------------

class TestMemoryAPI:
    def test_list_memory_empty(self, client):
        resp = client.get("/api/v1/memory/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_memory_entry(self, client):
        resp = client.post("/api/v1/memory/", json={
            "entry_type": "outcome",
            "content": {"result": "ok"},
            "tags": ["test"],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["entry_type"] == "outcome"

    def test_delete_memory_entry(self, client):
        create_resp = client.post("/api/v1/memory/", json={
            "entry_type": "insight",
            "content": {"note": "delete me"},
        })
        entry_id = create_resp.json()["id"]
        del_resp = client.delete(f"/api/v1/memory/{entry_id}")
        assert del_resp.status_code == 204


# ---------------------------------------------------------------------------
# Analytics API
# ---------------------------------------------------------------------------

class TestAnalyticsAPI:
    def test_summary_empty_db(self, client):
        resp = client.get("/api/v1/analytics/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_goals" in data
        assert data["total_goals"] == 0

    def test_learning_insights(self, client):
        resp = client.get("/api/v1/analytics/learning")
        assert resp.status_code == 200
        data = resp.json()
        assert "tool_performance" in data
        assert "strategy_suggestions" in data
