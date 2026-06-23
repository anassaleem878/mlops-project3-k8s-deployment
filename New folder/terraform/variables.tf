variable "app_name" { 
  default = "iris-mlops-app" 
}
variable "namespace" { 
  default = "mlops" 
}
variable "replica_count" { 
  description = "Requirement 7.1: Minimum 3-5 replicas"
  default = 3 
}
variable "app_port" { 
  default = 7000 
}
variable "image_name" { 
  description = "MUST match your logged-in Docker Hub username"
  default = "aun12/iris-api:latest" 
}
variable "mlflow_uri" { 
  description = "Cloud persistence for WSL-off capability"
  default = "https://dagshub.com/anassaleem878/mlops-project3.mlflow" 
}
variable "mlflow_username" { 
  default = "anassaleem878" 
}
variable "mlflow_password" { 
  default = "c80eaea30585653770fe829c28e2382a6cb81651" 
}
variable "student_name" { 
  default = "Syed-Aun-Ali-Kazmi" 
}
variable "sap_id" { 
  default = "SAP-70149156" 
}
