"""Tests for the Decision Engine module."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.modules.decision_engine import decide_strategy, evaluate_outcome


class TestDecisionEngine:
    def test_returns_strategy_for_known_action(self):
        result = decide_strategy("fetch_market_data", {})
        assert "selected_strategy" in result
        assert result["selected_strategy"]

    def test_fallback_strategies_provided(self):
        result = decide_strategy("run_simulation", {})
        assert isinstance(result["fallback_strategies"], list)

    def test_unknown_action_gets_default(self):
        result = decide_strategy("nonexistent_action", {})
        assert result["selected_strategy"]

    def test_debug_mode_prefers_mock(self):
        result = decide_strategy("fetch_market_data", {"debug": True})
        assert "mock" in result["selected_strategy"]

    def test_reasoning_is_string(self):
        result = decide_strategy("run_analysis", {})
        assert isinstance(result["reasoning"], str)

    def test_evaluate_positive_pnl_high_score(self):
        outcome = evaluate_outcome({"profit_loss": 50})
        assert outcome["score"] > 50
        assert outcome["success"] is True

    def test_evaluate_negative_pnl_low_score(self):
        outcome = evaluate_outcome({"profit_loss": -60})
        assert outcome["score"] < 50
        assert outcome["success"] is False

    def test_evaluate_empty_result_zero_score(self):
        outcome = evaluate_outcome({})
        assert outcome["score"] == 0

    def test_evaluate_explicit_success_flag(self):
        outcome = evaluate_outcome({"success": True})
        assert outcome["score"] == 80.0

    def test_recommendation_is_string(self):
        outcome = evaluate_outcome({"profit_loss": 10})
        assert isinstance(outcome["recommendation"], str)
