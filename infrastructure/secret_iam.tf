resource "google_secret_manager_secret_iam_member" "cloud_run_mongo_uri_access" {
  secret_id = var.mongo_uri_secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.cloud_run_service_account_email}"

  depends_on = [google_project_service.required]
}

resource "google_secret_manager_secret_iam_member" "cloud_run_gemini_api_key_access" {
  secret_id = var.gemini_api_key_secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.cloud_run_service_account_email}"

  depends_on = [google_project_service.required]
}
