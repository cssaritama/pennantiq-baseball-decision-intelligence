# GitHub Public Upload — v0.1.0

Repository name:

`pennantiq-baseball-decision-intelligence`

Recommended visibility for the course submission: **Public**.

```bash
git init
git branch -M main
git remote add origin https://github.com/cssaritama/pennantiq-baseball-decision-intelligence.git
git add .
git commit -m "release: PennantIQ v0.1.0 initial public release"
git push -u origin main
```

Before creating the certificate tag, complete the final verification in `docs/DELIVERY_CHECKLIST.md`.

Then:

```bash
git add .
git commit -m "release: PennantIQ v0.1.0 certificate submission"
git tag -a v0.1.0 -m "PennantIQ v0.1.0"
git push origin main --tags
git rev-parse HEAD
```

Submit the public repository URL and the exact final commit hash requested by the course.
