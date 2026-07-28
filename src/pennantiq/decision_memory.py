from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

from .config import settings


DDL = """
CREATE TABLE IF NOT EXISTS decision_journal(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    decision_type TEXT NOT NULL,
    actor TEXT,
    subject TEXT,
    context_json TEXT NOT NULL,
    options_json TEXT NOT NULL,
    chosen_action TEXT NOT NULL,
    rationale TEXT NOT NULL,
    evidence_strength TEXT NOT NULL,
    confidence REAL,
    outcome_json TEXT,
    lesson TEXT,
    status TEXT DEFAULT 'open'
);
"""


def _path() -> Path:
    configured = Path(settings.decision_db)
    path = settings.resolve(configured)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect() -> sqlite3.Connection:
    con = sqlite3.connect(_path())
    con.execute(DDL)
    con.commit()
    return con


def log_decision(
    decision_type: str,
    chosen_action: str,
    rationale: str,
    evidence_strength: str,
    context: dict[str, Any] | None = None,
    options: list[dict[str, Any]] | None = None,
    actor: str = "analyst",
    subject: str = "",
    confidence: float | None = None,
) -> int:
    con = _connect()
    cursor = con.execute(
        """INSERT INTO decision_journal(
            decision_type,actor,subject,context_json,options_json,chosen_action,
            rationale,evidence_strength,confidence
        ) VALUES(?,?,?,?,?,?,?,?,?)""",
        (
            decision_type,
            actor,
            subject,
            json.dumps(context or {}, default=str),
            json.dumps(options or [], default=str),
            chosen_action,
            rationale,
            evidence_strength,
            confidence,
        ),
    )
    rowid = int(cursor.lastrowid)
    con.commit()
    con.close()
    return rowid


def close_decision(decision_id: int, outcome: dict[str, Any], lesson: str) -> None:
    con = _connect()
    con.execute(
        "UPDATE decision_journal SET outcome_json=?, lesson=?, status='closed' WHERE id=?",
        (json.dumps(outcome, default=str), lesson, decision_id),
    )
    con.commit()
    con.close()


def decisions(limit: int = 500) -> pd.DataFrame:
    con = _connect()
    frame = pd.read_sql_query(
        "SELECT * FROM decision_journal ORDER BY id DESC LIMIT ?", con, params=(limit,)
    )
    con.close()
    return frame


def decision_metrics() -> dict:
    frame = decisions()
    if frame.empty:
        return {"decisions": 0, "closed": 0, "learning_rate": 0.0, "evidence_mix": {}}
    closed = int((frame["status"] == "closed").sum())
    return {
        "decisions": int(len(frame)),
        "closed": closed,
        "learning_rate": closed / len(frame),
        "evidence_mix": frame["evidence_strength"].value_counts().to_dict(),
    }
