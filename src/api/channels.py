"""Channel API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.schemas import ChannelResponse
from src.services.channel_service import ChannelService
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/channels", response_model=List[ChannelResponse])
async def get_channels(db: Session = Depends(get_db)):
    """Obtener todos los canales activos."""
    service = ChannelService(db)
    return await service.get_all_channels()

@router.get("/channels/{channel_name}", response_model=ChannelResponse)
async def get_channel(
    channel_name: str,
    db: Session = Depends(get_db)
):
    """Obtener un canal específico por nombre."""
    service = ChannelService(db)
    channel = await service.get_channel_by_name(channel_name)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel

@router.get("/channels/{channel_name}/stats")
async def get_channel_stats(
    channel_name: str,
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de un canal."""
    service = ChannelService(db)
    stats = await service.get_channel_stats(channel_name)
    if not stats:
        raise HTTPException(status_code=404, detail="Channel not found")
    return stats
