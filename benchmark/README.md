# BDIB — Baseball Decision Intelligence Benchmark

BDIB is the public evaluation layer of PennantIQ. Version 0.1 contains knowledge-retrieval and answer-quality cases under `evaluation/datasets/`.

## Why publish a benchmark?
A demo can be visually impressive while remaining impossible to verify. BDIB makes model changes comparable and prevents PennantIQ from selecting examples only after seeing favorable outputs.

## Current tracks
1. **Knowledge retrieval** — locate the correct methodology or policy document.
2. **Answer behavior** — compare direct answers, RAG and evidence-first agent outputs.
3. **Abstention** — verify that the system declines unsupported conclusions.

## Planned private and expert tracks
- Pitch-plan usefulness scored by qualified analysts.
- Temporal Shadow Mode cases built from licensed data.
- Strategy stability across seasons and rule environments.
- Off-policy evaluation and calibration.

Public benchmark items must not expose team-owned scouting knowledge.
