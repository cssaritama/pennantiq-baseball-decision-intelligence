# Architecture

## Reproducible public runtime

```mermaid
flowchart LR
  U[Analyst] --> UI[Streamlit workspaces]
  UI --> O[Evidence-first orchestrator]
  O --> S[Starter + Context + Matchup tools]
  O --> R[Hybrid retrieval + reranking]
  S --> D[(Pitch CSV / normalized upload)]
  R --> K[(Methodology knowledge base)]
  O --> L[Optional LLM]
  UI --> J[(Decision Journal)]
  UI --> M[(Feedback + monitoring)]
  D --> B[Chronological Shadow Mode]
  B --> J
```

The LLM explains. Deterministic tools calculate. The application runs without a provider key.

## GCP team target

![GCP target](../assets/gcp-architecture.svg)

See [GCP Architecture](GCP_ARCHITECTURE.md) for layers, datasets, controls and Terraform boundaries.
