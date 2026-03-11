"""Goal Interpreter – parses raw user input into a structured goal."""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Simple keyword-based priority detector
_HIGH_PRIORITY_KEYWORDS = {"urgent", "critical", "asap", "important", "immediately"}
_LOW_PRIORITY_KEYWORDS = {"someday", "maybe", "low", "whenever", "eventually"}


def interpret_goal(title: str, description: str | None = None) -> dict[str, Any]:
    """
    Analyze raw user input and return a structured goal dict with:
    - normalized title
    - detected domain (finance, research, analysis, general)
    - suggested priority (1-10)
    - extracted context key-value pairs
    """
    combined = f"{title} {description or ''}".lower()

    # Domain detection
    domain = _detect_domain(combined)

    # Priority detection
    priority = _detect_priority(combined)

    # Numeric context (e.g. "1000 units")
    amounts = re.findall(r"\b(\d+(?:\.\d+)?)\s*(units?|dollars?|usd|\$|shares?|%)?", combined)
    context: dict[str, Any] = {"domain": domain}
    if amounts:
        context["detected_amounts"] = [
            {"value": float(a[0]), "unit": a[1] or "units"} for a in amounts
        ]

    logger.info("Interpreted goal: domain=%s priority=%d", domain, priority)
    return {
        "title": title.strip(),
        "description": description,
        "priority": priority,
        "context": context,
    }


def _detect_domain(text: str) -> str:
    if any(kw in text for kw in ("stock", "invest", "trading", "market", "finance", "profit", "loss")):
        return "finance"
    if any(kw in text for kw in ("research", "study", "analyze", "survey")):
        return "research"
    if any(kw in text for kw in ("simulation", "simulate", "model", "experiment")):
        return "simulation"
    if any(kw in text for kw in ("report", "dashboard", "visualize", "chart", "data")):
        return "analytics"
    return "general"


def _detect_priority(text: str) -> int:
    # Strip punctuation for keyword matching
    words = set(re.sub(r"[^\w\s]", "", text).split())
    if words & _HIGH_PRIORITY_KEYWORDS:
        return 8
    if words & _LOW_PRIORITY_KEYWORDS:
        return 2
    return 5
