# Open-Core Plugin Boundary

PennantIQ Open and PennantIQ Team should not become two unrelated codebases.

The public repository defines stable interfaces for private capabilities. Private packages can implement those interfaces and be injected at deployment time.

Public contracts currently include conceptual protocols for:

- team evidence sources;
- private scouting context;
- organization-specific decision policy.

The public repository never contains team credentials, private endpoints or proprietary models.

## Why this matters

- a reviewer can clone Open and run it;
- a team can add private evidence without forking the entire platform;
- proprietary IP stays private;
- common bug fixes can flow through the open core;
- enterprise data isolation remains explicit.

## Future packaging

Possible structure:

```text
pennantiq-open/              # public GitHub
pennantiq-team-plugins/      # private package/repository
pennantiq-customer-config/   # per-organization deployment configuration
```

Private plugins are created only when real proprietary value exists.
