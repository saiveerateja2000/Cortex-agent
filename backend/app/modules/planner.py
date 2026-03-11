"""Planner – breaks a goal into an ordered list of tasks."""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Domain → task templates
_TASK_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "finance": [
        {"name": "Fetch market data", "action_type": "fetch_market_data", "order": 1,
         "description": "Retrieve current and historical price data for relevant assets."},
        {"name": "Run financial analysis", "action_type": "run_analysis", "order": 2,
         "description": "Compute technical indicators and statistical summaries."},
        {"name": "Simulate trading strategy", "action_type": "run_simulation", "order": 3,
         "description": "Back-test or paper-trade the chosen strategy."},
        {"name": "Evaluate profit/loss", "action_type": "evaluate_outcome", "order": 4,
         "description": "Assess P&L and risk metrics from the simulation."},
        {"name": "Store results in memory", "action_type": "store_memory", "order": 5,
         "description": "Persist outcomes and performance data for future learning."},
    ],
    "research": [
        {"name": "Gather information", "action_type": "web_search", "order": 1,
         "description": "Search and collect relevant sources."},
        {"name": "Summarise findings", "action_type": "run_analysis", "order": 2,
         "description": "Condense collected data into key insights."},
        {"name": "Store results in memory", "action_type": "store_memory", "order": 3,
         "description": "Save the research summary for future reference."},
    ],
    "simulation": [
        {"name": "Prepare simulation parameters", "action_type": "run_analysis", "order": 1,
         "description": "Define and validate input parameters."},
        {"name": "Execute simulation", "action_type": "run_simulation", "order": 2,
         "description": "Run the simulation model."},
        {"name": "Evaluate outcomes", "action_type": "evaluate_outcome", "order": 3,
         "description": "Analyse simulation results."},
        {"name": "Store results in memory", "action_type": "store_memory", "order": 4,
         "description": "Record simulation data for learning."},
    ],
    "analytics": [
        {"name": "Collect data", "action_type": "fetch_market_data", "order": 1,
         "description": "Fetch the required data set."},
        {"name": "Analyse data", "action_type": "run_analysis", "order": 2,
         "description": "Apply statistical or ML-based analysis."},
        {"name": "Generate report", "action_type": "evaluate_outcome", "order": 3,
         "description": "Produce a structured report of findings."},
        {"name": "Store results in memory", "action_type": "store_memory", "order": 4,
         "description": "Archive report for future reference."},
    ],
    "general": [
        {"name": "Analyse goal", "action_type": "run_analysis", "order": 1,
         "description": "Break down the goal into actionable components."},
        {"name": "Execute primary action", "action_type": "call_external_api", "order": 2,
         "description": "Perform the main action required by the goal."},
        {"name": "Evaluate and store results", "action_type": "store_memory", "order": 3,
         "description": "Review outcomes and commit to memory."},
    ],
}


def plan_tasks(goal_title: str, context: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Return an ordered list of task dicts for the given goal context.
    Each dict contains: name, description, action_type, order, parameters.
    """
    domain: str = context.get("domain", "general")
    templates = _TASK_TEMPLATES.get(domain, _TASK_TEMPLATES["general"])

    tasks: list[dict[str, Any]] = []
    for template in templates:
        task = {**template}
        # Inject context-specific parameters
        task["parameters"] = _build_parameters(task["action_type"], goal_title, context)
        tasks.append(task)

    logger.info("Planned %d tasks for domain '%s'", len(tasks), domain)
    return tasks


def _build_parameters(action_type: str, goal_title: str, context: dict[str, Any]) -> dict[str, Any]:
    params: dict[str, Any] = {"goal": goal_title}
    amounts = context.get("detected_amounts", [])

    if action_type == "fetch_market_data":
        params["symbol"] = "AAPL"  # default demo symbol
        params["period"] = "1mo"

    elif action_type == "run_simulation":
        params["strategy"] = "momentum"
        if amounts:
            params["capital"] = amounts[0]["value"]
            params["unit"] = amounts[0]["unit"]

    elif action_type == "run_analysis":
        params["method"] = "statistical_summary"

    elif action_type == "evaluate_outcome":
        params["metrics"] = ["profit_loss", "sharpe_ratio", "max_drawdown"]

    elif action_type == "store_memory":
        params["entry_type"] = "outcome"

    return params
