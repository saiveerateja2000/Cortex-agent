"""Celery application and task definitions for background goal execution."""

import logging
from typing import Any

from celery import Celery
from sqlalchemy.orm import Session

from app.config import get_settings

settings = get_settings()

logger = logging.getLogger(__name__)

celery_app = Celery(
    "cortex_agent",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
)


# ---------------------------------------------------------------------------
# Public Celery tasks
# ---------------------------------------------------------------------------

@celery_app.task(name="execute_goal_pipeline", bind=True, max_retries=3)
def execute_goal_pipeline(self: Any, goal_id: int) -> dict[str, Any]:
    """Execute the full goal pipeline in the background."""
    from app.database import SessionLocal  # noqa: PLC0415

    db = SessionLocal()
    try:
        return _run_goal_pipeline(goal_id, db)
    except Exception as exc:
        logger.error("Pipeline failed for goal_id=%d: %s", goal_id, exc)
        raise self.retry(exc=exc, countdown=10)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Internal pipeline runner (also used for synchronous fallback)
# ---------------------------------------------------------------------------

def _run_goal_pipeline(goal_id: int, db: Session) -> dict[str, Any]:
    """
    Execute all pending tasks for a goal in sequence.
    Updates task statuses and logs actions to the database.
    """
    from app.models.models import ActionLog, ActionStatus, Goal, GoalStatus, Task, TaskStatus  # noqa: PLC0415
    from app.modules.action_executor import execute_action  # noqa: PLC0415
    from app.modules.decision_engine import decide_strategy, evaluate_outcome  # noqa: PLC0415
    from app.modules.memory_system import MemorySystem  # noqa: PLC0415

    goal: Goal | None = db.get(Goal, goal_id)
    if goal is None:
        logger.error("Goal %d not found", goal_id)
        return {"error": f"Goal {goal_id} not found"}

    goal.status = GoalStatus.EXECUTING
    db.commit()

    memory = MemorySystem(db)
    completed = 0
    failed = 0

    tasks: list[Task] = (
        db.query(Task)
        .filter(Task.goal_id == goal_id, Task.status == TaskStatus.PENDING)
        .order_by(Task.order)
        .all()
    )

    for task in tasks:
        task.status = TaskStatus.RUNNING
        db.commit()

        action_type = task.action_type or "run_analysis"
        params = task.parameters or {}

        # Decision engine chooses the strategy
        decision = decide_strategy(action_type, goal.context or {})
        strategy = decision["selected_strategy"]

        # Execute with primary strategy; retry with fallbacks on failure
        exec_result: dict[str, Any] = {"success": False, "result": None, "error": "No strategy tried"}
        strategies_to_try = [strategy] + decision["fallback_strategies"][:2]

        for strat in strategies_to_try:
            exec_result = execute_action(action_type, params, strategy=strat)
            if exec_result["success"]:
                break
            logger.warning("Strategy '%s' failed for task %d, trying next", strat, task.id)

        # Log the action
        log = ActionLog(
            task_id=task.id,
            tool_name=action_type,
            status=ActionStatus.SUCCESS if exec_result["success"] else ActionStatus.FAILURE,
            input_data=params,
            output_data=exec_result.get("result"),
            error_message=exec_result.get("error"),
            duration_seconds=exec_result.get("duration_seconds"),
            attempt_number=exec_result.get("attempt", 1),
        )
        db.add(log)

        if exec_result["success"]:
            result_data = exec_result["result"] or {}
            # Evaluate outcome via decision engine
            outcome_eval = evaluate_outcome(result_data)
            task.status = TaskStatus.COMPLETED
            task.result = {**result_data, "_evaluation": outcome_eval}
            completed += 1

            # Persist to memory
            memory.store(
                entry_type="outcome",
                content={"task": task.name, "result": result_data, "evaluation": outcome_eval},
                goal_id=goal_id,
                tags=[action_type, goal.status.value],
            )
            memory.record_metric(
                name=f"task_score_{action_type}",
                value=outcome_eval.get("score", 0),
                context={"goal_id": goal_id, "task_id": task.id},
            )
        else:
            task.status = TaskStatus.FAILED
            task.error_message = exec_result.get("error")
            failed += 1

        db.commit()

    # Update goal status
    if failed == 0:
        goal.status = GoalStatus.COMPLETED
    elif completed == 0:
        goal.status = GoalStatus.FAILED
    else:
        goal.status = GoalStatus.COMPLETED  # partial success → completed

    db.commit()
    logger.info("Pipeline done for goal_id=%d: %d completed, %d failed", goal_id, completed, failed)
    return {"goal_id": goal_id, "completed": completed, "failed": failed}
