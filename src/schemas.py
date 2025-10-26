"""Pydantic schemas for API requests/responses."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class MessageBase(BaseModel):
    content: str
    message_type: str = "text"
    direction: str  # incoming, outgoing
    sender_name: Optional[str] = None
    sender_identifier: str
    timestamp: datetime
    message_metadata: Optional[str] = None

class MessageCreate(MessageBase):
    conversation_id: int
    external_message_id: Optional[str] = None

class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    external_message_id: Optional[str] = None
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    participant_name: Optional[str] = None
    participant_identifier: str
    is_active: bool = True

class ConversationCreate(ConversationBase):
    channel_id: int
    external_id: str

class ConversationResponse(ConversationBase):
    id: int
    channel_id: int
    external_id: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True

class ChannelResponse(BaseModel):
    id: int
    name: str
    display_name: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UnifiedMessage(BaseModel):
    """Formato unificado para mensajes de todos los canales"""
    channel: str
    sender: str
    message: str
    timestamp: str
    message_id: Optional[str] = None
    message_type: str = "text"
    sender_name: Optional[str] = None

class SendMessageRequest(BaseModel):
    """Request para enviar mensaje a través de un canal"""
    channel: str
    to: str
    message: str
    message_type: str = "text"
    media_url: Optional[str] = None

class SendMessageResponse(BaseModel):
    """Response del envío de mensaje"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    details: Optional[dict] = None
