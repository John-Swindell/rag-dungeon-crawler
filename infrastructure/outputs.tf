output "service_url" {
  description = "URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.game_engine.uri
}

output "artifact_registry" {
  description = "Docker image registry path"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.game_engine.repository_id}"
}

output "custom_domain" {
  description = "Configured custom domain, if domain mapping is enabled"
  value       = var.custom_domain
}

output "domain_records" {
  description = "DNS records produced by Cloud Run domain mapping"
  value       = try(google_cloud_run_domain_mapping.game_domain[0].status[0].resource_records, [])
}

output "mongo_uri_secret" {
  description = "Secret Manager secret containing the MongoDB Atlas URI"
  value       = var.mongo_uri_secret_id
}

output "gemini_api_key_secret" {
  description = "Secret Manager secret containing the Gemini API key"
  value       = var.gemini_api_key_secret_id
}
