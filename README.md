# FOG Prediction API

Microservicio de inferencia FOG — modelo compuesto (wB=0.35, wC=0.65, umbral=0.30).

## Endpoints

### `GET /health`
Verifica que el servicio está activo.
```json
{"status": "ok", "model": "ensemble", "weights": {"B": 0.35, "C": 0.65}, "threshold": 0.30}
```

### `POST /predict`
Recibe un JSON DGI completo y retorna las predicciones por ventana.

**Request body:** JSON DGI con `dgiResults` que contenga el subtest "Marcha normal" con sensores `LEFT-ANKLE`, `BASE-SPINE` y `LEFT-HAND`.

**Response:**
```json
{
  "ensemble": [
    {"timestamp": 105952, "fog": 0, "prob": 0.12},
    {"timestamp": 106952, "fog": 1, "prob": 0.45},
    ...
  ]
}
```

## Setup local

```bash
pip install -r requirements.txt
python app.py
```

## Despliegue (Docker / I2T)

El servicio corre **dentro de la infraestructura de I2T**, no en un proveedor externo.
Se empaqueta con Docker (`Dockerfile` + `docker-compose.yml`) y los modelos `.pkl`
van incluidos en la imagen. Ver **[`DEPLOY.md`](DEPLOY.md)** para los detalles.

```bash
docker compose up -d --build   # queda accesible en http://localhost:5001/health
```

## Integración con VIMOV

VIMOV alcanza este servicio por la **red interna de Docker** (no por una URL pública).
En el `.env` de VIMOV:

```
FOG_API_URL=http://fog-api:5001
```

La predicción se calcula **al ingerir** el estudio DGI y se persiste en la base de datos
de VIMOV (`imus.results.vars.fog`); el frontend la lee desde ahí.

## Uso de Inteligencia Artificial Generativa

Durante el desarrollo de este microservicio se utilizaron herramientas de inteligencia
artificial generativa (Anthropic, s.f.) como apoyo al desarrollo de software.

Estas herramientas se emplearon para:

- Diseñar la estructura inicial de la API de inferencia (endpoints, formato de
  request/response).
- Generar propuestas preliminares de implementación del pipeline de extracción de
  señales, construcción de características y predicción del modelo compuesto.
- Apoyar la generación de fragmentos iniciales de código relacionados con el
  procesamiento de solicitudes HTTP y la configuración del despliegue (Docker).

Todas las sugerencias y artefactos generados fueron revisados, adaptados, probados y
validados por el autor antes de su incorporación al proyecto, garantizando su
funcionamiento y adecuación a los requerimientos específicos de la solución desarrollada.

**Referencias**

- Anthropic. (s.f.). *Claude*. https://www.anthropic.com
