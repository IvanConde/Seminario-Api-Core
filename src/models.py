"""Database models for unified messaging system."""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from src.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    COLABORADOR = "colaborador"


class ConversationCategory(str, enum.Enum):
    CONSULTA = "consulta"
    PEDIDO = "pedido"
    RECLAMO = "reclamo"
    SIN_CATEGORIA = "sin_categoria"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.COLABORADOR)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Channel(Base):
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # whatsapp, gmail, instagram
    display_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="channel")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    external_id = Column(String(255), nullable=False)  # ID del canal externo
    participant_name = Column(String(255))
    participant_identifier = Column(String(255), nullable=False)  # email, phone, username
    is_active = Column(Boolean, default=True)
    category = Column(
        Enum(
            ConversationCategory,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=ConversationCategory.SIN_CATEGORIA,
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    channel = relationship("Channel", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    external_message_id = Column(String(255))  # ID del mensaje en el canal externo
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, image, audio, video, document
    direction = Column(String(10), nullable=False)  # incoming, outgoing
    sender_name = Column(String(255))
    sender_identifier = Column(String(255), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    is_read = Column(Boolean, default=False)
    message_metadata = Column(Text)  # JSON string para datos adicionales
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class HistoryEntry(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(255), nullable=False)
    action = Column(String(255), nullable=False)
    action_type = Column(String(50), nullable=False)
    details = Column(Text, nullable=False)
    endpoint = Column(String(255))
    method = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)