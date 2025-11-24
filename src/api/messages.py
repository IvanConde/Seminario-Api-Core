"""Message API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.database import get_db
from src.schemas import MessageResponse, MessageCreate, UnifiedMessage, SendMessageRequest, SendMessageResponse
from src.services.message_service import MessageService
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: Optional[int] = Query(None),
    channel: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Obtener mensajes con filtros opcionales."""
    service = MessageService(db)
    return await service.get_messages(
        conversation_id=conversation_id,
        channel=channel,
        limit=limit,
        offset=offset
    )

@router.post("/messages", response_model=MessageResponse)
async def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo mensaje."""
    service = MessageService(db)
    return await service.create_message(message)

@router.post("/messages/unified")
async def receive_unified_message(
    message: UnifiedMessage,
    db: Session = Depends(get_db)
):
    """Endpoint para recibir mensajes unificados de los servicios de canal."""
    # Log del mensaje recibido en archivo
    import json
    from datetime import datetime
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "direction": "incoming",
        "channel": message.channel,
        "sender": message.sender,
        "message": message.message,
        "message_id": message.message_id,
        "message_type": message.message_type,
        "original_timestamp": message.timestamp
    }
    
    try:
        with open("logs/incoming_messages.txt", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as log_error:
        logger.error(f"Error writing to incoming log file: {log_error}")
    
    service = MessageService(db)
    try:
        result = await service.process_unified_message(message)
        logger.info(f"Unified message received from {message.channel}: {message.sender}")
        return {"status": "success", "message_id": result.id}
    except Exception as e:
        logger.error(f"Error processing unified message: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/messages/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un mensaje específico."""
    service = MessageService(db)
    message = await service.get_message_by_id(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.put("/messages/{message_id}/read")
async def mark_message_as_read(
    message_id: int,
    db: Session = Depends(get_db)
):
    """Marcar un mensaje como leído."""
    service = MessageService(db)
    success = await service.mark_message_as_read(message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "success", "message": "Message marked as read"}

@router.get("/messages/unread/count")
async def get_unread_count(
    conversation_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Obtener cantidad de mensajes no leídos."""
    service = MessageService(db)
    count = await service.get_unread_messages_count(conversation_id)
    return {"unread_count": count}

@router.post("/send", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    db: Session = Depends(get_db)
):
    """Enviar mensaje a través de un canal específico."""
    # This will forward the message to the appropriate channel service
    import httpx
    
    channel_ports = {
        "whatsapp": 8000,  # Puerto correcto del WhatsApp Service
        "gmail": 8001,
        "instagram": 8002
    }
    
    if request.channel not in channel_ports:
        raise HTTPException(status_code=400, detail=f"Unsupported channel: {request.channel}")
    print("Sending message to channel:", request.channel)
    port = channel_ports[request.channel]
    if request.channel == "whatsapp":
        url = f"https://dawne-umbellately-annett.ngrok-free.dev/send/{request.channel}"
    elif request.channel == "gmail":
        url = f"https://lilah-tophaceous-overhonestly.ngrok-free.dev/send/{request.channel}"
    elif request.channel == "instagram":
        url = f"https://phyllomic-fernande-hedonistically.ngrok-free.dev/send/{request.channel}"

    # Formatear número para WhatsApp
    formatted_to = request.to
    if request.channel == "whatsapp":
        if request.to.startswith("+"):
            # Remover el +
            number = request.to[1:]
            
            # Para números argentinos (+549...), remover solo el 9 del código de área
            if number.startswith("549"):
                formatted_to = "54" + number[3:]  # Remover "9" -> queda "54" + número local
            else:
                formatted_to = number  # Para otros países, solo remover el +
        else:
            formatted_to = request.to

    
    payload = {
        "to": formatted_to,
        "message": request.message,
        "message_type": request.message_type
    }
    
    if request.media_url:
        payload["media_url"] = request.media_url
    
    # Log del body que se envía a la API externa en archivo
    import json
    from datetime import datetime
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "channel": request.channel,
        "url": url,
        "payload": payload
    }
    
    try:
        with open("logs/outgoing_messages.txt", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as log_error:
        logger.error(f"Error writing to log file: {log_error}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            result = response.json()
            
            logger.info(f"Response from {request.channel} service: status={response.status_code}, result={result}")
            
            # Store outgoing message in database SIEMPRE (independiente del resultado de la API)
            service = MessageService(db)
            try:
                # Find conversation
                conversation = await service._get_or_create_conversation(
                    channel_name=request.channel,
                    participant_identifier=request.to
                )
                
                # Create message record
                from src.schemas import MessageCreate
                from datetime import datetime, timezone, timedelta
                
                # Usar timezone de Argentina (UTC-3)
                argentina_tz = timezone(timedelta(hours=-3))
                current_time = datetime.now(argentina_tz)
                
                message_data = MessageCreate(
                    conversation_id=conversation.id,
                    external_message_id=result.get("message_id") if result.get("success") else None,
                    content=request.message,
                    message_type=request.message_type,
                    direction="outgoing",
                    sender_identifier="system",  # Or current user
                    timestamp=current_time
                )
                
                await service.create_message(message_data)
                logger.info(f"Outgoing message persisted in DB for {request.channel}")
            except Exception as db_error:
                logger.error(f"Error persisting outgoing message in DB: {str(db_error)}")
            
            if response.status_code == 200 and result.get("success"):
                return SendMessageResponse(
                    success=True,
                    message_id=result.get("message_id"),
                    details=result
                )
            else:
                return SendMessageResponse(
                    success=False,
                    error=result.get("error", "Unknown error"),
                    details=result
                )
                
    except Exception as e:
        logger.error(f"Error sending message to {request.channel}: {str(e)}")
        return SendMessageResponse(
            success=False,
            error=str(e)
        )
