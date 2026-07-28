from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .config import settings


def load_source_registry(path: str | Path = "data/source_registry.json") -> list[dict]:
    source = settings.resolve(Path(path))
    if not source.exists():
        return []
    return json.loads(source.read_text(encoding="utf-8"))


def source_table() -> pd.DataFrame:
    records = load_source_registry()
    return pd.DataFrame(records)


def catalog_health() -> dict:
    sources = load_source_registry()
    active = [s for s in sources if s.get("status") in {"available", "connector_ready"}]
    frozen = [s for s in sources if s.get("mode") == "frozen_real"]
    return {
        "registered_sources": len(sources),
        "active_or_ready": len(active),
        "frozen_real_sources": len(frozen),
        "gcp_ready": any(s.get("mode") == "gcp" for s in sources),
    }
