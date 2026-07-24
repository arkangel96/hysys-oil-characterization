"""Complementary intelligence — thin executable constraints (OC-COMP).

Docs live in complementary_intelligence/. This module exposes the hard
defaults and never-rules for the PE board / QA path. Does not supersede
pack v1 LE/TBP checks in assay_engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# From OC_D5 — binding defaults
DEFAULTS: dict[str, Any] = {
    "thermo_package": "PR",
    "allow_api_estimated_blend": False,
    "allow_silent_tbp_extrapolation": False,
    "allow_unresolved_light_ends_basis": False,
    "allow_O4_without_hypo_review": False,
    "allow_COM_write": False,
    "manual_oil_manager_first": True,
}

NEVER_RULES: tuple[str, ...] = (
    "auto_save_hsc",
    "silent_oil_manager_write",
    "silent_tbp_extrapolation",
    "invent_blend_percent",
    "o4_without_hypo_review",
    "use_product_specs_as_assay_input",
    "chase_cdu_mvs_for_bad_feed",
)

PRIORITY_STACK: tuple[str, ...] = (
    "assay_honesty",
    "traceable_source",
    "characterize_install_feed",
    "yield_check_vs_material_balance",
    "o4_handoff",
    "cdu_final_targets_storage_only",
)


@dataclass
class ComplementaryGate:
    """Result of applying complementary constraints to an assay QA result."""

    o4_blocked: bool
    reasons: list[str] = field(default_factory=list)
    reminders: list[str] = field(default_factory=list)
    defaults: dict[str, Any] = field(default_factory=dict)


def apply_complementary_gate(
    *,
    qa_status: str,
    flags: list[str] | None = None,
    hypo_reviewed: bool = False,
    feed_attached: bool = False,
    oil_installed: bool = False,
) -> ComplementaryGate:
    """Block O4 / surface never-rules. Does not invent assay numbers."""
    flags = list(flags or [])
    reasons: list[str] = []
    reminders: list[str] = [
        "manual_oil_manager_first=true — enter assay in Oil Manager yourself for now",
        "allow_COM_write=false — no silent Oil Manager automation",
        "product specs = FINAL_TARGETS for CDU later — not Oil Manager inputs",
        "material balance %wt = yield check after characterize — not distillation input",
    ]

    if "TBP_COVERAGE_BELOW_O2" in flags or qa_status == "OX":
        if not DEFAULTS["allow_silent_tbp_extrapolation"]:
            reasons.append("silent_tbp_extrapolation forbidden — obtain residue/Intertek or accept OX")

    if not DEFAULTS["allow_unresolved_light_ends_basis"]:
        if "UNRESOLVED_LIGHT_ENDS_BASIS" in flags:
            reasons.append("unresolved light-ends basis — fix before characterize")

    o4_blocked = True
    if qa_status in {"O2", "O3"} and oil_installed and feed_attached and hypo_reviewed:
        if DEFAULTS["allow_O4_without_hypo_review"]:
            o4_blocked = False
        elif hypo_reviewed:
            o4_blocked = False
    else:
        if not hypo_reviewed and not DEFAULTS["allow_O4_without_hypo_review"]:
            reasons.append("O4 blocked — hypo review required")
        if not oil_installed:
            reasons.append("O4 blocked — installed oil required")
        if not feed_attached:
            reasons.append("O4 blocked — FEED attach required")
        if qa_status not in {"O2", "O3"}:
            reasons.append(f"O4 blocked — assay QA status is {qa_status}, need O2/O3 first")

    return ComplementaryGate(
        o4_blocked=o4_blocked,
        reasons=reasons,
        reminders=reminders,
        defaults=dict(DEFAULTS),
    )


def format_complementary_block(gate: ComplementaryGate) -> str:
    lines = [
        "--- Complementary rules (OC-COMP) ---",
        f"O4 allowed: {'NO' if gate.o4_blocked else 'YES'}",
        f"Thermo default: {gate.defaults.get('thermo_package')}",
        f"COM write: {gate.defaults.get('allow_COM_write')}",
        f"Manual Oil Manager first: {gate.defaults.get('manual_oil_manager_first')}",
        "",
        "Never:",
    ]
    for rule in NEVER_RULES:
        lines.append(f"  • {rule}")
    if gate.reasons:
        lines.append("")
        lines.append("Gate reasons:")
        for reason in gate.reasons:
            lines.append(f"  • {reason}")
    lines.append("")
    lines.append("Reminders:")
    for item in gate.reminders:
        lines.append(f"  → {item}")
    return "\n".join(lines)
