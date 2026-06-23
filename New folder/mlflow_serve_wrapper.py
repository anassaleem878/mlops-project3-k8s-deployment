"""
MLflow Model Wrapper API
Loads model directly from MLflow Registry - no mlflow serve needed
Syed Aun Ali Kazmi | SAP: 70149156 | BSES-A | 6th Semester
MLflow Tracking URI: http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify
import mlflow
import mlflow.sklearn
import numpy as np

app = Flask(__name__)

MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
MODEL_NAME          = "iris-k8s-classifier"
CLASS_NAMES         = {0: "Setosa", 1: "Versicolor", 2: "Virginica"}

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Load model directly from registry at startup
try:
    model = mlflow.sklearn.load_model(f"models:/{MODEL_NAME}@Production")
    print(f"[WRAPPER] Model loaded from MLflow Registry: {MODEL_NAME}@Production")
except Exception as e:
    print(f"[WRAPPER ERROR] Could not load model: {e}")
    model = None

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "project":           "MLOps Project 3 — K8s Cluster Deployment",
        "student":           "Syed Aun Ali Kazmi",
        "mlflow_tracking":   MLFLOW_TRACKING_URI,
        "model":             MODEL_NAME,
        "model_loaded":      model is not None,
        "predict_endpoint":  "/predict",
        "input_format":      {"features": [5.1, 3.5, 1.4, 0.2]}
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":       "healthy",
        "model_loaded": model is not None
    }), 200

@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    data     = request.get_json()
    features = data.get("features")
    if not features or len(features) != 4:
        return jsonify({
            "error":  "Provide exactly 4 features",
            "format": {"features": [5.1, 3.5, 1.4, 0.2]}
        }), 400
    arr            = np.array(features).reshape(1, -1)
    pred           = model.predict(arr)[0]
    proba          = model.predict_proba(arr)[0].tolist()
    return jsonify({
        "mlflow_tracking_uri": MLFLOW_TRACKING_URI,
        "model":               MODEL_NAME,
        "input": {
            "sepal_length": features[0],
            "sepal_width":  features[1],
            "petal_length": features[2],
            "petal_width":  features[3]
        },
        "prediction_id": int(pred),
        "class_name":    CLASS_NAMES[int(pred)],
        "probabilities": {
            "Setosa":     round(proba[0], 4),
            "Versicolor": round(proba[1], 4),
            "Virginica":  round(proba[2], 4)
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7500)
