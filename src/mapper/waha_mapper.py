from src.entities.chatbot_entities import WahaRequest
from typing import Dict, Any, Optional

def map_to_chatbot_payload(request: WahaRequest, assistant: str, assistantName: str) -> Dict[str, str]:
    return {

        "user": request.payload.from_,
        "question": request.payload.body,

        "assistant": assistant,
        "assistantName": assistantName,
        "memory": True,
        "history": "",
        "conversationId": request.payload.from_.split('@')[0][2:] # Obtener el valor del numero telefonico sin el prefijo ni el @
    }

def map_to_send_text_payload(
    user: str, 
    response_text: str, 
    session: str,
    reply_to: Optional[str] = None,
    link_preview: bool = True,
    link_preview_high_quality: bool = False
) -> Dict[str, Any]:
    return {
        "chatId": user,
        "reply_to": reply_to,
        "text": response_text,
        "linkPreview": link_preview,
        "linkPreviewHighQuality": link_preview_high_quality,
        "session": session
    }
