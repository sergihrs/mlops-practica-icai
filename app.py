import joblib
import numpy as np
from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

PREDICTION_COUNTER = Counter(
    "iris_prediction_count",
    "Contador de predicciones del modelo Iris por especie",
    ["species"],
)

# Cargar el modelo entrenado
try:
    model = joblib.load("model.pkl")
except FileNotFoundError:
    print(
        "Error: 'model.pkl' no encontrado. Por favor, asegúrate de haber ejecutado el script de entrenamiento."
    )
    model = None
# Inicializar la aplicación Flask
app = Flask(__name__)


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return (
            jsonify(
                {"error": "Modelo no cargado. Por favor, entrene el modelo primero."}
            ),
            500,
        )
    try:
        # Obtener los datos de la petición en formato JSON
        data = request.get_json(force=True)
        features = np.array(data["features"]).reshape(1, -1)
        # Realizar la predicción
        prediction = model.predict(features)
        # Mapear el resultado numérico a una especie
        species_map = {0: "setosa", 1: "versicolor", 2: "virginica"}
        predicted_species = species_map.get(int(prediction[0]), "unknown")
        # Incrementa el contador para la especie predicha
        PREDICTION_COUNTER.labels(species=predicted_species).inc()
        # Devolver la predicción en formato JSON
        return jsonify({"prediction": int(prediction[0]), "species": predicted_species})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
