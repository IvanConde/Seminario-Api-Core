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


class HistoryCreate(BaseModel):
    user: str
    action: str
    action_type: str
    details: str
    endpoint: Optional[str] = None
    method: Optional[str] = None


class HistoryEntryResponse(BaseModel):
    id: int
    date: str
    time: str
    user: str
    action: str
    actionType: str
    details: str


class HistoryStatsResponse(BaseModel):
    action_type: str
    count: int

# Authentication schemas
class UserRegister(BaseModel):
    """Schema para registro de usuario"""
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    """Schema para login de usuario"""
    username: str  # Puede ser username o email
    password: str

class Token(BaseModel):
    """Schema para token JWT"""
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    """Schema para respuesta de usuario"""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserRoleUpdate(BaseModel):
    """Schema para actualizar rol de usuario"""
    role: str  # "admin" o "colaborador"

class UserStatusUpdate(BaseModel):
    """Schema para actualizar estado de usuario"""
    is_active: bool
