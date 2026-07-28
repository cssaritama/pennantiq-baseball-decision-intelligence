from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    root: Path = Path(__file__).resolve().parents[2]
    data_path: Path = Path(os.getenv("PENNANTIQ_DATA_PATH", "data/sample/demo_pitches.csv"))
    results_path: Path = Path(os.getenv("PENNANTIQ_RESULTS_PATH", "data/frozen_real/new_york_results_2026.csv"))
    knowledge_path: Path = Path(os.getenv("PENNANTIQ_KNOWLEDGE_PATH", "knowledge_base"))
    monitoring_db: Path = Path(os.getenv("PENNANTIQ_MONITORING_DB", "data/runtime/monitoring.sqlite"))
    decision_db: Path = Path(os.getenv("PENNANTIQ_DECISION_DB", "data/runtime/decision_memory.sqlite"))
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    data_mode: str = os.getenv("DATA_MODE", "demo")
    gcp_project: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    gcp_location: str = os.getenv("GCP_LOCATION", "US")
    bigquery_dataset: str = os.getenv("BIGQUERY_DATASET", "pennantiq")

    def resolve(self, path: Path) -> Path:
        return path if path.is_absolute() else self.root / path


settings = Settings()
