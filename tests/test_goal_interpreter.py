"""Tests for the GoalInterpreter module."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.modules.goal_interpreter import interpret_goal, _detect_domain, _detect_priority


class TestInterpretGoal:
    def test_basic_goal(self):
        result = interpret_goal("Buy groceries")
        assert result["title"] == "Buy groceries"
        assert result["priority"] == 5
        assert "domain" in result["context"]

    def test_finance_domain_detected(self):
        result = interpret_goal("Invest 1000 units in stock trading strategy")
        assert result["context"]["domain"] == "finance"

    def test_research_domain_detected(self):
        result = interpret_goal("Research the best machine learning frameworks and analyze data")
        assert result["context"]["domain"] == "research"

    def test_priority_elevated_for_urgent(self):
        result = interpret_goal("urgent: fix production bug")
        assert result["priority"] >= 7

    def test_priority_lowered_for_low(self):
        result = interpret_goal("someday clean up old files")
        assert result["priority"] <= 3

    def test_amount_extracted(self):
        result = interpret_goal("Invest 500 dollars in crypto")
        amounts = result["context"].get("detected_amounts", [])
        assert any(a["value"] == 500.0 for a in amounts)

    def test_description_passed_through(self):
        result = interpret_goal("My goal", description="Some description")
        assert result["description"] == "Some description"

    def test_simulation_domain(self):
        assert _detect_domain("run a simulation model") == "simulation"

    def test_analytics_domain(self):
        assert _detect_domain("generate a dashboard report") == "analytics"

    def test_general_domain_default(self):
        assert _detect_domain("do something random") == "general"
