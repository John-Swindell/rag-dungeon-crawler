variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service and Artifact Registry repository name"
  type        = string
  default     = "rag-narrative-engine"
}

variable "cloud_run_service_account_email" {
  description = "Existing service account used by Cloud Run"
  type        = string
  default     = ""
}

variable "custom_domain" {
  description = "Verified custom domain mapped to Cloud Run. Set to an empty string to skip domain mapping."
  type        = string
  default     = ""
}

variable "allowed_origins" {
  description = "Browser origins allowed to call the FastAPI service"
  type        = list(string)
  default = [
    "https://game.jswindell.dev",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
    "null",
  ]
}

variable "max_instance_count" {
  description = "Maximum Cloud Run instances"
  type        = number
  default     = 2
}

variable "cpu_limit" {
  description = "Cloud Run CPU limit"
  type        = string
  default     = "1"
}

variable "memory_limit" {
  description = "Cloud Run memory limit"
  type        = string
  default     = "512Mi"
}

variable "mongo_db" {
  description = "MongoDB database name"
  type        = string
  default     = "dungeon_crawler"
}

variable "mongo_uri_secret_id" {
  description = "Existing Secret Manager secret ID containing the MongoDB Atlas URI"
  type        = string
  default     = ""
}

variable "gemini_api_key_secret_id" {
  description = "Existing Secret Manager secret ID containing the Gemini API key"
  type        = string
  default     = ""
}

variable "mongo_vector_index" {
  description = "MongoDB Atlas Vector Search index name on the context collection"
  type        = string
  default     = "game_context_vector_index"
}

variable "vertex_location" {
  description = "Vertex AI location. Gemini 3 Flash preview uses global endpoints."
  type        = string
  default     = "global"
}

variable "gemini_model" {
  description = "Gemini model used for narrative context"
  type        = string
  default     = "gemini-2.5-flash"
}

variable "embedding_model" {
  description = "Vertex AI embedding model used for MongoDB Atlas vector search"
  type        = string
  default     = "gemini-embedding-001"
}

variable "embedding_dimensions" {
  description = "Embedding vector dimensions. Match this in the MongoDB Atlas vector index."
  type        = number
  default     = 768
}
