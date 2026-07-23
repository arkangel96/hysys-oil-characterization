"""Assay / characterization PE intelligence (thin coded layer).

Grow rules in docs/intelligence/ first, then add inventory rows + code here.
Do not auto-rewrite Oil Manager data.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from models import CaseSnapshot


# Characterization acceptance states (Oil Char Assist — not CDU column States A–F)
STATE_LABELS = {
    "O0": "Not connected / no case",
    "O1": "Case open — assay not yet assessed",
    "O2": "Assay incomplete or weak evidence",
    "O3": "Assay plausible — feed candidate",
    "O4": "Assay accepted — hand off to CDU Assist OK",
    "OX": "Blocked — contradictory / unsafe characterization signals",
}


@dataclass
class AssayDiagnosis:
    state: str
    summary: str
    evidence: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    handoff_to_cdu: bool = False


def diagnose_case(snapshot: CaseSnapshot | None) -> AssayDiagnosis:
    """First-pass coded rules — expand via inventory, not ad-hoc UI logic."""
    if snapshot is None:
        return AssayDiagnosis(
            state="O0",
            summary=STATE_LABELS["O0"],
            evidence=["No CaseSnapshot."],
            next_actions=["Connect to a running HYSYS case with crude feed."],
        )

    evidence: list[str] = [
        f"Case: {snapshot.case_title or '(untitled)'}",
        f"Components: {len(snapshot.component_names)}",
        f"Material streams: {len(snapshot.streams)}",
        f"Oil Manager probe: {snapshot.oil_manager_hint}",
    ]

    n_comp = len(snapshot.component_names)
    n_streams = len(snapshot.streams)
    oil_hint = (snapshot.oil_manager_hint or "").lower()

    # Weak signals only — real assay completeness needs Oil Manager COM map.
    if n_streams == 0:
        return AssayDiagnosis(
            state="OX",
            summary=STATE_LABELS["OX"],
            evidence=evidence + ["No material streams visible."],
            next_actions=["Confirm case opened; check flowsheet COM access."],
        )

    if "count=" in oil_hint and "count=0" in oil_hint.replace(" ", "").lower():
        return AssayDiagnosis(
            state="O2",
            summary=STATE_LABELS["O2"],
            evidence=evidence + ["Oil/assay collection reports Count=0."],
            next_actions=[
                "Open Oil Manager in HYSYS and confirm assay exists.",
                "Author COM discovery for assay properties (TBP, density, light ends).",
            ],
        )

    if "no oils/oilmanager" in oil_hint or "not found" in oil_hint:
        return AssayDiagnosis(
            state="O1",
            summary=STATE_LABELS["O1"],
            evidence=evidence + ["Oil Manager COM path not discovered for this build."],
            next_actions=[
                "Run COM discovery on BasisManager / Oils (see docs/COM_DISCOVERY.md).",
                "Meanwhile: manual assay checklist in docs/intelligence/01_Assay_Completeness.md.",
            ],
        )

    if n_comp < 5:
        return AssayDiagnosis(
            state="O2",
            summary=STATE_LABELS["O2"],
            evidence=evidence + [f"Few fluid-package components ({n_comp}) — may lack hypocomponents."],
            next_actions=[
                "Check characterization / hypo generation in Oil Manager.",
                "Do not chase CDU MVs until hypocomponents look credible.",
            ],
        )

    if n_comp >= 20:
        return AssayDiagnosis(
            state="O3",
            summary=STATE_LABELS["O3"],
            evidence=evidence + ["Component count suggests characterized petroleum package."],
            next_actions=[
                "Validate TBP/density/light ends vs lab sheet (intelligence docs).",
                "When checklist passes → mark O4 and hand off to CDU Assist.",
            ],
            handoff_to_cdu=False,
        )

    return AssayDiagnosis(
        state="O1",
        summary=STATE_LABELS["O1"],
        evidence=evidence,
        next_actions=[
            "Inspect Oil Manager assay inputs against lab sheet.",
            "Grow coded completeness checks in assay_engine + inventory.",
        ],
    )


def format_pe_board(diagnosis: AssayDiagnosis) -> str:
    lines = [
        "=== Oil Characterization — PE board ===",
        f"State: {diagnosis.state} — {diagnosis.summary}",
        f"CDU hand-off OK: {'YES' if diagnosis.handoff_to_cdu else 'NO (not yet)'}",
        "",
        "Evidence:",
    ]
    for item in diagnosis.evidence:
        lines.append(f"  • {item}")
    lines.append("")
    lines.append("Next:")
    for item in diagnosis.next_actions:
        lines.append(f"  → {item}")
    lines.append("")
    lines.append("Safety: never auto-save; never silent Oil Manager rewrite.")
    return "\n".join(lines)
