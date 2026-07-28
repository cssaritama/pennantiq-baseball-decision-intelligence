# GCP Production Architecture

![GCP architecture](../assets/gcp-architecture.svg)

## Why GCP

The product target is aligned with a data-intensive sports workflow:

- BigQuery for governed structured data and large analytical scans;
- Dataform for transformations and quality assertions;
- Cloud Storage for raw licensed assets;
- Cloud Run Jobs or Dataflow for ingestion;
- Vertex AI for models, embeddings and governed agent workloads;
- Cloud Run for portable application/API containers;
- Secret Manager, IAM and VPC Service Controls for protection;
- Cloud Logging and Monitoring for operational evidence;
- Looker for executive and staff dashboards.

Google Cloud publicly describes MLB Statcast and team analytics workloads using Google Cloud, BigQuery and Vertex AI. This establishes ecosystem alignment, not access to MLB private data or an endorsement of PennantIQ.

## Environments

### Local / Open

- CSV;
- optional DuckDB/dlt;
- SQLite monitoring and decision memory;
- Streamlit;
- deterministic analytics;
- optional LLM provider.

### Development GCP

- separate project;
- synthetic and permitted public data only;
- authenticated Cloud Run;
- budget alerts;
- BigQuery sandbox-size tables;
- no private team data.

### Team production

- organization-owned project or dedicated tenant;
- private landing and data products;
- least privilege and access reviews;
- encryption, retention and residency requirements;
- private connectors;
- model registry and approval;
- audit-ready decision memory.

## Data products

Suggested BigQuery datasets:

- `raw`: immutable source-aligned records;
- `core`: normalized games, plays, pitches, players, parks;
- `features`: versioned analytical features;
- `knowledge`: document chunks and embeddings;
- `decisions`: plans, approvals, outcomes and lessons;
- `monitoring`: quality, latency, cost and model events.

## Deployment

The included Terraform module provisions a minimal foundation only. It does not deploy an unauthenticated application or create a secret value.

```bash
pip install -r requirements-gcp.txt
gcloud auth application-default login
terraform -chdir=infra/gcp init
terraform -chdir=infra/gcp plan -var="project_id=YOUR_PROJECT"
```

## Production controls still required

- data-processing agreements and source licenses;
- organization IAM design;
- VPC Service Controls;
- private networking;
- CMEK where required;
- backup and disaster recovery;
- cost and quota controls;
- incident response;
- model/prompt approval workflow;
- separation of pregame, in-game and postgame capabilities.

---

## v0.1.0 — Decision Council on Vertex AI

The production target now includes a governed multi-agent path:

```text
Analyst UI / API (Cloud Run)
          |
          v
Chief Strategy Agent (Vertex AI ADK)
          |
  +-------+-------+----------------+----------------+
  |               |                |                |
Pitching       Starter          Context         Adaptation
Agent          Pulse Agent      Agent           Agent
  |               |                |                |
  +---------------+--------+-------+----------------+
                           |
                       Evidence Gate
                           |
                           v
                    Human approval
                           |
                           v
                 Decision Memory / BigQuery
```

Each specialist receives only the tools and datasets required for its role. BigQuery remains the source of structured truth; agents never invent statistics that can be computed deterministically. Agent trajectories, tool calls, model versions and approvals are logged for evaluation and governance.

Google Cloud components:

- Vertex AI Agent Builder / ADK — specialist orchestration;
- Agent Engine or Cloud Run — runtime;
- BigQuery — structured evidence and decision history;
- BigQuery Vector Search / Vertex AI Search — semantic retrieval;
- Cloud Storage — governed raw and media assets;
- Secret Manager / IAM / VPC Service Controls — isolation;
- Cloud Logging / Monitoring — operational and trajectory audit;
- Looker — executive intelligence.
