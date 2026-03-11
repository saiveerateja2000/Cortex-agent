"""Action Executor – pluggable tool registry that executes tasks."""

import logging
import random
import time
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def _fetch_market_data(params: dict[str, Any]) -> dict[str, Any]:
    """Simulate fetching financial market data."""
    symbol = params.get("symbol", "AAPL")
    period = params.get("period", "1mo")
    logger.info("Fetching market data: symbol=%s period=%s", symbol, period)

    # Simulated response (real implementation would call yfinance / Alpha Vantage)
    prices = [round(150 + random.gauss(0, 5), 2) for _ in range(20)]
    return {
        "symbol": symbol,
        "period": period,
        "prices": prices,
        "current_price": prices[-1],
        "average_price": round(sum(prices) / len(prices), 2),
        "data_points": len(prices),
    }


def _run_analysis(params: dict[str, Any]) -> dict[str, Any]:
    """Run statistical analysis on whatever data is in params."""
    method = params.get("method", "statistical_summary")
    logger.info("Running analysis: method=%s", method)

    # Simulated analysis output
    return {
        "method": method,
        "mean": round(random.uniform(100, 200), 2),
        "std_dev": round(random.uniform(5, 20), 2),
        "trend": random.choice(["bullish", "bearish", "sideways"]),
        "confidence": round(random.uniform(0.5, 0.99), 2),
    }


def _run_simulation(params: dict[str, Any]) -> dict[str, Any]:
    """Simulate a trading or other quantitative strategy."""
    strategy = params.get("strategy", "momentum")
    capital = float(params.get("capital", 1000))
    logger.info("Running simulation: strategy=%s capital=%s", strategy, capital)

    # Simulated P&L
    returns = [random.gauss(0.001, 0.02) for _ in range(30)]
    final_value = capital * (1 + sum(returns))
    pnl = round(final_value - capital, 2)
    sharpe = round(random.uniform(-1, 3), 2)
    max_drawdown = round(random.uniform(0.01, 0.25), 2)

    return {
        "strategy": strategy,
        "initial_capital": capital,
        "final_value": round(final_value, 2),
        "profit_loss": pnl,
        "return_pct": round((pnl / capital) * 100, 2),
        "sharpe_ratio": sharpe,
        "max_drawdown": max_drawdown,
        "num_trades": random.randint(5, 30),
    }


def _evaluate_outcome(params: dict[str, Any]) -> dict[str, Any]:
    """Evaluate outcomes against desired metrics."""
    metrics = params.get("metrics", ["profit_loss"])
    logger.info("Evaluating outcome: metrics=%s", metrics)

    evaluation = {}
    for metric in metrics:
        evaluation[metric] = round(random.uniform(-50, 150), 2)

    evaluation["overall_score"] = round(random.uniform(40, 95), 1)
    evaluation["recommendation"] = random.choice([
        "Continue strategy", "Adjust parameters", "Switch strategy",
    ])
    return evaluation


def _store_memory(params: dict[str, Any]) -> dict[str, Any]:
    """Placeholder – real persistence is handled by the MemorySystem."""
    logger.info("Storing memory entry (placeholder action)")
    return {"stored": True, "entry_type": params.get("entry_type", "outcome")}


def _call_external_api(params: dict[str, Any]) -> dict[str, Any]:
    """Generic external API call stub."""
    endpoint = params.get("endpoint", "https://example.com/api")
    logger.info("Calling external API: %s", endpoint)
    return {"endpoint": endpoint, "status_code": 200, "response": {"ok": True}}


def _web_search(params: dict[str, Any]) -> dict[str, Any]:
    """Stub web search tool."""
    query = params.get("goal", "general query")
    logger.info("Web search: %s", query)
    return {
        "query": query,
        "results": [
            {"title": f"Result {i}", "snippet": f"Snippet for {query}", "url": f"https://example.com/{i}"}
            for i in range(1, 4)
        ],
    }


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

_TOOL_REGISTRY: dict[str, Any] = {
    "fetch_market_data": _fetch_market_data,
    "run_analysis": _run_analysis,
    "run_simulation": _run_simulation,
    "evaluate_outcome": _evaluate_outcome,
    "store_memory": _store_memory,
    "call_external_api": _call_external_api,
    "web_search": _web_search,
}


def execute_action(
    tool_name: str,
    parameters: dict[str, Any],
    strategy: str | None = None,
    max_retries: int = 2,
) -> dict[str, Any]:
    """
    Execute a named tool with optional retry logic.

    Returns a dict with: success, result, error, duration_seconds, attempt.
    """
    tool = _TOOL_REGISTRY.get(tool_name)
    if tool is None:
        return {
            "success": False,
            "result": None,
            "error": f"Unknown tool: '{tool_name}'",
            "duration_seconds": 0.0,
            "attempt": 1,
        }

    params = {**parameters}
    if strategy:
        params["_strategy"] = strategy

    last_error: str | None = None
    for attempt in range(1, max_retries + 1):
        start = time.perf_counter()
        try:
            result = tool(params)
            duration = round(time.perf_counter() - start, 4)
            logger.info("Tool '%s' succeeded (attempt %d) in %.4fs", tool_name, attempt, duration)
            return {
                "success": True,
                "result": result,
                "error": None,
                "duration_seconds": duration,
                "attempt": attempt,
            }
        except Exception as exc:  # noqa: BLE001
            duration = round(time.perf_counter() - start, 4)
            last_error = str(exc)
            logger.warning(
                "Tool '%s' failed (attempt %d): %s", tool_name, attempt, last_error
            )
            if attempt < max_retries:
                time.sleep(0.1 * attempt)

    return {
        "success": False,
        "result": None,
        "error": last_error or "Unknown error",
        "duration_seconds": 0.0,
        "attempt": max_retries,
    }


def list_tools() -> list[str]:
    """Return the names of all registered tools."""
    return list(_TOOL_REGISTRY.keys())
