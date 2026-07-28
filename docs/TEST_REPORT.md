# Test Report — PennantIQ v0.1.0

## Verified in the packaged repository

The certificate-hardened package was checked with:

```bash
python -m compileall -q src app.py evaluation scripts tests
pytest -q
python evaluation/run_retrieval_evaluation.py
python evaluation/run_answer_evaluation.py
python scripts/run_shadow_mode.py
python scripts/audit_repository.py
```

Results at packaging time:

- **20 automated tests passed**;
- retrieval benchmark: **24 cases**, four methods;
- selected retrieval method: **TF-IDF vector**, MRR@5 **0.9513888889**;
- Shadow Mode: **14,252** chronological rows on the deterministic synthetic fixture;
- repository audit: required evidence present, no broken local Markdown links or obvious API-key patterns found.

## Live LLM evaluation

The package includes `.github/workflows/live-llm-evaluation.yml`. GitHub Actions can call GitHub Models with its automatically generated `GITHUB_TOKEN` when the workflow declares `models: read`. The workflow compares:

1. Direct LLM;
2. RAG LLM;
3. Agent + Evidence.

It writes `evaluation/results/live_llm_github_*`, uploads them as an Actions artifact and attempts to commit them back to `main` when repository workflow permissions allow writes.

This live network call cannot be truthfully marked as executed inside the offline packaging environment. For the final course submission, the public GitHub Actions run should be green and the generated output should be preserved in the repository or workflow artifact.

## Environment-specific checks

The packaging environment did not provide a Docker daemon or installed Streamlit runtime. The public CI therefore performs a Docker Compose build, starts the application and checks Streamlit's health endpoint on GitHub-hosted Ubuntu. A **visual** Streamlit review remains optional portfolio polish rather than a fabricated packaging claim:
- optional Statcast/Retrosheet downloads;
- actual GCP deployment (no cloud bonus is claimed until deployed).
