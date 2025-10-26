"""Core API - Unified messaging system."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from typing import List

from src.database import init_db
from src.api import messages, conversations, channels
from src.utils.logger import get_logger

logger = get_logger(__name__)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """Broadcast message to all connected clients."""
        if self.active_connections:
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.active_connections.remove(conn)
            
            logger.info(f"Broadcasted to {len(self.active_connections)} clients")

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Core API...")
    await init_db()
    logger.info("✅ Database initialized")
    yield
    # Shutdown
    logger.info("🛑 Shutting down Core API...")

app = FastAPI(
    title="Core Unified Messaging API",
    description="API para unificar mensajes de WhatsApp, Gmail e Instagram",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(messages.router, prefix="/api/v1", tags=["messages"])
app.include_router(conversations.router, prefix="/api/v1", tags=["conversations"])
app.include_router(channels.router, prefix="/api/v1", tags=["channels"])

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Core Unified Messaging API",
        "version": "1.0.0",
        "description": "API para unificar mensajes de WhatsApp, Gmail e Instagram"
    }

@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": "Core Unified Messaging API",
        "version": "1.0.0",
        "database": "connected",
        "websocket_connections": len(manager.active_connections)
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time messaging."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"WebSocket message received: {data}")
            
            # Echo back for testing
            await manager.send_personal_message(f"Echo: {data}", websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/broadcast")
async def broadcast_message(message: str):
    """Broadcast a message to all connected WebSocket clients."""
    await manager.broadcast(message)
    return {"status": "success", "message": "Broadcasted to all clients"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8003, reload=True)
