# Script de PowerShell para desplegar el WAHA Gateway en Google Cloud Run
# Proyecto: is-geniaton-ifs-2025-g3

$ErrorActionPreference = "Stop"

Write-Host "🚀 Desplegando WAHA Gateway en Cloud Run..." -ForegroundColor Blue

# Variables de configuración
$PROJECT_ID = "is-geniaton-ifs-2025-g3"
$SERVICE_NAME = "waha-gateway"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

Write-Host ""
Write-Host "📋 Configuración:" -ForegroundColor Cyan
Write-Host "  - Proyecto: $PROJECT_ID"
Write-Host "  - Servicio: $SERVICE_NAME"
Write-Host "  - Región: $REGION"
Write-Host "  - Imagen: $IMAGE_NAME"
Write-Host ""

# 1. Configurar proyecto
Write-Host "🔧 Configurando proyecto de GCP..." -ForegroundColor Cyan
gcloud config set project $PROJECT_ID

# 2. Habilitar APIs necesarias
Write-Host "🔌 Habilitando APIs necesarias..." -ForegroundColor Cyan
Write-Host "  - Cloud Build API"
gcloud services enable cloudbuild.googleapis.com
Write-Host "  - Cloud Run API"
gcloud services enable run.googleapis.com
Write-Host "  - Container Registry API"
gcloud services enable containerregistry.googleapis.com
Write-Host "  - Vertex AI API"
gcloud services enable aiplatform.googleapis.com

# 3. Construir la imagen con Cloud Build
Write-Host ""
Write-Host "🏗️  Construyendo imagen Docker con Cloud Build..." -ForegroundColor Cyan
Write-Host "    (Esto puede tomar unos minutos...)" -ForegroundColor Yellow
gcloud builds submit --tag $IMAGE_NAME

# 4. Desplegar en Cloud Run
Write-Host ""
Write-Host "🚀 Desplegando en Cloud Run..." -ForegroundColor Cyan
gcloud run deploy $SERVICE_NAME `
  --image $IMAGE_NAME `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --port 8080 `
  --memory 512Mi `
  --cpu 1 `
  --timeout 300 `
  --max-instances 10 `
  --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID,GCP_LOCATION=$REGION,VERTEX_AI_MODEL=gemini-2.0-flash-exp"

# 5. Obtener URL del servicio
Write-Host ""
Write-Host "✅ Despliegue completado!" -ForegroundColor Green
Write-Host ""

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
Write-Host "🌐 URL del servicio: $SERVICE_URL" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Próximos pasos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Configura las variables de entorno necesarias:" -ForegroundColor White
Write-Host "   - CHATBOT_API_URL: URL de tu servicio de chatbot"
Write-Host "   - WAHA_API_URL: URL de tu instancia WAHA"
Write-Host ""
Write-Host "2. Para actualizar variables de entorno ejecuta:" -ForegroundColor White
Write-Host "   gcloud run services update $SERVICE_NAME ``" -ForegroundColor Gray
Write-Host "     --region $REGION ``" -ForegroundColor Gray
Write-Host "     --set-env-vars CHATBOT_API_URL=<url>,WAHA_API_URL=<url>" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Accede a la documentación de la API en:" -ForegroundColor White
Write-Host "   $SERVICE_URL/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Verifica el health check:" -ForegroundColor White
Write-Host "   $SERVICE_URL/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎉 ¡Listo para usar!" -ForegroundColor Green

