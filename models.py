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
class ComponentFraction:
    name: str
    fraction: float | None = None
    kind: str = "other"  # light | nbp | other


@dataclass
class StreamComposition:
    stream_name: str
    basis: str = "mass"  # mass | mole | unknown
    components: list[ComponentFraction] = field(default_factory=list)
    error: str = ""

    @property
    def light_count(self) -> int:
        return sum(1 for c in self.components if c.kind == "light")

    @property
    def nbp_count(self) -> int:
        return sum(1 for c in self.components if c.kind == "nbp")

    @property
    def has_nbp_slate(self) -> bool:
        return self.nbp_count >= 3


@dataclass
class BlendSummary:
    name: str
    is_ready_to_install: bool | None = None
    assay_names: list[str] = field(default_factory=list)


@dataclass
class OilManagerSnapshot:
    found: bool = False
    path: str = ""
    assay_names: list[str] = field(default_factory=list)
    oil_names: list[str] = field(default_factory=list)
    blends: list[BlendSummary] = field(default_factory=list)
    readable_members: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    error: str = ""

    @property
    def assay_count(self) -> int:
        return len(self.assay_names)

    @property
    def blend_count(self) -> int:
        return len(self.blends)

    @property
    def any_blend_ready(self) -> bool:
        return any(b.is_ready_to_install for b in self.blends if b.is_ready_to_install)


@dataclass
class FeedAttachEvidence:
    """Heuristics from live COM reads — not a silent write proof."""

    feed_stream: str = ""
    oil_installed: bool = False
    feed_attached: bool = False
    nbp_count: int = 0
    light_count: int = 0
    blend_ready: bool = False
    notes: list[str] = field(default_factory=list)


@dataclass
class CaseSnapshot:
    case_title: str = ""
    component_names: list[str] = field(default_factory=list)
    streams: list[StreamSummary] = field(default_factory=list)
    oil_manager_hint: str = ""
    oil_manager: OilManagerSnapshot = field(default_factory=OilManagerSnapshot)
    feed_composition: StreamComposition | None = None
    feed_evidence: FeedAttachEvidence = field(default_factory=FeedAttachEvidence)
