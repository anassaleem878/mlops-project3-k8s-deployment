# MLOps Project 3 — K8s Cluster Deployment

> **Automated ML pipeline** that trains an Iris classifier, registers it in MLflow, and deploys it as a load-balanced REST API on a local Kubernetes cluster — all provisioned and torn down with a single `terraform apply`.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture & Agent Workflow](#system-architecture--agent-workflow)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation Steps](#installation-steps)
- [Environment Variables](#environment-variables)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Acknowledgements & Data Sources](#acknowledgements--data-sources)
- [License](#license)

---

## Overview

This project implements a full **MLOps deployment pipeline** using Kubernetes. It covers every stage from raw data ingestion through model training, MLflow registration, Docker containerization, and live inference via a Kubernetes-managed Flask API — fronted by an Nginx Ingress controller acting as a load balancer.

Infrastructure is declared in **Terraform** (IaC), the cluster runs on **Minikube**, and the CI/CD pipeline runs through **Jenkins**. The trained model is exposed as a REST API with a minimum of 3 replicas behind Nginx, demonstrating self-healing, horizontal scaling, and zero-downtime pod replacement.

---

## Key Features

- **Single-command infrastructure** — `terraform apply` provisions Minikube, builds the Docker image, creates the K8s namespace, deployment, service, and ingress
- **Self-healing pods** — Kubernetes ReplicaSet automatically restarts failed pods to maintain 3 replicas
- **Horizontal scaling** — scale from 3 to 5 replicas (or any count) with one `kubectl scale` command
- **MLflow model registry** — model versioned and aliased as `Production` before deployment
- **Nginx load balancing** — Ingress controller distributes traffic across all running pods
- **Live health checks** — liveness and readiness probes prevent traffic from reaching unhealthy pods
- **Full CI/CD** — Jenkins pipeline covers data ingestion → training → evaluation → registration → deployment → verification

---

## System Architecture & Agent Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         WORKFLOW OVERVIEW                           │
└─────────────────────────────────────────────────────────────────────┘

  Developer
     │
     ▼
  GitHub Repo  ──►  Jenkins CI/CD Pipeline
                         │
          ┌──────────────┼──────────────────────┐
          │              │                      │
          ▼              ▼                      ▼
    Data Ingest    Model Training          Terraform Apply
    (iris.csv)     (RandomForest)               │
                         │                      │
                         ▼                      ▼
                   MLflow Tracking         Minikube Cluster
                   & Experiment                 │
                         │               ┌──────┴──────┐
                         ▼               │             │
                   MLflow Registry    Namespace      Docker
                   (Production        (mlops)        Image
                    alias)                │        (iris-api)
                         │               ▼
                         └──────►  K8s Deployment
                                    │
                              ┌─────┼─────┐
                              ▼     ▼     ▼
                            Pod1  Pod2  Pod3   ← ReplicaSet (min 3)
                              │     │     │
                              └─────┼─────┘
                                    │
                              NodePort Service
                                    │
                            Nginx Ingress Controller
                            (Load Balancer)
                                    │
                              ┌─────┴──────┐
                              ▼            ▼
                        curl / Postman   Browser
                        POST /predict   GET /health
```

### Pipeline Stage Breakdown

```
Jenkins Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stage 1  │ Checkout Repository
Stage 2  │ Install Dependencies
Stage 3  │ Data Ingestion          → data/iris.csv
Stage 4  │ Model Training          → MLflow run logged
Stage 5  │ Model Evaluation        → accuracy ≥ 0.85
Stage 6  │ Model Registration      → MLflow alias: Production
Stage 7  │ Terraform Init
Stage 8  │ Terraform Plan
Stage 9  │ Minikube Start + Docker Build
Stage 10 │ Terraform Apply         → K8s resources created
Stage 11 │ Verify K8s Deployment   → pods, services, ingress
Stage 12 │ Test API Endpoint       → /health + /predict
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Kubernetes Resource Layout

```
Namespace: mlops
├── Deployment: iris-mlops-app
│   └── ReplicaSet (replicas: 3)
│       ├── Pod 1  (iris-api container, port 7000)
│       ├── Pod 2  (iris-api container, port 7000)
│       └── Pod 3  (iris-api container, port 7000)
├── Service: iris-mlops-app-service  (NodePort 30007 → 7000)
└── Ingress: iris-mlops-app-ingress  (host: iris-api.local → Service:80)
```

### MLflow Model Lifecycle

```
Training Run
    │
    ▼
MLflow Tracking Server (localhost:5000)
    │
    ▼
Model Registered → iris-k8s-classifier
    │
    ▼
Alias assigned → Production
    │
    ▼
Flask API loads model @ startup
models:/iris-k8s-classifier@Production
```

---

## Tech Stack

| Layer | Tool | Version |
|---|---|---|
| Infrastructure (IaC) | Terraform | ≥ 1.0 |
| Kubernetes cluster | Minikube | ≥ 1.30 |
| Container runtime | Docker | ≥ 24.0 |
| CI/CD | Jenkins | ≥ 2.4 (WAR) |
| ML experiment tracking | MLflow | ≥ 2.9 |
| ML framework | scikit-learn | ≥ 1.3 |
| API server | Flask + Flask-CORS | ≥ 3.0 |
| Load balancer | Nginx Ingress | via Minikube addon |
| Language | Python | 3.11+ |
| Dataset | Iris (sklearn) | built-in |
| Model | Random Forest Classifier | 100 estimators |

---

## Prerequisites

Install and verify each before proceeding:

```bash
# Docker
sudo service docker start
docker --version          # ≥ 24.0

# Minikube
minikube version          # ≥ 1.30

# kubectl
kubectl version --client  # ≥ 1.28

# Terraform
terraform version         # ≥ 1.0

# Python
python3 --version         # ≥ 3.11

# Java (for Jenkins WAR)
java -version             # ≥ 17
```

---

## Installation Steps

### 1 — Clone the Repository

```bash
git clone https://github.com/SyedAunAliKazmi/mlops-project3-k8s-deployment.git
cd mlops-project3-k8s-deployment
```

### 2 — Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3 — Start Services

Open three separate terminals:

```bash
# Terminal 1 — Docker
sudo service docker start

# Terminal 2 — MLflow tracking server
mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns

# Terminal 3 — Jenkins
java -jar ~/jenkins.war --httpPort=8080
```

### 4 — Run ML Pipeline

```bash
python3 src/data_ingest.py
python3 src/train.py
python3 src/evaluate.py
python3 src/register_model.py
```

### 5 — Start Minikube

```bash
minikube start --driver=docker --memory=4096 --cpus=2
minikube addons enable ingress
minikube addons enable metrics-server
```

### 6 — Build Docker Image Inside Minikube

```bash
eval $(minikube docker-env)
docker build -t iris-api:latest .
```

### 7 — Deploy with Terraform

```bash
cd terraform
terraform init
terraform plan
terraform apply -auto-approve
cd ..
```

### 8 — Configure Nginx Ingress Host

```bash
MINIKUBE_IP=$(minikube ip)
echo "$MINIKUBE_IP iris-api.local" | sudo tee -a /etc/hosts
```

### 9 — Verify Deployment

```bash
kubectl get pods -n mlops
kubectl get replicaset -n mlops
kubectl get services -n mlops
kubectl get ingress -n mlops
```

Expected output:

```
NAME                                    READY   STATUS    RESTARTS   AGE
iris-mlops-app-xxxxxxxxx-xxxxx          1/1     Running   0          2m
iris-mlops-app-xxxxxxxxx-yyyyy          1/1     Running   0          2m
iris-mlops-app-xxxxxxxxx-zzzzz          1/1     Running   0          2m
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `MLFLOW_TRACKING_URI` | `http://localhost:5000` | MLflow server address (local) |
| `MLFLOW_TRACKING_URI` (in pod) | `http://host.minikube.internal:5000` | MLflow address from inside K8s pod |

Set inside `k8s/deployment.yaml` under `env:`. No `.env` file required for local runs.

---

## Usage

### Run the Full Jenkins Pipeline

- Open `http://localhost:8080`
- Create a Pipeline job pointing to this repo
- Set Script Path: `Jenkinsfile`
- Click **Build Now**

### Run ML Pipeline Manually

```bash
source venv/bin/activate
python3 src/data_ingest.py   # ingest Iris dataset → data/iris.csv
python3 src/train.py         # train + log to MLflow
python3 src/evaluate.py      # evaluate accuracy (threshold 0.85)
python3 src/register_model.py # register + assign Production alias
```

### Scale Replicas

```bash
# Scale up
kubectl scale deployment iris-mlops-app -n mlops --replicas=5

# Scale down
kubectl scale deployment iris-mlops-app -n mlops --replicas=3
```

### Demonstrate Self-Healing

```bash
# Delete one pod — ReplicaSet will recreate it automatically
kubectl delete pod \
  $(kubectl get pods -n mlops -o name | head -1 | cut -d/ -f2) \
  -n mlops

# Watch recovery
kubectl get pods -n mlops -w
```

### Tear Down Infrastructure

```bash
cd terraform
terraform destroy -auto-approve
```

---

## API Reference

Base URL (NodePort): `http://$(minikube service iris-mlops-app-service -n mlops --url)`  
Base URL (Ingress): `http://iris-api.local`

---

### `GET /`

Returns project and student metadata.

**Response:**
```json
{
  "project":  "MLOps Project 3 — K8s Cluster Deployment",
  "student":  "Syed Aun Ali Kazmi",
  "model":    "iris-k8s-classifier",
  "endpoint": "/predict",
  "status":   "running"
}
```

---

### `GET /health`

Returns API and model health status.

**Response:**
```json
{
  "status":       "healthy",
  "model_loaded": true
}
```

---

### `POST /predict`

Runs inference on 4 Iris features.

**Request Body:**
```json
{
  "features": [5.1, 3.5, 1.4, 0.2]
}
```

**Feature Order:**

| Index | Feature |
|---|---|
| 0 | sepal length (cm) |
| 1 | sepal width (cm) |
| 2 | petal length (cm) |
| 3 | petal width (cm) |

**Response:**
```json
{
  "prediction":  0,
  "class_name":  "Setosa",
  "probabilities": {
    "Setosa":     0.97,
    "Versicolor": 0.02,
    "Virginica":  0.01
  },
  "input": {
    "sepal_length": 5.1,
    "sepal_width":  3.5,
    "petal_length": 1.4,
    "petal_width":  0.2
  }
}
```

**Class Reference:**

| Class ID | Name |
|---|---|
| 0 | Setosa |
| 1 | Versicolor |
| 2 | Virginica |

**Error Responses:**

```json
// Missing features key
{ "error": "Missing 'features'", "format": {"features": [5.1, 3.5, 1.4, 0.2]} }

// Wrong number of features
{ "error": "Exactly 4 features required", "received": 2 }

// Model not loaded
{ "error": "Model not loaded" }
```

---

## Project Structure

```
mlops-project3-k8s-deployment/
│
├── terraform/
│   ├── providers.tf        # Kubernetes + null provider config
│   ├── variables.tf        # Input variables (replicas, ports, names)
│   └── main.tf             # All K8s resources + Minikube provisioning
│
├── src/
│   ├── data_ingest.py      # Load Iris dataset → data/iris.csv
│   ├── train.py            # Train RandomForest + log to MLflow
│   ├── evaluate.py         # Evaluate accuracy vs threshold
│   └── register_model.py   # Register model + assign Production alias
│
├── api/
│   └── app.py              # Flask REST API (/, /health, /predict)
│
├── k8s/
│   ├── namespace.yaml      # mlops namespace
│   ├── deployment.yaml     # ReplicaSet (3 pods)
│   ├── service.yaml        # NodePort service (port 30007)
│   └── ingress.yaml        # Nginx Ingress (iris-api.local)
│
├── Dockerfile              # Python 3.11-slim, port 7000
├── Jenkinsfile             # 12-stage CI/CD pipeline
├── requirements.txt        # Python dependencies
└── README.md
```

---

## Acknowledgements & Data Sources

| Item | Source |
|---|---|
| **Iris Dataset** | [UCI ML Repository](https://archive.ics.uci.edu/ml/datasets/iris) via `sklearn.datasets.load_iris` |
| **scikit-learn** | [scikit-learn.org](https://scikit-learn.org) — RandomForestClassifier |
| **MLflow** | [mlflow.org](https://mlflow.org) — experiment tracking and model registry |
| **Terraform K8s Provider** | [registry.terraform.io/hashicorp/kubernetes](https://registry.terraform.io/providers/hashicorp/kubernetes/latest) |
| **Minikube** | [minikube.sigs.k8s.io](https://minikube.sigs.k8s.io) — local Kubernetes cluster |
| **Nginx Ingress** | [kubernetes.github.io/ingress-nginx](https://kubernetes.github.io/ingress-nginx) |
| **Jenkins** | [jenkins.io](https://www.jenkins.io) — CI/CD automation server |
| **Course** | Machine Learning Operations — University of Lahore, Department of Intelligent Systems |

---

## License

This project is submitted as academic coursework for the Machine Learning Operations course at the University of Lahore. All ML pipeline code, Terraform configuration, Kubernetes manifests, and API implementation are original work by **Syed Aun Ali Kazmi**.

The Iris dataset is public domain. All third-party tools and libraries retain their respective licenses.

---

<div align="center">

**Syed Aun Ali Kazmi**  
BS Embedded Systems — University of Lahore  
Machine Learning Operations | 6th Semester

</div>
