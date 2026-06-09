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

## Integración en VIMOV (como submódulo — recomendada)

Igual que `taping-toe`, este servicio se engancha a VIMOV como **submódulo de git**.
Una vez el repo esté en la organización (`i2tResearch/fog-api`), desde la raíz de VIMOV:

```bash
# 1) Agregar el submódulo bajo services/ (misma convención que taping-toe)
git submodule add git@github.com:i2tResearch/fog-api.git services/fog-api

# 2) En el docker-compose.yml de VIMOV, cambiar el build del servicio fog-api:
#    -  build: ../fog-api
#    +  build: ./services/fog-api

git add .gitmodules services/fog-api docker-compose.yml
git commit -m "chore: add fog-api as submodule under services/"
```

Para inicializar el submódulo al clonar VIMOV (o en el servidor):

```bash
git submodule sync --recursive
git submodule update --init --recursive
```

> El runtime de VIMOV ya está listo y **no cambia** con el submódulo: el servicio se
> llama `fog-api` y se alcanza por la red interna con `FOG_API_URL=http://fog-api:5001`.

### Estado actual de la rama de VIMOV

Mientras el repo no esté en la organización, la rama de VIMOV referencia este servicio
como **directorio hermano** (`build: ../fog-api`), clonando ambos repos lado a lado:

```
/ruta/i2t/
├── vimov/
└── fog-api/      # este repo
```

Al moverlo a la organización, solo se aplica el cambio a submódulo descrito arriba
(`build: ../fog-api` → `build: ./services/fog-api`).

## Alternativa — despliegue independiente con red compartida

Si se prefiere desplegar este servicio por separado del compose de VIMOV:

```bash
# 1) Crear una red compartida (una sola vez)
docker network create vimov-net
# 2) Descomentar los bloques "networks" del docker-compose.yml de este repo.
# 3) Conectar el servicio de VIMOV a esa misma red externa vimov-net.
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
