# 01 Pitching Matchup

**Status:** Implemented baseline in v0.1  
**Primary user:** Advance Scouting and Pitching Strategy Analyst

## Decision
How should an available pitcher approach a hitter by count, pitch family and target region before a game?

## Required data
Pitch-level outcomes, handedness, count, location, velocity, movement proxies and methodology documents.

## Evaluation gate
Retrieval benchmark, evidence coverage, abstention, chronological Shadow Mode and expert review.

## Release boundary
Public baseline. Team-specific scouting and proprietary features remain private.

## Acceptance criteria before promotion
- Data rights and temporal semantics documented.
- A transparent baseline and leakage-resistant evaluation exist.
- Evidence strength, abstention and human override are implemented.
- Monitoring and failure modes are documented.
- Domain practitioners review the workflow.

This file is a product contract. It does not imply that roadmap code or data integrations already exist.
