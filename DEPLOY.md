# Despliegue de la FOG Prediction API en la infraestructura I2T

Este servicio corre **dentro** de la misma infraestructura que VIMOV, de modo que
**los datos de pacientes nunca salen del entorno I2T**: VIMOV llama a la API por la
red interna de Docker.

## Qué incluye

- `Dockerfile` — empaqueta el código fuente y los modelos (`fog/models/*.pkl`,
  ya versionados en el repo, ~1.2 MB), así que viajan dentro de la imagen.
- `docker-compose.yml` — levanta el servicio `fog-api` (gunicorn en el puerto `5001`).
- `.dockerignore` — excluye artefactos innecesarios de la imagen.

## Endpoints

- `GET  /health`  → estado del modelo.
- `POST /predict` → recibe el JSON DGI y devuelve `{"ensemble": [...]}`.

## Opción A — Servicio dentro del compose de la plataforma (recomendada)

En el `docker-compose.yml` de VIMOV ya se agregó un servicio `fog-api` cuyo
`build` apunta a este repo como directorio hermano (`../fog-api`). Basta con
clonar ambos repos lado a lado en el servidor:

```
/ruta/i2t/
├── vimov/        # repo de la plataforma
└── fog-api/      # este repo
```

y levantar todo con el compose de VIMOV:

```bash
cd vimov
docker compose up -d --build
```

Al estar en el mismo compose comparten la red por defecto, y VIMOV resuelve el
host `fog-api`. La variable en el `.env` de VIMOV queda:

```
FOG_API_URL=http://fog-api:5001
```

## Opción B — Despliegue independiente con red compartida

Si se prefiere desplegar este servicio por separado:

```bash
# 1) Crear una red compartida (una sola vez)
docker network create vimov-net

# 2) En el docker-compose.yml de este repo, descomentar los bloques "networks"
#    (tanto en el servicio como al final del archivo).

# 3) En el docker-compose de VIMOV, conectar su servicio a la misma red externa
#    vimov-net.

docker compose up -d --build
```

Con ambos en `vimov-net`, VIMOV alcanza el servicio en `http://fog-api:5001`.

## Modelos

Los cuatro archivos `fog/models/*.pkl` se copian dentro de la imagen al construir.
Si por política se prefiere mantenerlos fuera de la imagen, se pueden montar como
volumen en runtime y excluirlos del `COPY` — pero dado su tamaño y que ya están
versionados, empaquetarlos es lo más simple.

## Prueba rápida

```bash
curl http://localhost:5001/health
# {"status":"ok","model":"ensemble","weights":{"B":0.35,"C":0.65},"threshold":0.30}
```
