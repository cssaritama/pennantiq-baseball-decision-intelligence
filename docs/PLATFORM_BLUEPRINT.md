# PennantIQ Platform Blueprint

## Product category

PennantIQ is a Baseball Data Intelligence and Decision Memory Platform. Its central object is not a chart or an answer; it is a **decision package** containing context, alternatives, evidence, uncertainty, chosen action, outcome and lesson.

## Platform layers

### 1. Data Fabric

- source registry and ownership;
- raw immutable landing;
- normalized pitch, play, game, roster and environment models;
- freshness, lineage and quality rules;
- era and tracking-definition boundaries.

### 2. Context Engine

- time: recency, rest, season phase, game time, inning and order cycle;
- space: park, home/away, location, weather, roof and elevation;
- competition: handedness, count, opponent, role and pitch family;
- statistical safeguards: minimum samples, shrinkage, stability and abstention.

### 3. Decision Services

- Starter Pulse;
- Matchup Lab;
- Opponent Adaptation Signals;
- Scenario Lab;
- Shadow Mode;
- future bullpen, lineup, offense, defense and roster services.

### 4. Knowledge and Agent Layer

- RAG over methodology, policy and team knowledge;
- deterministic tools for calculations;
- query rewriting and intent classification;
- role-specific explanations;
- citations, uncertainty and abstention.

### 5. Decision Memory

- intention;
- options considered;
- chosen action;
- evidence strength;
- human confidence;
- observed outcome;
- postgame lesson;
- searchable organizational history.

### 6. Trust and Governance

- data and model provenance;
- prompt/tool/model versions;
- pregame/in-game/postgame control boundaries;
- access, audit and retention;
- bias, leakage and data-quality monitoring.

## Initial user

Advance Scouting and Pitching Strategy Analyst.

## Initial job to be done

Produce an evidence-backed pregame plan for a pitcher and opponent, explain current form and context, preserve the analyst's decision and review it after the game.

## Why pitching first

Pitch-level data offers clear event granularity, repeatable decisions and chronological evaluation. Expanding to the entire game before validating one decision loop would create a broad but shallow product.

## Expansion principle

A module advances from roadmap to implementation only when it has:

1. a named user;
2. a defined decision;
3. legally usable data;
4. a baseline;
5. an evaluation design;
6. an abstention rule;
7. a human review process.
