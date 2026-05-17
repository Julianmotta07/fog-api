"""
app.py — FOG Prediction API
Expone POST /predict para inferencia del modelo compuesto FOG.
"""

import logging
import os
import sys

from flask import Flask, jsonify, request
from flask_cors import CORS

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fog import fog_extractor, fog_feature_builder
from fog.fog_predictor import get_predictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'model': 'ensemble', 'weights': {'B': 0.35, 'C': 0.65}, 'threshold': 0.30})


@app.route('/predict', methods=['POST'])
def predict():
    """
    Recibe un JSON DGI completo y retorna las predicciones del modelo compuesto.

    Request body: JSON DGI con estructura:
        {
            "dgiResults": [
                {
                    "subtest": "Marcha normal",
                    "imuData": [
                        {"deviceId": "LEFT-ANKLE", "timestamp": ...,
                         "accelerometer": {"x":..,"y":..,"z":..},
                         "gyroscope": {"x":..,"y":..,"z":..}},
                        ...
                    ]
                },
                ...
            ]
        }

    Response:
        200: {"ensemble": [{"timestamp": ms, "fog": 0|1, "prob": float}, ...]}
        400: {"error": "..."}  — faltan sensores o formato incorrecto
        500: {"error": "..."}  — error interno
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Body JSON requerido'}), 400

    if not data.get('dgiResults'):
        return jsonify({'error': 'El JSON no contiene dgiResults'}), 400

    try:
        predictor = get_predictor()

        signals_b = fog_extractor.extract_for_model_b(data)
        signals_c = fog_extractor.extract_for_model_c(data)

        if signals_b is None:
            return jsonify({'error': 'Sensores insuficientes para modelo B (necesita LEFT-ANKLE + BASE-SPINE)'}), 400
        if signals_c is None:
            return jsonify({'error': 'Sensores insuficientes para modelo C (necesita LEFT-ANKLE + LEFT-HAND)'}), 400

        features_b = fog_feature_builder.build_features_model_b(signals_b)
        features_c = fog_feature_builder.build_features_model_c(signals_c)

        ensemble = predictor.predict_ensemble(features_b, features_c)
        if ensemble is None:
            return jsonify({'error': 'Error en la inferencia del modelo'}), 500

        logger.info("Predicción completada: %d ventanas, %d FOG",
                    len(ensemble), sum(1 for x in ensemble if x['fog'] == 1))

        return jsonify({'ensemble': ensemble})

    except Exception as e:
        logger.exception("Error en /predict")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
