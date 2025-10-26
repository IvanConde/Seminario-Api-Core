"""Conversation API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.database import get_db
from src.schemas import ConversationResponse, ConversationCreate
from src.services.conversation_service import ConversationService
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    channel_id: Optional[int] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Obtener conversaciones con filtros opcionales."""
    service = ConversationService(db)
    return await service.get_conversations(
        channel_id=channel_id,
        limit=limit,
        offset=offset
    )

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
):
    """Crear una nueva conversación."""
    from src.models import Channel
    
    # Validar que el canal existe
    channel = db.query(Channel).filter(Channel.id == conversation.channel_id).first()
    if not channel:
        raise HTTPException(
            status_code=400, 
            detail=f"Channel with id {conversation.channel_id} not found"
        )
    
    service = ConversationService(db)
    return await service.create_conversation(conversation)

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """Obtener una conversación específica con sus mensajes."""
    service = ConversationService(db)
    conversation = await service.get_conversation_with_messages(
        conversation_id=conversation_id,
        limit=limit
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.put("/conversations/{conversation_id}/participant")
async def update_participant_name(
    conversation_id: int,
    participant_name: str,
    db: Session = Depends(get_db)
):
    """Actualizar el nombre del participante en una conversación."""
    service = ConversationService(db)
    success = await service.update_conversation_participant_name(
        conversation_id=conversation_id,
        participant_name=participant_name
    )
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "success", "message": "Participant name updated"}

@router.put("/conversations/{conversation_id}/deactivate")
async def deactivate_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Desactivar una conversación."""
    service = ConversationService(db)
    success = await service.deactivate_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "success", "message": "Conversation deactivated"}
