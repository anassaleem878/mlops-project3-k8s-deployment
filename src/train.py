import mlflow
import mlflow.sklearn
import os
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_model():
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI"))
    mlflow.set_experiment("iris-k8s-project3")
    
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.2)

    with mlflow.start_run() as run:
        model = RandomForestClassifier(n_estimators=100)
        model.fit(X_train, y_train)
        
        # Calculate and log the metric instantly to the database
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        mlflow.log_metric("accuracy", acc)
        
        # Log the heavy artifact in the background
        mlflow.sklearn.log_model(model, "model", registered_model_name="iris-k8s-classifier")
        
        with open("run_id.txt", "w") as f:
            f.write(run.info.run_id)
        print(f"[TRAIN] Run ID: {run.info.run_id} | Accuracy: {acc}")

if __name__ == "__main__":
    train_model()
