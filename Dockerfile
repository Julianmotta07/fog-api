# FOG Prediction API — imagen para desplegar dentro de la infraestructura I2T,
# junto a VIMOV (NO en un servicio externo tipo Render).
#
# El código fuente y los modelos (fog/models/*.pkl) se empaquetan en la imagen,
# por lo que NO se requiere subir "secret files" como en Render.
FROM python:3.11.0-slim

# libgomp1: requerido en runtime por xgboost / scikit-learn (OpenMP)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias primero para aprovechar la cache de capas de Docker.
# Se usa una cache de pip de BuildKit: si un build se interrumpe (p. ej. red lenta),
# el reintento reutiliza los wheels ya descargados en vez de bajarlos de nuevo.
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copiar el código fuente (incluye fog/models/*.pkl, ya versionados en el repo)
COPY . .

EXPOSE 5001

# Healthcheck contra el endpoint /health que expone app.py
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:5001/health').status==200 else 1)"

# Mismo comando que usaba render.yaml
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5001", "--workers", "1", "--timeout", "120"]
