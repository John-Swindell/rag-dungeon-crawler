resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "gemini_api_key_value" {
  secret      = google_secret_manager_secret.gemini_api_key.id
  secret_data = "REPLACE_ME"

  lifecycle {
    ignore_changes = [secret_data]
  }
}

resource "google_secret_manager_secret_iam_member" "cloud_run_access" {
  secret_id = google_secret_manager_secret.gemini_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.current.number}-compute@developer.gserviceaccount.com"
}

data "google_project" "current" {}
