# 🚀 Guía de Despliegue en Google Cloud Run

## ✅ Pre-requisitos

1. **Google Cloud SDK** instalado
2. Autenticado con tu cuenta de Google Cloud
3. Proyecto GCP: `is-geniaton-ifs-2025-g3`

## 🔐 Autenticación

Si aún no estás autenticado, ejecuta:

```bash
gcloud auth login
gcloud config set project is-geniaton-ifs-2025-g3
```

## 📦 Despliegue Automático

### Opción 1: PowerShell (Windows)

```powershell
.\deploy.ps1
```

### Opción 2: Comandos manuales

```bash
# 1. Configurar proyecto
gcloud config set project is-geniaton-ifs-2025-g3

# 2. Habilitar APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com aiplatform.googleapis.com

# 3. Construir imagen
gcloud builds submit --tag gcr.io/is-geniaton-ifs-2025-g3/waha-gateway

# 4. Desplegar
gcloud run deploy waha-gateway \
  --image gcr.io/is-geniaton-ifs-2025-g3/waha-gateway \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "GCP_PROJECT_ID=is-geniaton-ifs-2025-g3,GCP_LOCATION=us-central1,VERTEX_AI_MODEL=gemini-2.0-flash-exp"
```

## 🔧 Configurar Variables de Entorno

Después del despliegue, configura las URLs necesarias:

```bash
gcloud run services update waha-gateway \
  --region us-central1 \
  --set-env-vars CHATBOT_API_URL=<tu-chatbot-url>,WAHA_API_URL=<tu-waha-url>,WAHA_API_KEY=<tu-waha-api-key>
```

## 📊 Verificar el Despliegue

```bash
# Obtener URL del servicio
gcloud run services describe waha-gateway --region us-central1 --format 'value(status.url)'

# Probar health check
curl https://tu-url.run.app/health

# Ver logs
gcloud run services logs read waha-gateway --region us-central1
```

## 🔍 Monitoreo y Logs

- **Logs en tiempo real:**
  ```bash
  gcloud run services logs tail waha-gateway --region us-central1
  ```

- **Console de GCP:**
  - Logs: https://console.cloud.google.com/run/detail/us-central1/waha-gateway/logs
  - Métricas: https://console.cloud.google.com/run/detail/us-central1/waha-gateway/metrics

## 🔄 Actualizar el Servicio

Si haces cambios en el código:

```bash
# Reconstruir y redesplegar
gcloud builds submit --tag gcr.io/is-geniaton-ifs-2025-g3/waha-gateway
gcloud run deploy waha-gateway --image gcr.io/is-geniaton-ifs-2025-g3/waha-gateway --region us-central1
```

## 🛠️ Comandos Útiles

```bash
# Ver todas las revisiones
gcloud run revisions list --service waha-gateway --region us-central1

# Rollback a una revisión anterior
gcloud run services update-traffic waha-gateway --to-revisions=REVISION_NAME=100 --region us-central1

# Eliminar el servicio
gcloud run services delete waha-gateway --region us-central1

# Ver la configuración actual
gcloud run services describe waha-gateway --region us-central1
```

## 🔐 Permisos Necesarios

El servicio necesita acceso a:
- ✅ Vertex AI API (ya configurado automáticamente en Cloud Run)
- ✅ Cloud Storage (si usas archivos)

La cuenta de servicio de Cloud Run tiene permisos automáticos para Vertex AI en el mismo proyecto.

## ❓ Troubleshooting

### Error: "Permission denied"
```bash
# Dar permisos a la cuenta de servicio
gcloud projects add-iam-policy-binding is-geniaton-ifs-2025-g3 \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### Ver número del proyecto
```bash
gcloud projects describe is-geniaton-ifs-2025-g3 --format='value(projectNumber)'
```

## 📝 Notas Importantes

1. **NO necesitas `gcp-credentials.json` en Cloud Run** - El servicio usa Application Default Credentials
2. El archivo `.dockerignore` excluye `gcp-credentials.json` del contenedor por seguridad
3. Las variables de entorno se configuran directamente en Cloud Run
4. El servicio escala automáticamente de 0 a 10 instancias según la demanda

