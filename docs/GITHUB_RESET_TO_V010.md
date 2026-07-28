# Reset the public repository to a clean v0.1.0 history

Use this only if the current public GitHub repository already contains experimental `0.3.x` commits and you want the public history to begin cleanly at `v0.1.0`.

## Recommended for PennantIQ now

Because PennantIQ is still at its initial public/certificate stage, a clean history is reasonable **before** external users depend on old commit hashes.

### 1. Back up the old repository

```bash
git clone https://github.com/cssaritama/pennantiq-baseball-decision-intelligence.git pennantiq-old-backup
```

Keep that backup locally or in the private `pennantiq-internal` repository if you need historical notes. Do not copy Git history into the new public release.

### 2. Work from the v0.1.0 package

Extract this package so the root folder is:

```text
pennantiq-baseball-decision-intelligence/
```

### 3. Create a clean Git history

Inside the extracted folder:

```bash
rm -rf .git
git init
git branch -M main
git add .
git commit -m "release: PennantIQ v0.1.0 initial public release"
git remote add origin https://github.com/cssaritama/pennantiq-baseball-decision-intelligence.git
git push --force -u origin main
```

### 4. Remove obsolete tags/releases

If old `v0.3.x` Git tags or GitHub Releases exist, remove them before the certificate submission so the public release story is coherent.

Local/remote tag example:

```bash
git tag -d v0.3.0 v0.3.1 2>/dev/null || true
git push origin --delete v0.3.0 v0.3.1 2>/dev/null || true
```

Delete any corresponding GitHub Releases from the Releases page if they were created.

### 5. Do not create the final certificate tag yet

First complete:

- live Gemini evaluation;
- Docker build;
- dlt ingestion verification;
- Streamlit visual QA;
- screenshots / demo video;
- CI green.

Then create the final `v0.1.0` tag from the verified certificate commit.

## Alternative

Deleting and recreating the GitHub repository with the same name also creates a clean history, but a force-reset is normally sufficient while the project has no external dependencies.

## Warning

History rewriting is appropriate only because this is still an initial public release. Do not make force-pushing a normal practice once other people rely on public commit hashes.
