"""Learning Engine – analyses historical outcomes to improve future decisions.

Currently implements simple statistical learning. Structured to accept
reinforcement-learning models in future iterations.
"""

import logging
import statistics
from typing import Any

from sqlalchemy.orm import Session

from app.models.models import ActionLog, ActionStatus

logger = logging.getLogger(__name__)


class LearningEngine:
    """Learns from historical action logs and memory entries."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def compute_tool_performance(self) -> dict[str, Any]:
        """Aggregate success rate and average duration per tool."""
        logs: list[ActionLog] = self.db.query(ActionLog).all()

        stats: dict[str, dict[str, Any]] = {}
        for log in logs:
            tool = log.tool_name
            if tool not in stats:
                stats[tool] = {"total": 0, "success": 0, "durations": []}
            stats[tool]["total"] += 1
            if log.status == ActionStatus.SUCCESS:
                stats[tool]["success"] += 1
            if log.duration_seconds is not None:
                stats[tool]["durations"].append(log.duration_seconds)

        result: dict[str, Any] = {}
        for tool, data in stats.items():
            durations = data["durations"]
            result[tool] = {
                "total_calls": data["total"],
                "success_rate": round(data["success"] / data["total"], 3) if data["total"] else 0,
                "avg_duration_seconds": round(statistics.mean(durations), 4) if durations else None,
            }

        logger.info("Computed performance for %d tools", len(result))
        return result

    def suggest_strategy_adjustments(self) -> list[dict[str, Any]]:
        """
        Produce a list of strategy-adjustment recommendations based on
        historical success rates.

        Returns items like:
        {"tool": "run_simulation", "recommendation": "Switch to backtest strategy",
         "reason": "Current strategy success rate 30% < threshold 50%"}
        """
        performance = self.compute_tool_performance()
        suggestions: list[dict[str, Any]] = []

        for tool, data in performance.items():
            rate = data["success_rate"]
            if rate < 0.5 and data["total_calls"] >= 3:
                suggestions.append({
                    "tool": tool,
                    "recommendation": f"Consider switching strategy for '{tool}'.",
                    "reason": f"Success rate {rate:.0%} is below the 50% threshold.",
                    "current_success_rate": rate,
                })

        logger.info("Generated %d strategy suggestions", len(suggestions))
        return suggestions

    def learn_from_outcome(
        self, tool_name: str, outcome: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Process a single action outcome and return an updated learning signal.

        In future this can update a Q-table or neural network weights.
        For now it returns a human-readable signal.
        """
        score = outcome.get("overall_score", outcome.get("score", 50))
        if isinstance(score, (int, float)):
            quality = "high" if score > 70 else ("medium" if score > 40 else "low")
        else:
            quality = "unknown"

        signal = {
            "tool": tool_name,
            "quality": quality,
            "reinforcement_delta": (float(score) - 50) / 50 if isinstance(score, (int, float)) else 0,
            "notes": f"Outcome quality '{quality}' recorded for '{tool_name}'.",
        }
        logger.debug("Learning signal: %s", signal)
        return signal
