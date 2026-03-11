"""Tasks API router."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import ActionLog, Goal, Task
from app.schemas.schemas import ActionLogResponse, TaskResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    goal_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[TaskResponse]:
    query = db.query(Task).order_by(Task.goal_id, Task.order)
    if goal_id is not None:
        query = query.filter(Task.goal_id == goal_id)
    tasks = query.offset(skip).limit(limit).all()
    return [TaskResponse.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)) -> TaskResponse:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.get("/{task_id}/actions", response_model=list[ActionLogResponse])
def get_task_actions(task_id: int, db: Session = Depends(get_db)) -> list[ActionLogResponse]:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    logs = (
        db.query(ActionLog)
        .filter(ActionLog.task_id == task_id)
        .order_by(ActionLog.created_at.desc())
        .all()
    )
    return [ActionLogResponse.model_validate(log) for log in logs]


@router.get("/goal/{goal_id}", response_model=list[TaskResponse])
def get_goal_tasks(goal_id: int, db: Session = Depends(get_db)) -> list[TaskResponse]:
    goal = db.get(Goal, goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    tasks = (
        db.query(Task)
        .filter(Task.goal_id == goal_id)
        .order_by(Task.order)
        .all()
    )
    return [TaskResponse.model_validate(t) for t in tasks]
