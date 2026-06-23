"""
MLflow Model Prediction Script
Syed Aun Ali Kazmi | SAP: 70149156 | BSES-A | 6th Semester
MLflow Tracking URI: http://127.0.0.1:5000
MLflow Serving URI:  http://127.0.0.1:6000
"""

import requests
import json

MLFLOW_SERVING_URI = "http://127.0.0.1:6000/invocations"
CLASS_NAMES        = {0: "Setosa", 1: "Versicolor", 2: "Virginica"}

def predict(features: list) -> dict:
    response = requests.post(
        MLFLOW_SERVING_URI,
        headers={"Content-Type": "application/json"},
        data=json.dumps({"inputs": [features]})
    )
    prediction_id = response.json()["predictions"][0]
    return {
        "input": {
            "sepal_length": features[0],
            "sepal_width":  features[1],
            "petal_length": features[2],
            "petal_width":  features[3]
        },
        "prediction_id": prediction_id,
        "class_name":    CLASS_NAMES[prediction_id]
    }

if __name__ == "__main__":
    test_cases = [
        [5.1, 3.5, 1.4, 0.2],   # Setosa
        [6.0, 2.9, 4.5, 1.5],   # Versicolor
        [6.7, 3.1, 5.6, 2.4]    # Virginica
    ]
    print("\n=== MLflow Model Predictions ===")
    print(f"Tracking URI: http://127.0.0.1:5000")
    print(f"Serving URI:  {MLFLOW_SERVING_URI}\n")
    for features in test_cases:
        result = predict(features)
        print(f"Input:       {result['input']}")
        print(f"Prediction:  [{result['prediction_id']}] → {result['class_name']}")
        print("-" * 50)
