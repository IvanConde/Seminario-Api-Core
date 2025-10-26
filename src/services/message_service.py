"""Message service for handling message operations."""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import datetime
import json

from src.models import Message, Conversation, Channel
from src.schemas import MessageCreate, MessageResponse, UnifiedMessage
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MessageService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_messages(
        self,
        conversation_id: Optional[int] = None,
        channel: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[MessageResponse]:
        """Get messages with optional filters."""
        query = self.db.query(Message)
        
        if conversation_id:
            query = query.filter(Message.conversation_id == conversation_id)
        
        if channel:
            query = query.join(Conversation).join(Channel).filter(Channel.name == channel)
        
        messages = query.order_by(desc(Message.timestamp)).offset(offset).limit(limit).all()
        
        return [MessageResponse.from_orm(msg) for msg in messages]
    
    async def get_message_by_id(self, message_id: int) -> Optional[MessageResponse]:
        """Get a specific message by ID."""
        message = self.db.query(Message).filter(Message.id == message_id).first()
        if message:
            return MessageResponse.from_orm(message)
        return None
    
    async def create_message(self, message_data: MessageCreate) -> MessageResponse:
        """Create a new message."""
        message = Message(**message_data.dict())
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        logger.info(f"Message created: {message.id}")
        return MessageResponse.from_orm(message)
    
    async def process_unified_message(self, unified_msg: UnifiedMessage) -> MessageResponse:
        """Process a unified message from channel services."""
        # Find or create conversation
        conversation = await self._get_or_create_conversation(
            channel_name=unified_msg.channel,
            participant_identifier=unified_msg.sender
        )
        
        # Parse timestamp
        try:
            timestamp = datetime.fromisoformat(unified_msg.timestamp.replace('Z', '+00:00'))
        except:
            timestamp = datetime.utcnow()
        
        # Create message
        message_data = MessageCreate(
            conversation_id=conversation.id,
            external_message_id=unified_msg.message_id,
            content=unified_msg.message,
            message_type=unified_msg.message_type,
            direction="incoming",
            sender_name=unified_msg.sender_name,
            sender_identifier=unified_msg.sender,
            timestamp=timestamp
        )
        
        message = await self.create_message(message_data)
        
        logger.info(f"Unified message processed: {unified_msg.channel} from {unified_msg.sender}")
        return message
    
    async def _get_or_create_conversation(
        self,
        channel_name: str,
        participant_identifier: str
    ) -> Conversation:
        """Get or create a conversation for a participant in a channel."""
        # Get channel
        channel = self.db.query(Channel).filter(Channel.name == channel_name).first()
        if not channel:
            raise ValueError(f"Channel {channel_name} not found")
        
        # Try to find existing conversation
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.channel_id == channel.id,
                Conversation.participant_identifier == participant_identifier
            )
        ).first()
        
        if not conversation:
            # Create new conversation
            conversation = Conversation(
                channel_id=channel.id,
                external_id=f"{channel_name}_{participant_identifier}",
                participant_identifier=participant_identifier,
                participant_name=None  # Will be updated when we have more info
            )
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            
            logger.info(f"New conversation created: {conversation.id}")
        
        return conversation
    
    async def mark_message_as_read(self, message_id: int) -> bool:
        """Mark a message as read."""
        message = self.db.query(Message).filter(Message.id == message_id).first()
        if message:
            message.is_read = True
            self.db.commit()
            logger.info(f"Message {message_id} marked as read")
            return True
        return False
    
    async def get_unread_messages_count(self, conversation_id: Optional[int] = None) -> int:
        """Get count of unread messages."""
        query = self.db.query(Message).filter(Message.is_read == False)
        
        if conversation_id:
            query = query.filter(Message.conversation_id == conversation_id)
        
        return query.count()
