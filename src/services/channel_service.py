"""Channel service for handling channel operations."""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional

from src.models import Channel, Conversation, Message
from src.schemas import ChannelResponse
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ChannelService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_all_channels(self) -> List[ChannelResponse]:
        """Get all active channels."""
        channels = self.db.query(Channel).filter(Channel.is_active == True).all()
        return [ChannelResponse.from_orm(channel) for channel in channels]
    
    async def get_channel_by_name(self, channel_name: str) -> Optional[ChannelResponse]:
        """Get channel by name."""
        channel = self.db.query(Channel).filter(Channel.name == channel_name).first()
        if channel:
            return ChannelResponse.from_orm(channel)
        return None
    
    async def get_channel_stats(self, channel_name: str) -> dict:
        """Get statistics for a channel."""
        channel = self.db.query(Channel).filter(Channel.name == channel_name).first()
        if not channel:
            return {}
        
        # Get conversation count
        conversation_count = self.db.query(Conversation).filter(
            Conversation.channel_id == channel.id
        ).count()
        
        # Get message count
        message_count = self.db.query(Message).join(Conversation).filter(
            Conversation.channel_id == channel.id
        ).count()
        
        # Get unread message count
        unread_count = self.db.query(Message).join(Conversation).filter(
            and_(
                Conversation.channel_id == channel.id,
                Message.is_read == False
            )
        ).count()
        
        return {
            "channel_name": channel_name,
            "conversation_count": conversation_count,
            "message_count": message_count,
            "unread_count": unread_count
        }
