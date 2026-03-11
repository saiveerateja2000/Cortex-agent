"""Tests for the Action Executor module."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.modules.action_executor import execute_action, list_tools


class TestActionExecutor:
    def test_list_tools_not_empty(self):
        tools = list_tools()
        assert len(tools) > 0

    def test_known_tools_present(self):
        tools = list_tools()
        for expected in ["fetch_market_data", "run_analysis", "run_simulation", "evaluate_outcome"]:
            assert expected in tools

    def test_fetch_market_data_succeeds(self):
        result = execute_action("fetch_market_data", {"symbol": "AAPL"})
        assert result["success"] is True
        assert "prices" in result["result"]

    def test_run_analysis_succeeds(self):
        result = execute_action("run_analysis", {"method": "statistical_summary"})
        assert result["success"] is True
        assert "mean" in result["result"]

    def test_run_simulation_succeeds(self):
        result = execute_action("run_simulation", {"capital": 1000, "strategy": "momentum"})
        assert result["success"] is True
        assert "profit_loss" in result["result"]

    def test_evaluate_outcome_succeeds(self):
        result = execute_action("evaluate_outcome", {"metrics": ["profit_loss"]})
        assert result["success"] is True
        assert "overall_score" in result["result"]

    def test_unknown_tool_returns_failure(self):
        result = execute_action("does_not_exist", {})
        assert result["success"] is False
        assert "Unknown tool" in result["error"]

    def test_duration_is_float(self):
        result = execute_action("run_analysis", {})
        assert isinstance(result["duration_seconds"], float)

    def test_attempt_number_present(self):
        result = execute_action("run_simulation", {})
        assert "attempt" in result

    def test_store_memory_tool(self):
        result = execute_action("store_memory", {"entry_type": "outcome"})
        assert result["success"] is True

    def test_web_search_tool(self):
        result = execute_action("web_search", {"goal": "test query"})
        assert result["success"] is True
        assert "results" in result["result"]

    def test_call_external_api_tool(self):
        result = execute_action("call_external_api", {"endpoint": "https://example.com"})
        assert result["success"] is True
