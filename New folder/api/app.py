from flask import Flask, request, jsonify
import mlflow.pyfunc
import os
import time

app = Flask(__name__)

# Iris Species Mapping Logic (Instructor Requirement for "Human Readable" Output)
SPECIES_MAP = {0: "setosa", 1: "versicolor", 2: "virginica"}

# Logic: Pull from DagsHub Cloud for WSL-off persistence
MODEL_NAME = "iris-k8s-classifier"
STAGE = "Production"
TRACKING_URI = "https://dagshub.com/anassaleem878/mlops-project3.mlflow"

mlflow.set_tracking_uri(TRACKING_URI)
model = None

def load_model():
    global model
    model_uri = f"models:/{MODEL_NAME}/{STAGE}"
    print(f"[INIT] Attempting to load model from: {model_uri}")
    for i in range(5):
        try:
            model = mlflow.pyfunc.load_model(model_uri)
            print("[INIT] Model loaded successfully!")
            return True
        except Exception as e:
            print(f"[INIT] Load attempt {i+1} failed. Retrying in 10s... Error: {e}")
            time.sleep(10)
    return False

# Initial load on startup
load_model()

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        if not load_model():
            return jsonify({"error": "Model not deployed. Check DagsHub Production stage."}), 503
    
    try:
        data = request.get_json()
        # Predict returns an array, we get the first element and convert to int
        prediction_int = int(model.predict([data['features']])[0])
        
        # Map integer to the actual flower name
        species_name = SPECIES_MAP.get(prediction_int, "unknown")
        
        return jsonify({
            "prediction_index": prediction_int,
            "species": species_name
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# THE FIX: Corrected 'methods' spelling.
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "model_loaded": model is not None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)
