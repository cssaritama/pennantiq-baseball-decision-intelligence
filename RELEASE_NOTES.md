# Release Notes — v0.1.0

## PennantIQ: Baseball Decision Intelligence Platform

This is the first public PennantIQ release.

The release is designed around one principle: **public claims must be reproducible and auditable**.

### What is implemented
- An evidence-first pre-game decision-support workflow.
- A deterministic specialist Decision Council with typed evidence contracts.
- Starter Pulse for recent pitcher form and context.
- Matchup planning with Plan A / Plan B / Avoid outputs.
- Context exploration across handedness, home/away and temporal factors when available.
- Chronological Shadow Mode that prevents future-data leakage.
- Trust / monitoring views and decision memory.
- Four retrieval approaches and executable evaluation.
- Optional live LLM providers (Gemini / OpenAI) behind the same evidence package.
- Automated dlt ingestion into DuckDB.
- Docker Compose, tests and CI.

### What is deliberately not claimed
- No championship guarantee.
- No autonomous in-game coaching.
- No causal counterfactual claims from descriptive history.
- No deployed GCP production environment unless independently provisioned and verified.
- No affiliation with MLB, the Yankees, Mets, Dodgers or any other club.

### Certificate note
Before submitting the final course commit, run the live LLM comparison with a configured provider, verify Docker locally, review the Streamlit UI visually, and commit the generated evidence/results.

## Certificate submission hardening
The v0.1.0 submission package now includes a GitHub-hosted real LLM evaluation path. The `Live LLM Evaluation` workflow compares Direct LLM, RAG LLM and Agent + Evidence using GitHub Models, publishes the result artifact and attempts to commit generated evaluation files back to `main` when workflow write permissions are enabled. No external API secret is required for that GitHub Actions path.
