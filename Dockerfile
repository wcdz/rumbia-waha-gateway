FROM python:3.10-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME

COPY . .

# Actualiza pip y setuptools
RUN pip install -U pip
RUN pip install -U setuptools

# Instala las dependencias desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Cloud Run proporciona el puerto dinámicamente a través de $PORT
EXPOSE 8080

# CMD que ejecuta uvicorn directamente, escuchando en el puerto proporcionado por Cloud Run
CMD exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8080}