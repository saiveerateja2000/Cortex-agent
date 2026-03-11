"""Memory API router."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import MemoryEntry
from app.modules.memory_system import MemorySystem
from app.schemas.schemas import MemoryEntryCreate, MemoryEntryResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/", response_model=list[MemoryEntryResponse])
def list_memory(
    entry_type: str | None = None,
    goal_id: int | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[MemoryEntryResponse]:
    ms = MemorySystem(db)
    entries = ms.recall(entry_type=entry_type, goal_id=goal_id, limit=limit)
    return [MemoryEntryResponse.model_validate(e) for e in entries]


@router.post("/", response_model=MemoryEntryResponse, status_code=status.HTTP_201_CREATED)
def create_memory_entry(
    payload: MemoryEntryCreate,
    db: Session = Depends(get_db),
) -> MemoryEntryResponse:
    ms = MemorySystem(db)
    entry = ms.store(
        entry_type=payload.entry_type,
        content=payload.content,
        goal_id=payload.goal_id,
        tags=payload.tags,
    )
    return MemoryEntryResponse.model_validate(entry)


@router.get("/{entry_id}", response_model=MemoryEntryResponse)
def get_memory_entry(entry_id: int, db: Session = Depends(get_db)) -> MemoryEntryResponse:
    entry = db.get(MemoryEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Memory entry not found")
    return MemoryEntryResponse.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory_entry(entry_id: int, db: Session = Depends(get_db)) -> None:
    entry = db.get(MemoryEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Memory entry not found")
    db.delete(entry)
    db.commit()
