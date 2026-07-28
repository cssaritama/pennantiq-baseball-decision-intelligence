# PennantIQ — Submission Ready Guide

This document separates what the repository can verify automatically from what depends on the GitHub-hosted environment.

## What is already part of the submission

- explicit problem statement, target user, decision gap and solution;
- structured data + knowledge-base architecture;
- automated dlt ingestion to DuckDB;
- four retrieval approaches and a 24-question benchmark;
- best retrieval approach selected from generated results;
- live LLM evaluation script for Direct / RAG / Agent+Evidence;
- GitHub Models workflow using the repository `GITHUB_TOKEN`;
- Streamlit interface;
- feedback + monitoring dashboard;
- Dockerfile + Docker Compose;
- deterministic fixture, real game-level snapshot and optional real-data adapters;
- Shadow Mode chronological validation;
- tests, CI, repository audit and pinned dependencies;
- documentation, data/model cards, responsible-use and legal boundaries.

## One push completes the live LLM evidence

The workflow `.github/workflows/live-llm-evaluation.yml` has `models: read` permission and calls GitHub Models with the automatic Actions token. On the first push containing the workflow it:

1. runs a real model on six cases;
2. compares Direct LLM, RAG LLM and Agent + Evidence;
3. uses an LLM-as-judge rubric for groundedness, actionability, uncertainty and evidence use;
4. uploads the result files as an Actions artifact;
5. commits the generated `live_llm_github_*` files back to `main` when repository workflow permissions allow writes.

If repository Actions are configured read-only, the artifact still contains the results. Change **Settings → Actions → General → Workflow permissions** to **Read and write permissions** if you want the bot to commit them automatically.

## Final GitHub checks

1. `Actions → CI` is green. This workflow now builds Docker Compose, starts the app and checks the Streamlit health endpoint.
2. `Actions → Live LLM Evaluation` is green.
3. `evaluation/results/live_llm_github_summary.csv` exists in the repository OR is available as the workflow artifact.
4. The public repository URL works without authentication.
5. Copy the final commit hash shown by GitHub or run `git rev-parse HEAD` locally.
6. Submit the public repository URL and that exact commit hash.
7. Complete three peer reviews as required by the course.

## Optional polish, not a grading blocker

Real screenshots and a short app demo video are strongly recommended for portfolio value. Do not use mock screenshots. Add them only after launching the actual Streamlit app.
