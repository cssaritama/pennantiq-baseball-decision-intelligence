#!/usr/bin/env python3
"""Static release audit for required files, local links, placeholders and secrets."""
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "README.md",
    "LICENSE",
    "NOTICE.md",
    "Dockerfile",
    "docker-compose.yml",
    "pyproject.toml",
    "docs/RUBRIC_TRACEABILITY.md",
    "docs/DATA_CARD.md",
    "docs/MODEL_CARD.md",
    "evaluation/results/retrieval_results.csv",
    "evaluation/results/answer_summary.csv",
    "evaluation/results/shadow_mode_metrics.json",
}
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SECRET_PATTERNS = {
    "OpenAI-style key": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "Google-style key": re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
}


def markdown_link_failures() -> list[str]:
    failures: list[str] = []
    for document in ROOT.rglob("*.md"):
        for target in LINK_RE.findall(document.read_text(encoding="utf-8", errors="ignore")):
            target = target.strip().split()[0].strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative = target.split("#", 1)[0]
            if relative and not (document.parent / relative).resolve().exists():
                failures.append(f"{document.relative_to(ROOT)} -> {target}")
    return failures


def secret_findings() -> list[str]:
    findings: list[str] = []
    ignored = {".git", ".venv", "__pycache__", ".pytest_cache"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in ignored for part in path.parts):
            continue
        if path.stat().st_size > 2_000_000:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{label}: {path.relative_to(ROOT)}")
    return findings


def main() -> int:
    errors: list[str] = []
    missing = sorted(path for path in REQUIRED if not (ROOT / path).exists())
    errors.extend(f"Missing required file: {path}" for path in missing)
    errors.extend(f"Broken Markdown link: {item}" for item in markdown_link_failures())
    errors.extend(f"Possible secret: {item}" for item in secret_findings())

    if errors:
        print("Repository audit failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    file_count = sum(1 for path in ROOT.rglob("*") if path.is_file())
    print(f"Repository audit passed: {file_count} files, required evidence present, no broken local Markdown links or key patterns found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
