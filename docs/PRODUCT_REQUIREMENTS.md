# Product Requirements — v0.2

## Product

PennantIQ is a Baseball Data Intelligence and Decision Memory Platform.

## Primary user

Advance Scouting and Pitching Strategy Analyst.

## Primary workflow

Before a game or series:

1. understand how a starter is arriving;
2. explore relevant time, space and competitive context;
3. produce Plan A, Plan B and Avoid scenarios;
4. expose sample size, uncertainty and limitations;
5. record the human choice;
6. review the decision after the game;
7. preserve the lesson.

## Functional requirements

- clean-clone demo without credentials;
- optional real Statcast upload/download;
- bundled real game-results snapshot;
- source registry and provenance;
- starter recent-form signals;
- sparse/debutant policy;
- context splits with shrinkage and warnings;
- matchup plan and abstention;
- RAG and deterministic tools;
- chronological Shadow Mode;
- decision journal;
- feedback and at least five monitoring charts;
- evaluation scripts;
- Docker Compose;
- optional GCP blueprint.

## Quality requirements

- no future-data leakage;
- no invented metrics;
- no hidden synthetic data;
- no data redistribution without rights;
- deterministic calculations outside the LLM;
- tests for core policies;
- generated evaluation results;
- clear public/private boundary.

## Product success hypotheses

Future pilots should measure:

- preparation time saved;
- analyst usefulness;
- acceptance and modification rate;
- evidence completeness;
- abstention quality;
- learning-loop completion;
- repeated use across series.

These are hypotheses, not achieved results.

## Out of scope for v0.2

- live dugout recommendations;
- championship guarantees;
- medical or injury diagnosis;
- autonomous coaching;
- causal counterfactual claims;
- private team integrations;
- whole-game optimization presented as complete.

## Principles

1. Evidence before eloquence.
2. Deterministic tools before LLM arithmetic.
3. Abstention before unsupported confidence.
4. Temporal validity before headline metrics.
5. Context before superficial splits.
6. Human judgment remains final.
7. Every important decision deserves a memory.
