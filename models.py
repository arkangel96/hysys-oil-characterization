"""Plain records — no COM objects leave the adapter."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StreamSummary:
    name: str
    temperature: float | None = None
    pressure: float | None = None
    molar_flow: float | None = None
    vapor_fraction: float | None = None


@dataclass
class CaseSnapshot:
    case_title: str = ""
    component_names: list[str] = field(default_factory=list)
    streams: list[StreamSummary] = field(default_factory=list)
    oil_manager_hint: str = ""
