import httpx
import io
import os
from urllib.parse import urlparse, urlunparse
from google.genai import types
from google import genai
from src.utils.environment import (
    WAHA_API_URL, 
    WAHA_API_KEY,
    GOOGLE_APPLICATION_CREDENTIALS,
    GCP_PROJECT_ID,
    GCP_LOCATION,
    VERTEX_AI_MODEL
)
from src.utils.logger import logger


# Cliente de Vertex AI (se inicializa una sola vez)
_vertex_client = None

def _get_vertex_client():
    """
    Obtiene o crea una instancia del cliente de Vertex AI.
    Configura las credenciales de Google Cloud automáticamente.
    En Cloud Run, usa las credenciales predeterminadas de la aplicación.
    """
    global _vertex_client
    if _vertex_client is None:
        # Configurar la variable de entorno para las credenciales solo si existe el archivo y la variable está configurada
        if GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
            logger.info(f"Credenciales de GCP configuradas desde archivo: {GOOGLE_APPLICATION_CREDENTIALS}")
        else:
            logger.info("Usando credenciales predeterminadas de la aplicación (Application Default Credentials)")
        
        _vertex_client = genai.Client(
            vertexai=True,
            project=GCP_PROJECT_ID,
            location=GCP_LOCATION,
        )
        logger.info(f"Cliente de Vertex AI inicializado - Proyecto: {GCP_PROJECT_ID}, Región: {GCP_LOCATION}")
    return _vertex_client


async def convert_image_to_text(url_media: str, model_name: str = None) -> str:
    """
    Convierte una imagen o PDF a texto (OCR/descripción) usando Google Vertex AI.
    
    Args:
        url_media: URL del archivo de imagen o PDF (puede tener localhost:3000)
        model_name: Nombre del modelo de Vertex AI a usar (opcional, usa VERTEX_AI_MODEL por defecto)
        
    Returns:
        str: Descripción/texto extraído de la imagen o PDF, o None si hay un error
    """
    try:
        # Usar el modelo por defecto si no se especifica uno
        if model_name is None:
            model_name = VERTEX_AI_MODEL
        logger.info(f"Iniciando conversión de imagen/PDF a texto. URL: {url_media}")
        
        # Reemplazar localhost:3000 con el WAHA_API_URL real
        parsed_url = urlparse(url_media)
        waha_parsed = urlparse(WAHA_API_URL)
        
        # Construir la URL correcta reemplazando el scheme, netloc del URL original
        corrected_url = urlunparse((
            waha_parsed.scheme,  # http o https
            waha_parsed.netloc,  # hostname:port
            parsed_url.path,     # ruta del archivo
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment
        ))
        
        logger.info(f"URL corregida para descargar archivo: {corrected_url}")
        
        # Descargar el archivo (imagen o PDF)
        headers = {
            "X-Api-Key": WAHA_API_KEY
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            logger.info(f"Descargando archivo...")
            response = await client.get(corrected_url, headers=headers)
            response.raise_for_status()
            image_data = response.content
            logger.info(f"Archivo descargado exitosamente. Tamaño: {len(image_data)} bytes")
        
        # Detectar el tipo MIME del archivo (imagen o PDF)
        mime_type = "image/jpeg"  # Por defecto para WhatsApp
        if url_media.lower().endswith('.png'):
            mime_type = "image/png"
        elif url_media.lower().endswith('.jpg') or url_media.lower().endswith('.jpeg'):
            mime_type = "image/jpeg"
        elif url_media.lower().endswith('.webp'):
            mime_type = "image/webp"
        elif url_media.lower().endswith('.gif'):
            mime_type = "image/gif"
        elif url_media.lower().endswith('.pdf'):
            mime_type = "application/pdf"
        
        # Validar que sea una imagen o PDF válido
        if not (mime_type.startswith('image/') or mime_type == 'application/pdf'):
            logger.error(f"El archivo no es una imagen o PDF válido. MIME type: {mime_type}")
            return None
        
        logger.info(f"Tipo MIME detectado: {mime_type}")
        
        # Crear BytesIO con la imagen
        image_file = io.BytesIO(image_data)
        
        # Obtener cliente de Vertex AI
        client = _get_vertex_client()
        
        # Configurar el prompt para descripción/extracción de texto
        if mime_type == 'application/pdf':
            prompt = "Analiza este documento PDF (DNI peruano) y extrae los Apellidos, Prenombres/Pre Nombres, Sexo, Fecha de Nacimiento y numero de documento (DNI). En el caso de que el documento no sea legible, retorna un mensaje de error indicando que el documento no es legible."
        else:
            prompt = "Analiza esta imagen (DNI peruano) y extrae los Apellidos, Prenombres/Pre Nombres, Sexo, Fecha de Nacimiento y numero de documento (DNI). En el caso de que la imagen no sea legible, retorna un mensaje de error indicando que la imagen no es legible."
        
        # Configurar la generación de contenido
        generate_content_config = types.GenerateContentConfig(
            temperature=0.1,  # Baja temperatura para análisis más preciso
            top_p=0.95,
            max_output_tokens=8192,
            response_mime_type="text/plain",
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="OFF"
                )
            ],
        )
        
        logger.info(f"Invocando Vertex AI para análisis de archivo ({mime_type}) con modelo: {model_name}")
        
        # Invocar Vertex AI
        result = client.models.generate_content(
            model=model_name,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=image_file.read(), mime_type=mime_type),
                        types.Part.from_text(text=prompt)
                    ]
                )
            ],
            config=generate_content_config,
        )
        
        image_text = result.text
        logger.info(f"Análisis de archivo exitoso: {image_text}")
        logger.debug(f"Tokens utilizados - Total: {result.usage_metadata.total_token_count}, "
                    f"Prompt: {result.usage_metadata.prompt_token_count}, "
                    f"Respuesta: {result.usage_metadata.candidates_token_count}")
        
        return image_text
        
    except httpx.TimeoutException as e:
        logger.error(f"Timeout al descargar el archivo: {str(e)}", exc_info=True)
        return None
    except httpx.HTTPError as e:
        logger.error(f"Error HTTP al descargar el archivo: {str(e)} - Tipo: {type(e).__name__}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error al convertir imagen/PDF a texto: {str(e)} - Tipo: {type(e).__name__}", exc_info=True)
        return None

