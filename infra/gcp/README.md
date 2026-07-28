# PennantIQ GCP infrastructure blueprint

This Terraform module provisions only the safe platform foundation:

- required APIs;
- a private Cloud Storage landing bucket;
- a BigQuery dataset;
- a least-privilege runtime service account;
- a Secret Manager placeholder.

It intentionally does **not** deploy a public Cloud Run service or create a secret value. Build and test an immutable image first, then deploy with authenticated access.

```bash
gcloud auth application-default login
terraform init
terraform plan -var="project_id=YOUR_PROJECT"
terraform apply -var="project_id=YOUR_PROJECT"
```

Before production, add organization policies, VPC Service Controls, CMEK where required, private connectivity, data retention, backup, access reviews and cost budgets.
