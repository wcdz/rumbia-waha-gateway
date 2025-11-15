from decouple import config

# Configuracion de la aplicacion
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
# ASSISTANT = config("ASSISTANT", default="84ae4421-0102-4ccc-9f17-5b9b12600324")
# ASSISTANT_NAME = config("ASSISTANT_NAME", default="Bot Test")
CHATBOT_API_URL = config("CHATBOT_API_URL", default="http://localhost:8090/v1/llm/question")
WAHA_API_URL = config("WAHA_API_URL", default="https://waha-197831323053.us-central1.run.app")
WAHA_API_KEY = config("WAHA_API_KEY", default="d74e39d8e82248e6bac96e853d095fc8")

# Configuracion de Google Cloud / Vertex AI
GOOGLE_APPLICATION_CREDENTIALS = config("GOOGLE_APPLICATION_CREDENTIALS", default="gcp-credentials.json")
GCP_PROJECT_ID = config("GCP_PROJECT_ID", default="is-geniaton-ifs-2025-g3")
GCP_LOCATION = config("GCP_LOCATION", default="us-central1")
VERTEX_AI_MODEL = config("VERTEX_AI_MODEL", default="gemini-2.0-flash-exp")