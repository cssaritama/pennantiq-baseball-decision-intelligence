provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  labels = {
    application = "pennantiq"
    environment = var.environment
    managed_by  = "terraform"
  }
}

resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "aiplatform.googleapis.com",
    "secretmanager.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com"
  ])
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_storage_bucket" "landing" {
  name                        = "${var.project_id}-${var.service_name}-landing"
  location                    = upper(var.region == "us-central1" ? "US" : var.region)
  uniform_bucket_level_access = true
  force_destroy               = false
  labels                      = local.labels
  depends_on                  = [google_project_service.services]
}

resource "google_bigquery_dataset" "core" {
  dataset_id                 = "pennantiq"
  friendly_name              = "PennantIQ governed data products"
  location                   = "US"
  delete_contents_on_destroy = false
  labels                     = local.labels
  depends_on                 = [google_project_service.services]
}

resource "google_service_account" "runtime" {
  account_id   = "pennantiq-runtime"
  display_name = "PennantIQ Cloud Run runtime"
}

resource "google_project_iam_member" "runtime_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_bigquery_dataset_iam_member" "runtime_data_viewer" {
  dataset_id = google_bigquery_dataset.core.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_secret_manager_secret" "llm_key" {
  secret_id = "pennantiq-llm-api-key"
  replication { auto {} }
  labels = local.labels
  depends_on = [google_project_service.services]
}

# Cloud Run is intentionally not created until an immutable container image is
# supplied. See README.md for the deployment command and production controls.
