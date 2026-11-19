# Contributing
Open an issue before large changes. Contributions must include tests, data provenance, time-aware evaluation and no claims of team affiliation. Do not commit secrets, large uncertain-license datasets or official team marks.

## How this repository is run

Profile `product`. Data class Public. State Active. Owner Carlos Saritama.
README.md states what is deployed and what is not.

Before starting work, read:

1. `README.md`
2. `STATUS.md`
3. The active module in `modules/` or `src/`
4. `docs/standards/PROJECT_STANDARDS.md` and `docs/standards/PROFILE.md`

Then follow links only as far as the change needs. Do not read `archive/`, `past_version/` and raw Statcast data in `data/`
unless the change needs that evidence.

Rules:

- Changes to scoring models and schemas need recorded evidence: the test run and the evaluation results.
- `docs/standards/` is a verified copy of the Systems Studio Engineering Standard. Do not edit it; start specifications, decisions and verification records from `docs/standards/templates/`.
- Work on a focused branch and open a pull request. Keep `main` working.

Verify:

```bash
make test
make audit
```
