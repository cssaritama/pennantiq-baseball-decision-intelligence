# Validation Plan

PennantIQ advances only when evidence supports the next claim.

| Level | Question | Required evidence | Allowed claim |
|---|---|---|---|
| L0 — Technical | Does the repository run? | Clean clone, tests, container and demo | Reproducible prototype |
| L1 — Retrieval | Does it find the right evidence? | BDIB Hit Rate, MRR and error analysis | Evaluated retrieval system |
| L2 — Temporal | Does it avoid future leakage? | Chronological Shadow Mode | Historically replayable workflow |
| L3 — Expert | Are briefs useful to baseball practitioners? | Blind review by analysts/coaches | Practitioner-reviewed decision support |
| L4 — Pilot | Does it improve preparation in workflow? | Prospective shadow pilot and time-saved metrics | Operational pilot evidence |
| L5 — Commercial | Will an organization pay and retain? | Contract, usage and renewal | Validated product |

## Non-negotiable tests
- Time-based train/evaluation separation.
- No player identity leakage into labels.
- Baseline comparisons.
- Calibration and abstention analysis.
- Failure-case review.
- Data provenance and schema checks.
- Human review before operational use.

A historical difference between recommended and observed choices is not proof that the recommendation would have caused a better result. Causal claims are reserved for later research with defensible assumptions.
