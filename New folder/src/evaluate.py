import mlflow
import os

def evaluate_model():
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI"))
    with open("run_id.txt", "r") as f:
        run_id = f.read().strip()

    # Fetch run data (This queries the fast database, bypassing artifact latency)
    run = mlflow.get_run(run_id)
    accuracy = run.data.metrics.get("accuracy", 0.0)
    
    print(f"[EVALUATE] Retrieved Accuracy: {accuracy}")
    
    if accuracy < 0.80:
        raise Exception("Model accuracy is below 80%. Failing pipeline.")
    
    print("[EVALUATE] Model passed evaluation threshold.")

if __name__ == "__main__":
    evaluate_model()
