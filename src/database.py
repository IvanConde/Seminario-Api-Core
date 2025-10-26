"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=True,  # Set to False in production
    pool_pre_ping=True,
    pool_recycle=300
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database tables."""
    from src.models import Channel, Conversation, Message
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create default channels if they don't exist
    db = SessionLocal()
    try:
        # Check if channels exist
        if not db.query(Channel).first():
            # Create default channels
            channels = [
                Channel(name="whatsapp", display_name="WhatsApp"),
                Channel(name="gmail", display_name="Gmail"),
                Channel(name="instagram", display_name="Instagram")
            ]
            
            for channel in channels:
                db.add(channel)
            
            db.commit()
            print("✅ Default channels created")
        else:
            print("✅ Channels already exist")
    except Exception as e:
        print(f"❌ Error creating default channels: {e}")
        db.rollback()
    finally:
        db.close()
