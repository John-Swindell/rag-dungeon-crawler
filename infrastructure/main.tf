terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

data "google_project" "current" {}

resource "google_project_service" "required" {
  for_each = toset([
    "artifactregistry.googleapis.com",
    "generativelanguage.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com",
  ])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "game_engine" {
  location      = var.region
  repository_id = var.service_name
  format        = "DOCKER"

  depends_on = [google_project_service.required]
}

resource "google_cloud_run_v2_service" "game_engine" {
  name     = var.service_name
  location = var.region

  template {
    service_account = var.cloud_run_service_account_email

    scaling {
      min_instance_count = 0
      max_instance_count = var.max_instance_count
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.game_engine.repository_id}/${var.service_name}:latest"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = var.cpu_limit
          memory = var.memory_limit
        }
        cpu_idle          = true
        startup_cpu_boost = false
      }

      env {
        name  = "APP_ENV"
        value = "production"
      }

      env {
        name  = "ALLOWED_ORIGINS"
        value = jsonencode(var.allowed_origins)
      }

      env {
        name  = "MONGO_DB"
        value = var.mongo_db
      }

      env {
        name = "MONGO_URI"
        value_source {
          secret_key_ref {
            secret  = var.mongo_uri_secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = var.gemini_api_key_secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "ENABLE_LLM_CONTEXT"
        value = "true"
      }

      env {
        name  = "ENABLE_VECTOR_SEARCH"
        value = "true"
      }

      env {
        name  = "MONGO_VECTOR_INDEX"
        value = var.mongo_vector_index
      }

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.vertex_location
      }

      env {
        name  = "GEMINI_MODEL"
        value = var.gemini_model
      }

      env {
        name  = "EMBEDDING_MODEL"
        value = var.embedding_model
      }

      env {
        name  = "EMBEDDING_DIMENSIONS"
        value = tostring(var.embedding_dimensions)
      }
    }
  }

  depends_on = [
    google_artifact_registry_repository.game_engine,
    google_secret_manager_secret_iam_member.cloud_run_gemini_api_key_access,
    google_secret_manager_secret_iam_member.cloud_run_mongo_uri_access,
  ]
}

resource "google_cloud_run_v2_service_iam_member" "public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.game_engine.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_domain_mapping" "game_domain" {
  count    = var.custom_domain == "" ? 0 : 1
  name     = var.custom_domain
  location = google_cloud_run_v2_service.game_engine.location

  metadata {
    namespace = data.google_project.current.project_id
  }

  spec {
    route_name = google_cloud_run_v2_service.game_engine.name
  }
}
