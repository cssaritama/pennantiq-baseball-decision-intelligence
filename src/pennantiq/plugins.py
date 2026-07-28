from __future__ import annotations

from typing import Protocol, runtime_checkable
import pandas as pd


@runtime_checkable
class TeamEvidencePlugin(Protocol):
    """Boundary between PennantIQ Open and private/team-owned evidence packages."""

    plugin_id: str

    def health(self) -> dict: ...

    def pitch_events(self, start: str, end: str) -> pd.DataFrame: ...

    def scouting_context(self, subject_id: str) -> list[dict]: ...


@runtime_checkable
class DecisionPolicyPlugin(Protocol):
    """Optional private organization policy without changing open-core code."""

    plugin_id: str

    def validate(self, decision_package: dict) -> dict: ...
