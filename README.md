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

## Deploy en Render

1. Sube el proyecto a GitHub (sin los `.pkl`)
2. En [render.com](https://render.com) → New → Web Service → conecta el repo
3. Render detecta el `render.yaml` automáticamente
4. Agrega los modelos como **Secret Files** en Render:
   - `fog/models/model_b.pkl`
   - `fog/models/model_c.pkl`
   - `fog/models/scaler_b.pkl`
   - `fog/models/scaler_c.pkl`

## Integración con VIMOV

En `imus/fog/fog_predictor.py` de VIMOV reemplaza la lógica local por:

```python
import os, requests

FOG_API_URL = os.getenv("FOG_API_URL", "https://fog-api.onrender.com")

def predict_ensemble_remote(json_content: dict):
    try:
        r = requests.post(f"{FOG_API_URL}/predict", json=json_content, timeout=60)
        if r.status_code == 200:
            return r.json().get("ensemble")
        return None
    except Exception as e:
        logger.error("Error llamando FOG API: %s", e)
        return None
```

Y en `.env` de VIMOV agrega:
```
FOG_API_URL=https://fog-api.onrender.com
```
