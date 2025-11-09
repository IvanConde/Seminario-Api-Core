from fastapi import APIRouter, Request, HTTPException, Depends
import openai, os, requests
from sqlalchemy.orm import Session
from database import get_db
from services.conversation_service import ConversationService

router = APIRouter()
openai.api_key = os.getenv("OPENAI_API_KEY")

@router.post("/suggest_reply")
async def suggest_reply(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    conversation_id = body["conversation_id"]

    # 1️⃣ Obtener los mensajes directamente desde la base (sin otra request HTTP)
    service = ConversationService(db)
    conversation = await service.get_conversation_with_messages(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # 2️⃣ Preparar el contexto
    messages = conversation.messages[-10:]  # solo los últimos 10
    context = "\n".join([f"{m.sender_name}: {m.content}" for m in messages])

    # 3️⃣ Crear el prompt
    prompt = f"""
    Sos un asistente de atención al cliente amable y conciso.
    Te paso la conversación con el cliente, y quiero que sugieras una respuesta breve, empática y útil.
    Conversación:
    {context}
    Respuesta sugerida:
    """

    # 4️⃣ Llamar al modelo
    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    suggestion = completion.choices[0].message["content"]

    return {"suggestion": suggestion}
