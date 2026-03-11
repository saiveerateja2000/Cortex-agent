"""Tests for the Planner module."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.modules.planner import plan_tasks


class TestPlanner:
    def test_finance_tasks_generated(self):
        tasks = plan_tasks("Invest 1000 in stocks", {"domain": "finance"})
        assert len(tasks) >= 3
        action_types = [t["action_type"] for t in tasks]
        assert "fetch_market_data" in action_types
        assert "run_simulation" in action_types

    def test_research_tasks_generated(self):
        tasks = plan_tasks("Research AI trends", {"domain": "research"})
        action_types = [t["action_type"] for t in tasks]
        assert "web_search" in action_types

    def test_general_tasks_fallback(self):
        tasks = plan_tasks("Do something", {"domain": "general"})
        assert len(tasks) >= 2

    def test_tasks_have_required_fields(self):
        tasks = plan_tasks("Test", {"domain": "finance"})
        for task in tasks:
            assert "name" in task
            assert "action_type" in task
            assert "order" in task
            assert "parameters" in task

    def test_tasks_ordered(self):
        tasks = plan_tasks("Finance goal", {"domain": "finance"})
        orders = [t["order"] for t in tasks]
        assert orders == sorted(orders)

    def test_simulation_parameters_include_capital(self):
        tasks = plan_tasks(
            "Invest 5000 units",
            {"domain": "finance", "detected_amounts": [{"value": 5000.0, "unit": "units"}]},
        )
        sim_tasks = [t for t in tasks if t["action_type"] == "run_simulation"]
        assert sim_tasks
        assert sim_tasks[0]["parameters"].get("capital") == 5000.0

    def test_unknown_domain_falls_back_to_general(self):
        tasks = plan_tasks("Unknown domain task", {"domain": "nonexistent"})
        assert len(tasks) >= 1
