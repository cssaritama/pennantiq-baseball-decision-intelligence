# Organization Model

PennantIQ is team-agnostic. Organization configuration changes the objective, data entitlements, knowledge base, model versions and decision memory without changing core code.

```text
Organization
├── identity and objective
├── roster and availability
├── public evidence
├── private licensed evidence
├── scouting knowledge
├── model / feature versions
├── decision policies
├── decision memory
└── access controls
```

The public repository includes four safe profiles:

- generic professional club;
- Yankees public championship-edge case;
- Mets public turnaround case;
- Dodgers public dynasty benchmark.

No profile implies affiliation.

The private Team edition should enforce tenant isolation in BigQuery datasets/projects, Cloud Storage buckets, service accounts and agent tool permissions.
