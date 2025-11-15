from fastapi import APIRouter, Request
import httpx
from src.entities.chatbot_entities import WahaRequest
from src.mapper.waha_mapper import map_to_chatbot_payload, map_to_send_text_payload
import os
from src.services.speech2text import convert_speech_to_text
import src.utils.environment as env
import json
from src.utils.logger import logger

router = APIRouter(prefix="/waha", tags=["waha"])


async def send_waha_message(user: str, message: str, session: str):
    """Send a message to WAHA API sendText endpoint"""
    try:
        payload = map_to_send_text_payload(user, message, session)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{env.WAHA_API_URL}/api/sendText",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Api-Key": env.WAHA_API_KEY,
                },
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error sending message to WAHA: {str(e)}")
        return None


async def handle_error_response(
    request: WahaRequest, user_message: str, technical_message: str, chatbot_data=None
):
    """Handle error response by sending WAHA message and returning error dict"""
    await send_waha_message(request.payload.from_, user_message, request.session)
    error_response = {"status": "error", "message": technical_message}
    if chatbot_data:
        error_response["chatbot_response"] = chatbot_data
    return error_response


@router.post("/webhook", summary="Process webhook")
async def chatbot_endpoint(request: WahaRequest):
    logger.info(f"Received webhook request: {request}")
    try:
        # assistant = env.ASSISTANT
        # assistantName = env.ASSISTANT_NAME

        if request.payload.hasMedia:
            logger.info(f"Received media: {request.payload.media.mimetype if request.payload.media else 'No media object'}")
            if request.payload.media.mimetype == "audio/ogg; codecs=opus":
                logger.info(f"Received audio: {request.payload.media.url}")
                try:
                    text_message = await convert_speech_to_text(request.payload.media.url)
                    logger.info(f"Transcripción en Router: {text_message}")
                    if text_message is None:
                        logger.error(f"No se pudo transcribir el audio - convert_speech_to_text retornó None")
                        return {
                            "status": "error",
                            "message": "No se pudo transcribir el audio"
                        }
                    else:
                        request.payload.body = text_message
                except Exception as e:
                    logger.error(f"Excepción al transcribir el audio: {str(e)} - Tipo: {type(e).__name__}", exc_info=True)
                    return {
                        "status": "error",
                        "message": f"Error al transcribir el audio: {str(e)}"
                    }

        """
        chatbot_payload = map_to_chatbot_payload(request, assistant, assistantName)
        # Call the chatbot API
        async with httpx.AsyncClient(timeout=30.0) as client:
            chatbot_response = await client.post(
                f"{env.CHATBOT_API_URL}/v1/llm/question",
                json=chatbot_payload,
                headers={"Content-Type": "application/json"}
            )
            chatbot_response.raise_for_status()
            chatbot_data = chatbot_response.json()
        
        # Validate chatbot API response
        if chatbot_response.status_code != 200 or chatbot_data.get("status") != "OK":
            return await handle_error_response(
                request,
                "Lo siento, no puedo procesar tu mensaje en este momento. Por favor intenta nuevamente más tarde.",
                f"Chatbot API error - Status code: {chatbot_response.status_code}, Status: {chatbot_data.get('status', 'unknown')}",
                chatbot_data
            )
        
        # Extract data from the response
        data = chatbot_data.get("data", {})
        response_text = data.get("answer", "")
        answer_id = data.get("answerId", "")
        conversation_id = data.get("conversationId", "")
        
        # Send the chatbot response to WAHA
        send_data = await send_waha_message(
            user=request.payload.from_,
            message=response_text,
            session=request.session
        )
        
        return {
            "status": "success",
            "message": "Message processed and sent successfully",
            "chatbot_response": chatbot_data,
            "send_response": send_data
        }
        """

        return {
            "status": "success",
            "message": "Message processed and sent successfully",
            "chatbot_response": "chatbot_data",
            "send_response": "send_data",
        }

    except httpx.HTTPError as e:
        logger.error(
            f"HTTP error occurred: {str(e)} - Tipo: {type(e).__name__} - URL: {getattr(e.request, 'url', 'N/A') if hasattr(e, 'request') else 'N/A'}",
            exc_info=True,
        )
        return await handle_error_response(
            request,
            "Lo siento, hay un problema de conexión. Por favor intenta nuevamente más tarde.",
            f"HTTP error occurred: {type(e).__name__} - {str(e)}",
        )
    except Exception as e:
        logger.error(
            f"An error occurred: {str(e)} - Tipo: {type(e).__name__}", exc_info=True
        )
        return await handle_error_response(
            request,
            "Lo siento, ocurrió un error inesperado. Por favor intenta nuevamente más tarde.",
            f"An error occurred: {type(e).__name__} - {str(e)}",
        )
