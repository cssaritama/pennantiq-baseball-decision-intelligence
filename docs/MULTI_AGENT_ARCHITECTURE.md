# PennantIQ Decision Council — Multi-Agent Architecture

## Decision

PennantIQ uses a **council architecture**, not a swarm.

The public v0.1.0 release implements specialist evidence producers through deterministic workflows. This is intentional: baseball statistics should not be invented or recalculated by language models. A production Team edition can move individual specialists to Google Cloud Vertex AI Agent Builder / Agent Development Kit while retaining the same typed evidence contracts.

## Public council

```text
                         HUMAN ANALYST / COACH
                                  |
                                  v
                         CHIEF STRATEGY LAYER
                                  |
            +---------------------+---------------------+
            |                     |                     |
            v                     v                     v
   PITCHING STRATEGY      STARTER PULSE        CONTEXT INTELLIGENCE
            |                     |                     |
            +----------+----------+----------+----------+
                       |                     |
                       v                     v
             OPPONENT ADAPTATION      EVIDENCE GATE
                       |                     |
                       +----------+----------+
                                  |
                                  v
                          DECISION BRIEF
                                  |
                                  v
                          HUMAN APPROVAL
                                  |
                                  v
                          DECISION MEMORY
```

## Specialist contracts

### Pitching Strategy Agent

Question: what pitcher–batter scenario is best supported by the active evidence?

Tools: matchup ranking, pitch family, zone, count, handedness and evidence thresholds.

### Starter Pulse Agent

Question: how is the pitcher arriving relative to his own baseline?

Tools: recent appearances, velocity, whiff, hard contact, rest and sparse-history protocol.

### Context Intelligence Agent

Question: which time/space splits are relevant and which are likely noise?

Tools: home/away, handedness, day/night, day of week, rest, opponent and venue with empirical-Bayes shrinkage.

### Opponent Adaptation Agent

Question: has the opponent's observable response changed across recent windows?

Tools: pitch-family response shifts, whiff changes, sample sizes and associative warnings.

### Evidence Auditor / Gate

Question: is the council allowed to speak confidently?

The gate can force `human_review_required` even if another specialist produces a strong-sounding idea.

### Chief Strategy Agent

Synthesizes specialist reports. It may explain trade-offs but must never overwrite deterministic evidence or remove an abstention warning.

## Roadmap agents

Only add agents when data and evaluation exist:

- Bullpen Strategy Agent;
- Offensive Approach Agent;
- Lineup Construction Agent;
- Defense & Positioning Agent;
- Baserunning Agent;
- Roster & Transaction Agent;
- Player Development Agent;
- Dynasty Benchmark Agent;
- Integrity & Governance Agent;
- Organizational Memory Agent.

## Why not make everything an agent?

Every autonomous agent adds latency, cost, failure modes and evaluation burden. PennantIQ follows a simple rule:

> If a deterministic function can calculate the answer reliably, use a tool. If judgment requires combining uncertain evidence across domains, consider an agent.

## GCP Team target

- Vertex AI Agent Builder / ADK for specialist orchestration;
- Agent Engine or Cloud Run for runtime;
- BigQuery for structured evidence;
- BigQuery Vector Search / Vertex AI Search for semantic evidence;
- Cloud Storage for governed raw assets;
- IAM, Secret Manager and VPC Service Controls for isolation;
- Cloud Logging/Monitoring for trajectory and tool-call audits;
- human-in-the-loop approval before any strategy artifact becomes operational.
