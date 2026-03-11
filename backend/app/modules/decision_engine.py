"""Decision Engine – chooses the best strategy for each task.

Rule-based today; structured to accept reinforcement-learning policies later.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Action type → ranked list of strategies (first = preferred)
_STRATEGY_REGISTRY: dict[str, list[str]] = {
    "fetch_market_data": ["yfinance_api", "alpha_vantage_api", "mock_data"],
    "run_analysis": ["statistical_analysis", "ml_analysis", "simple_summary"],
    "run_simulation": ["monte_carlo", "backtest", "random_walk"],
    "evaluate_outcome": ["risk_adjusted_return", "simple_pnl", "rule_based_score"],
    "store_memory": ["sqlite_persist", "in_memory_cache"],
    "web_search": ["serpapi", "mock_search"],
    "call_external_api": ["http_client", "mock_response"],
}

_DEFAULT_STRATEGIES = ["default_strategy", "fallback_strategy"]


def decide_strategy(action_type: str, context: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluate available strategies and return the best one.

    Returns a dict with:
    - selected_strategy: name of chosen strategy
    - fallback_strategies: remaining strategies to try on failure
    - reasoning: human-readable explanation
    """
    candidates = _STRATEGY_REGISTRY.get(action_type, _DEFAULT_STRATEGIES)[:]

    # Simple rule: prefer mock/fallback strategies in debug/test mode
    debug_mode = context.get("debug", False)
    if debug_mode:
        # Move mock/fallback to the front
        candidates = sorted(candidates, key=lambda s: 0 if "mock" in s else 1)

    selected = candidates[0]
    fallbacks = candidates[1:]

    reasoning = _explain_choice(action_type, selected, context)
    logger.info("Decision: action=%s strategy=%s", action_type, selected)

    return {
        "selected_strategy": selected,
        "fallback_strategies": fallbacks,
        "reasoning": reasoning,
    }


def evaluate_outcome(result: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluate the outcome of an action and produce a score + recommendation.

    Returns:
    - score: 0-100
    - success: bool
    - recommendation: next-step hint
    """
    score = _compute_score(result)
    success = score >= 50
    recommendation = _recommend(score, result)

    return {"score": score, "success": success, "recommendation": recommendation}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _explain_choice(action_type: str, strategy: str, context: dict[str, Any]) -> str:
    if "mock" in strategy:
        return f"Mock strategy selected for '{action_type}' (debug/test mode)."
    return (
        f"Strategy '{strategy}' selected for '{action_type}' based on rule priority "
        f"and available context keys: {list(context.keys())}."
    )


def _compute_score(result: dict[str, Any]) -> float:
    """Compute a 0-100 quality score from an action result."""
    if not result:
        return 0.0

    # If result carries an explicit success flag, use it
    if "success" in result:
        return 80.0 if result["success"] else 20.0

    # Finance heuristic: positive P&L is good
    pnl = result.get("profit_loss", result.get("pnl", None))
    if pnl is not None:
        if pnl > 0:
            return min(100.0, 60.0 + float(pnl))
        return max(0.0, 40.0 + float(pnl))

    # Default: moderate score if data is present
    return 60.0 if result else 0.0


def _recommend(score: float, result: dict[str, Any]) -> str:
    if score >= 80:
        return "Excellent result. Proceed with confidence."
    if score >= 60:
        return "Good result. Minor optimisation possible."
    if score >= 40:
        return "Marginal result. Consider adjusting strategy parameters."
    return "Poor result. Switch to a fallback strategy or re-plan the goal."
