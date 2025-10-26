"""Conversation service for handling conversation operations."""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from src.models import Conversation, Channel, Message
from src.schemas import ConversationCreate, ConversationResponse, MessageResponse
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ConversationService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_conversations(
        self,
        channel_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ConversationResponse]:
        """Get conversations with optional channel filter."""
        query = self.db.query(Conversation)
        
        if channel_id:
            query = query.filter(Conversation.channel_id == channel_id)
        
        conversations = query.order_by(desc(Conversation.updated_at)).offset(offset).limit(limit).all()
        
        return [ConversationResponse.from_orm(conv) for conv in conversations]
    
    async def get_conversation_by_id(self, conversation_id: int) -> Optional[ConversationResponse]:
        """Get a specific conversation by ID."""
        conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            return ConversationResponse.from_orm(conversation)
        return None
    
    async def create_conversation(self, conversation_data: ConversationCreate) -> ConversationResponse:
        """Create a new conversation."""
        conversation = Conversation(**conversation_data.dict())
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        logger.info(f"Conversation created: {conversation.id}")
        return ConversationResponse.from_orm(conversation)
    
    async def get_conversation_with_messages(
        self,
        conversation_id: int,
        limit: int = 50
    ) -> Optional[ConversationResponse]:
        """Get conversation with its messages."""
        conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            return None
        
        # Get recent messages
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(desc(Message.timestamp)).limit(limit).all()
        
        # Convert to response format
        conv_response = ConversationResponse.from_orm(conversation)
        conv_response.messages = [MessageResponse.from_orm(msg) for msg in messages]
        
        return conv_response
    
    async def update_conversation_participant_name(
        self,
        conversation_id: int,
        participant_name: str
    ) -> bool:
        """Update participant name in conversation."""
        conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.participant_name = participant_name
            self.db.commit()
            logger.info(f"Conversation {conversation_id} participant name updated")
            return True
        return False
    
    async def deactivate_conversation(self, conversation_id: int) -> bool:
        """Deactivate a conversation."""
        conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.is_active = False
            self.db.commit()
            logger.info(f"Conversation {conversation_id} deactivated")
            return True
        return False
