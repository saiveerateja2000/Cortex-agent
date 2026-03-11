"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.models import ActionStatus, GoalStatus, TaskStatus


# ---------------------------------------------------------------------------
# Goal schemas
# ---------------------------------------------------------------------------

class GoalCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    priority: int = Field(default=5, ge=1, le=10)
    context: dict[str, Any] | None = None


class GoalUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    priority: int | None = Field(default=None, ge=1, le=10)
    status: GoalStatus | None = None
    context: dict[str, Any] | None = None


class GoalResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: GoalStatus
    priority: int
    context: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Task schemas
# ---------------------------------------------------------------------------

class TaskCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    order: int = 0
    action_type: str | None = None
    parameters: dict[str, Any] | None = None


class TaskResponse(BaseModel):
    id: int
    goal_id: int
    name: str
    description: str | None
    status: TaskStatus
    order: int
    action_type: str | None
    parameters: dict[str, Any] | None
    result: dict[str, Any] | None
    error_message: str | None
    celery_task_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# ActionLog schemas
# ---------------------------------------------------------------------------

class ActionLogResponse(BaseModel):
    id: int
    task_id: int
    tool_name: str
    status: ActionStatus
    input_data: dict[str, Any] | None
    output_data: dict[str, Any] | None
    error_message: str | None
    duration_seconds: float | None
    attempt_number: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Memory schemas
# ---------------------------------------------------------------------------

class MemoryEntryCreate(BaseModel):
    goal_id: int | None = None
    entry_type: str = Field(..., max_length=50)
    content: dict[str, Any]
    tags: list[str] | None = None


class MemoryEntryResponse(BaseModel):
    id: int
    goal_id: int | None
    entry_type: str
    content: dict[str, Any]
    tags: list[str] | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Performance metric schemas
# ---------------------------------------------------------------------------

class MetricResponse(BaseModel):
    id: int
    metric_name: str
    metric_value: float
    context: dict[str, Any] | None
    recorded_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Pipeline / agent response
# ---------------------------------------------------------------------------

class PipelineResponse(BaseModel):
    goal: GoalResponse
    tasks: list[TaskResponse]
    message: str


class AnalyticsSummary(BaseModel):
    total_goals: int
    goals_by_status: dict[str, int]
    total_tasks: int
    tasks_by_status: dict[str, int]
    total_actions: int
    success_rate: float
    average_tasks_per_goal: float
