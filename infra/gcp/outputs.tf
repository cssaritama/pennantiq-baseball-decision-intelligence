output "landing_bucket" { value = google_storage_bucket.landing.name }
output "bigquery_dataset" { value = google_bigquery_dataset.core.dataset_id }
output "runtime_service_account" { value = google_service_account.runtime.email }
