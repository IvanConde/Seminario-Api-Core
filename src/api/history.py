"""History API endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas import HistoryCreate, HistoryEntryResponse, HistoryStatsResponse
from src.services.history_service import HistoryService
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


def _service(db: Session) -> HistoryService:
    return HistoryService(db)


@router.get("/history", response_model=List[HistoryEntryResponse])
async def get_history(
    action_type: Optional[str] = Query(None, alias="actionType"),
    user: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: Optional[int] = Query(None, ge=1, le=500),
    offset: Optional[int] = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    service = _service(db)
    return await service.get_history(
        action_type=action_type,
        user=user,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get("/history/stats", response_model=List[HistoryStatsResponse])
async def get_history_stats(db: Session = Depends(get_db)):
    service = _service(db)
    return await service.get_stats()


@router.post("/history/log", response_model=HistoryEntryResponse, status_code=201)
async def log_history(entry: HistoryCreate, db: Session = Depends(get_db)):
    try:
        service = _service(db)
        return await service.log_action(entry)
    except Exception as exc:  # pragma: no cover - unexpected
        logger.error("Error logging history entry: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Error logging history entry")
