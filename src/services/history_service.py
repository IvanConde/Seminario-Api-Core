"""History service for tracking user actions."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models import HistoryEntry
from src.schemas import HistoryCreate, HistoryEntryResponse, HistoryStatsResponse
from src.utils.logger import get_logger

logger = get_logger(__name__)


class HistoryService:
    def __init__(self, db: Session):
        self.db = db

    async def log_action(self, entry: HistoryCreate) -> HistoryEntryResponse:
        history = HistoryEntry(
            user=entry.user,
            action=entry.action,
            action_type=entry.action_type,
            details=entry.details,
            endpoint=entry.endpoint,
            method=entry.method,
            created_at=datetime.utcnow()
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        logger.info("History entry created: %s", history.id)
        return _to_response(history)

    async def get_history(
        self,
        action_type: Optional[str] = None,
        user: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[HistoryEntryResponse]:
        query = self.db.query(HistoryEntry)

        if action_type:
            query = query.filter(HistoryEntry.action_type == action_type)
        if user:
            query = query.filter(HistoryEntry.user.ilike(f"%{user}%"))
        if search:
            like_term = f"%{search}%"
            query = query.filter(
                (HistoryEntry.user.ilike(like_term))
                | (HistoryEntry.action.ilike(like_term))
                | (HistoryEntry.details.ilike(like_term))
            )

        query = query.order_by(HistoryEntry.created_at.desc())

        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        entries = query.all()
        return [_to_response(entry) for entry in entries]

    async def get_stats(self) -> List[HistoryStatsResponse]:
        rows = (
            self.db.query(HistoryEntry.action_type, func.count(HistoryEntry.id).label("count"))
            .group_by(HistoryEntry.action_type)
            .all()
        )
        return [HistoryStatsResponse(action_type=row.action_type, count=row.count) for row in rows]


def _to_response(entry: HistoryEntry) -> HistoryEntryResponse:
    created_at = entry.created_at or datetime.utcnow()
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    date_str = f"{created_at.day} {months[created_at.month - 1]} {created_at.year}"
    time_str = created_at.strftime("%H:%M")

    return HistoryEntryResponse(
        id=entry.id,
        date=date_str,
        time=time_str,
        user=entry.user,
        action=entry.action,
        actionType=entry.action_type,
        details=entry.details,
    )
