# Live LLM Evaluation

PennantIQ compares Direct LLM, RAG LLM and Agent + Evidence approaches.

The GitHub Actions workflow uses GitHub Models for reproducible CI evaluation. The workflow has retry/backoff handling for transient provider rate limits (HTTP 429).

The public repository demonstrates evaluation engineering. Enterprise deployments may use Vertex AI/GCP providers.
