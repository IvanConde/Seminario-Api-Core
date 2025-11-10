from fastapi import APIRouter, Request, HTTPException, Depends
import os, requests
from sqlalchemy.orm import Session
from src.database import get_db
from src.services.conversation_service import ConversationService
from src.config import settings
#from openai import OpenAI
import openai

router = APIRouter()
client = openai.OpenAI(api_key=settings.openai_api_key)

@router.post("/ia_service/suggest_reply")
async def suggest_reply(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    conversation_id = body["conversation_id"]

    # 1️⃣ Obtener los mensajes directamente desde la base (sin otra request HTTP)
    service = ConversationService(db)
    conversation = await service.get_conversation_with_messages(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # 2️⃣ Preparar el contexto (últimos 10 mensajes ordenados por timestamp)
    sorted_messages = sorted(
        conversation.messages,
        key=lambda m: m.timestamp or m.created_at
    )
    messages = sorted_messages[-10:]
    context = "\n".join([f"{m.sender_name}: {m.content}" for m in messages])
    print("[IA suggest_reply] Contexto utilizado:\n", context)

    # 3️⃣ Crear el prompt
    prompt = f"""
    Sos un asistente virtual de atención al cliente para una tienda de ropa mayorista y minorista.

    Tu objetivo es responder de forma breve, amable y útil a los mensajes de los clientes.
    Siempre hablá en un tono profesional, cordial y cercano, como si fueras parte del equipo de ventas o atención de la tienda.

    Tené en cuenta estas reglas:
    - Respondé solo sobre temas relacionados con la ropa, la tienda, los productos, los precios, los envíos, los horarios o los medios de contacto.
    - Si el mensaje no tiene que ver con ropa o con el comercio (por ejemplo, si preguntan sobre comida, tecnología, servicios o cualquier otro tema), aclarales amablemente que la tienda se dedica exclusivamente a la venta de indumentaria.
    - Evitá respuestas largas: priorizá la claridad y la calidez.
    - Si el mensaje parece una duda de compra o un interés por un producto, respondé de forma que fomente la conversación o la venta (por ejemplo, ofreciendo ayuda, catálogo o información adicional).
    - Nunca inventes información que no figure en el contexto o que no corresponda a una tienda de ropa.

    Conversación con el cliente:
    {context}
    Respuesta sugerida:
    """

    # 4️⃣ Llamar al modelo
    completion = client.responses.create(
    model="gpt-4o-mini",
    input=prompt,
    )
    suggestion = completion.output[0].content[0].text

    return {"suggestion": suggestion}
