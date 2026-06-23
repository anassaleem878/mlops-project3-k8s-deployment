pipeline {
    agent any
    environment {
        MLFLOW_TRACKING_URI      = "https://dagshub.com/anassaleem878/mlops-project3.mlflow"
        MLFLOW_TRACKING_USERNAME = "anassaleem878"
        MLFLOW_TRACKING_PASSWORD = "c6931f0db93def701315ed01e51aa16fb2f4f66d"
        KUBECONFIG               = "/var/lib/jenkins/.kube/config"
    }
    stages {
        stage('Checkout') {
            steps { git branch: 'main', url: 'https://github.com/anassaleem878/mlops-project3-k8s-deployment.git' }
        }
        stage('Train Model') {
            steps { sh 'python3 src/train.py' }
        }
        stage('Evaluate Model') {
            steps { sh 'python3 src/evaluate.py' }
        }
        stage('Register to Production') {
            steps { sh 'python3 src/register_model.py' }
        }
        stage('Deploy to Kubernetes') {
            steps {
                // Tells the ReplicaSet to restart, forcing it to download the fresh Production model
                sh 'kubectl rollout restart deployment iris-mlops-app -n mlops'
                sh 'kubectl rollout status deployment iris-mlops-app -n mlops'
            }
        }
    }
}
