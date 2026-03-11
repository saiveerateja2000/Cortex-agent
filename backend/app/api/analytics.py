"""Analytics API router."""

import logging
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import ActionLog, ActionStatus, Goal, GoalStatus, Task, TaskStatus
from app.modules.learning_engine import LearningEngine
from app.modules.memory_system import MemorySystem
from app.schemas.schemas import AnalyticsSummary, MetricResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(db: Session = Depends(get_db)) -> AnalyticsSummary:
    """High-level dashboard summary."""
    total_goals = db.query(Goal).count()
    goals_by_status: dict[str, int] = {}
    for status in GoalStatus:
        goals_by_status[status.value] = db.query(Goal).filter(Goal.status == status).count()

    total_tasks = db.query(Task).count()
    tasks_by_status: dict[str, int] = {}
    for status in TaskStatus:
        tasks_by_status[status.value] = db.query(Task).filter(Task.status == status).count()

    total_actions = db.query(ActionLog).count()
    success_actions = db.query(ActionLog).filter(ActionLog.status == ActionStatus.SUCCESS).count()
    success_rate = round(success_actions / total_actions, 3) if total_actions else 0.0

    avg_tasks = round(total_tasks / total_goals, 2) if total_goals else 0.0

    return AnalyticsSummary(
        total_goals=total_goals,
        goals_by_status=goals_by_status,
        total_tasks=total_tasks,
        tasks_by_status=tasks_by_status,
        total_actions=total_actions,
        success_rate=success_rate,
        average_tasks_per_goal=avg_tasks,
    )


@router.get("/metrics", response_model=list[MetricResponse])
def get_metrics(
    name: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[MetricResponse]:
    ms = MemorySystem(db)
    metrics = ms.get_metrics(name=name, limit=limit)
    return [MetricResponse.model_validate(m) for m in metrics]


@router.get("/learning", response_model=dict[str, Any])
def get_learning_insights(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Return tool performance stats and strategy adjustment suggestions."""
    le = LearningEngine(db)
    return {
        "tool_performance": le.compute_tool_performance(),
        "strategy_suggestions": le.suggest_strategy_adjustments(),
    }
