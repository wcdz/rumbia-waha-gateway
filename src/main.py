import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv
load_dotenv()
from src.routes.waha_router import router as waha_router

# Cargar variables de entorno del archivo .env

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="WAHA Gateway",
    description="API Gateway for processing WAHA messages",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(waha_router)

@app.get("/health")
async def health_check():
    """Health check endpoint para Cloud Run"""
    return {"status": "healthy", "service": "WAHA Gateway"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "WAHA Gateway API", "docs": "/docs"}

if __name__ == "__main__":
    # Cloud Run proporciona el puerto a través de la variable de entorno PORT
    port = int(os.environ.get("PORT", 8090))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=False)
