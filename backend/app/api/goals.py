"""Goals API router."""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Goal, GoalStatus, Task, TaskStatus
from app.modules.goal_interpreter import interpret_goal
from app.modules.planner import plan_tasks
from app.schemas.schemas import GoalCreate, GoalResponse, GoalUpdate, PipelineResponse, TaskResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db)) -> GoalResponse:
    """Create a new goal (no pipeline execution)."""
    interpreted = interpret_goal(payload.title, payload.description)
    goal = Goal(
        title=interpreted["title"],
        description=interpreted["description"],
        priority=payload.priority or interpreted["priority"],
        context={**(interpreted["context"] or {}), **(payload.context or {})},
        status=GoalStatus.PENDING,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    logger.info("Created goal id=%d", goal.id)
    return GoalResponse.model_validate(goal)


@router.post("/{goal_id}/run", response_model=PipelineResponse)
def run_goal_pipeline(
    goal_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> PipelineResponse:
    """
    Interpret the goal, generate tasks, and queue them for execution.
    Returns immediately with the planned task list.
    """
    goal = db.get(Goal, goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")

    if goal.status not in (GoalStatus.PENDING, GoalStatus.FAILED):
        raise HTTPException(
            status_code=400,
            detail=f"Goal is already in '{goal.status}' state.",
        )

    # Plan tasks
    task_defs = plan_tasks(goal.title, goal.context or {})
    db_tasks: list[Task] = []
    for td in task_defs:
        task = Task(
            goal_id=goal.id,
            name=td["name"],
            description=td.get("description"),
            action_type=td.get("action_type"),
            parameters=td.get("parameters"),
            order=td.get("order", 0),
            status=TaskStatus.PENDING,
        )
        db.add(task)
        db_tasks.append(task)

    goal.status = GoalStatus.PLANNING
    db.commit()
    for t in db_tasks:
        db.refresh(t)
    db.refresh(goal)

    # Queue execution via Celery (non-blocking)
    background_tasks.add_task(_trigger_execution, goal_id)

    return PipelineResponse(
        goal=GoalResponse.model_validate(goal),
        tasks=[TaskResponse.model_validate(t) for t in db_tasks],
        message=f"Pipeline started: {len(db_tasks)} tasks queued.",
    )


@router.get("/", response_model=list[GoalResponse])
def list_goals(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[GoalResponse]:
    goals = db.query(Goal).order_by(Goal.created_at.desc()).offset(skip).limit(limit).all()
    return [GoalResponse.model_validate(g) for g in goals]


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(goal_id: int, db: Session = Depends(get_db)) -> GoalResponse:
    goal = db.get(Goal, goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return GoalResponse.model_validate(goal)


@router.patch("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: int,
    payload: GoalUpdate,
    db: Session = Depends(get_db),
) -> GoalResponse:
    goal = db.get(Goal, goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)

    db.commit()
    db.refresh(goal)
    return GoalResponse.model_validate(goal)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: int, db: Session = Depends(get_db)) -> None:
    goal = db.get(Goal, goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()


# ---------------------------------------------------------------------------
# Internal helper (executed in background)
# ---------------------------------------------------------------------------

def _trigger_execution(goal_id: int) -> None:
    """Trigger Celery task to execute the goal pipeline asynchronously."""
    try:
        from app.tasks.celery_tasks import execute_goal_pipeline  # noqa: PLC0415

        execute_goal_pipeline.delay(goal_id)
        logger.info("Celery task queued for goal_id=%d", goal_id)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not queue Celery task (Redis unavailable?): %s", exc)
        # Fall back to synchronous execution
        from app.database import SessionLocal  # noqa: PLC0415
        from app.tasks.celery_tasks import _run_goal_pipeline  # noqa: PLC0415

        db = SessionLocal()
        try:
            _run_goal_pipeline(goal_id, db)
        finally:
            db.close()
