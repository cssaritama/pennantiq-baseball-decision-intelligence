from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORG_DIR = ROOT / "organizations"


def organization_profiles() -> dict[str, dict]:
    profiles: dict[str, dict] = {}
    if not ORG_DIR.exists():
        return profiles
    for path in sorted(ORG_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        profiles[payload["organization_id"]] = payload
    return profiles


def get_organization(organization_id: str = "demo-generic") -> dict:
    profiles = organization_profiles()
    if organization_id in profiles:
        return profiles[organization_id]
    if profiles:
        return next(iter(profiles.values()))
    return {
        "organization_id": "demo-generic",
        "display_name": "Demo Professional Club",
        "objective": "evidence-backed decision support",
        "mode": "public_research",
        "notes": "Fallback profile.",
    }
