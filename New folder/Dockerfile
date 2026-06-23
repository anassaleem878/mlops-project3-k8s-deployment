FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for pyarrow/mlflow
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# FIX: Increased timeout to prevent the ReadTimeoutError you faced
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

COPY api/app.py .

EXPOSE 7000

# Healthcheck ensures K8s knows if the model loading failed
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
  CMD curl -f http://localhost:7000/health || exit 1

CMD ["python", "app.py"]
