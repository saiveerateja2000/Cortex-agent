"""Memory System – stores and retrieves goals, outcomes, and metrics."""

import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.models import MemoryEntry, PerformanceMetric

logger = logging.getLogger(__name__)


class MemorySystem:
    """Provides a high-level interface to the persistent memory store."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Memory entries
    # ------------------------------------------------------------------

    def store(
        self,
        entry_type: str,
        content: dict[str, Any],
        goal_id: int | None = None,
        tags: list[str] | None = None,
    ) -> MemoryEntry:
        """Persist a new memory entry and return it."""
        entry = MemoryEntry(
            goal_id=goal_id,
            entry_type=entry_type,
            content=content,
            tags=tags or [],
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        logger.info("Stored memory entry id=%d type=%s", entry.id, entry_type)
        return entry

    def recall(
        self,
        entry_type: str | None = None,
        goal_id: int | None = None,
        limit: int = 50,
    ) -> list[MemoryEntry]:
        """Retrieve memory entries, optionally filtered."""
        query = self.db.query(MemoryEntry)
        if entry_type:
            query = query.filter(MemoryEntry.entry_type == entry_type)
        if goal_id is not None:
            query = query.filter(MemoryEntry.goal_id == goal_id)
        return query.order_by(MemoryEntry.created_at.desc()).limit(limit).all()

    def search_by_tag(self, tag: str, limit: int = 50) -> list[MemoryEntry]:
        """Return entries that contain the given tag (JSON array search)."""
        # SQLite JSON path: cast tags column to text and look for tag
        entries = (
            self.db.query(MemoryEntry)
            .order_by(MemoryEntry.created_at.desc())
            .limit(200)
            .all()
        )
        return [e for e in entries if e.tags and tag in e.tags][:limit]

    # ------------------------------------------------------------------
    # Performance metrics
    # ------------------------------------------------------------------

    def record_metric(
        self,
        name: str,
        value: float,
        context: dict[str, Any] | None = None,
    ) -> PerformanceMetric:
        """Record a performance metric data point."""
        metric = PerformanceMetric(
            metric_name=name,
            metric_value=value,
            context=context or {},
            recorded_at=datetime.utcnow(),
        )
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        logger.debug("Recorded metric %s=%.4f", name, value)
        return metric

    def get_metrics(self, name: str | None = None, limit: int = 100) -> list[PerformanceMetric]:
        """Fetch recent performance metrics, optionally filtered by name."""
        query = self.db.query(PerformanceMetric)
        if name:
            query = query.filter(PerformanceMetric.metric_name == name)
        return query.order_by(PerformanceMetric.recorded_at.desc()).limit(limit).all()
