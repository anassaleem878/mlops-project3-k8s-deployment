import mlflow
from mlflow.tracking import MlflowClient
import os

def register():
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI"))
    client = MlflowClient()
    model_name = "iris-k8s-classifier"
    
    # Get the version we just trained
    versions = client.get_latest_versions(model_name, stages=["None"])
    latest_version = versions[0].version
    
    # Promote to Production
    client.transition_model_version_stage(
        name=model_name,
        version=latest_version,
        stage="Production",
        archive_existing_versions=True
    )
    print(f"[REGISTER] Version {latest_version} successfully transitioned to Production.")

if __name__ == "__main__":
    register()
