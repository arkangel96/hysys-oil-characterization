"""Assay / characterization PE intelligence.

Merges MRC intelligence pack rules (OC-01 LE/TBP/completeness) with HYSYS
case heuristics. Do not auto-rewrite Oil Manager data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from models import CaseSnapshot

from complementary_rules import apply_complementary_gate, format_complementary_block
from aspen_intelligence import format_aspen_block
from pe_identity import (
    PRODUCT_NAME,
    expert_next_actions,
    format_identity_block,
    pe_banner,
)

CASES_DIR = Path(__file__).resolve().parent / "docs" / "intelligence" / "cases"

STATE_LABELS = {
    "O0": "Not connected / no assay loaded",
    "O1": "Raw assay captured / not fully assessed",
    "O2": "Minimum usable assay",
    "O3": "Strong / preferred assay",
    "O4": "Assay accepted — CDU hand-off OK",
    "OX": "Blocked — contradictory / incomplete characterization",
}


@dataclass
class QAResult:
    status: str
    flags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssayDiagnosis:
    state: str
    summary: str
    evidence: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    handoff_to_cdu: bool = False
    qa: QAResult | None = None
    assay_id: str | None = None
    assay: dict[str, Any] | None = None


def cases_dir() -> Path:
    return CASES_DIR


def load_json(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_assay(crude_id: str) -> dict[str, Any]:
    """Load Basrah or Mishrif assay JSON from the cases pack."""
    key = crude_id.strip().upper()
    mapping = {
        "BASRAH": "basrah_assay.json",
        "MISHRIF": "mishrif_assay.json",
    }
    if key not in mapping:
        raise FileNotFoundError(f"Unknown crude_id {crude_id!r}; expected BASRAH or MISHRIF")
    path = CASES_DIR / mapping[key]
    if not path.is_file():
        raise FileNotFoundError(path)
    return load_json(path)


def load_mrc_support() -> dict[str, Any]:
    """Material balance, battery limits, FINAL_TARGETS (not assay inputs)."""
    return {
        "material_balance": load_json(CASES_DIR / "mrc_material_balance.json"),
        "battery_limits": load_json(CASES_DIR / "mrc_battery_limits.json"),
        "final_targets": load_json(CASES_DIR / "mrc_final_targets.json"),
    }


def normalize_light_ends(assay: dict[str, Any]) -> QAResult:
    le = assay.get("light_ends", {})
    basis = le.get("basis")
    bulk = le.get("light_ends_bulk_wt_pct_of_crude")
    comps = le.get("components", {}) or {}
    numeric = {k: float(v) for k, v in comps.items() if v is not None}
    total = sum(numeric.values())

    if basis == "OF_WHOLE_CRUDE":
        return QAResult("PASS", metrics={"whole_crude_wt_pct": numeric, "sum": total})
    if basis != "OF_LIGHT_ENDS_CUT":
        return QAResult("FAIL", flags=["UNRESOLVED_LIGHT_ENDS_BASIS"])
    if bulk is None:
        return QAResult("FAIL", flags=["MISSING_LIGHT_ENDS_BULK_FRACTION"])
    if not numeric:
        return QAResult("FAIL", flags=["MISSING_LIGHT_ENDS_COMPONENTS"])
    if total < 95 or total > 105:
        return QAResult(
            "FAIL",
            flags=["LIGHT_ENDS_COMPONENT_SUM_OUTSIDE_95_105"],
            metrics={"sum": total},
        )

    warnings: list[str] = [] if 98 <= total <= 102 else ["LIGHT_ENDS_COMPONENTS_RENORMALIZED"]
    frac = {k: v / total for k, v in numeric.items()}
    whole = {k: float(bulk) * f for k, f in frac.items()}
    return QAResult(
        "PASS",
        warnings=warnings,
        metrics={
            "raw_sum": total,
            "normalized_cut_fraction": frac,
            "whole_crude_wt_pct": whole,
            "light_ends_bulk_wt_pct_of_crude": float(bulk),
        },
    )


def validate_tbp(assay: dict[str, Any]) -> QAResult:
    pts: list[tuple[float, float]] = []
    for point in assay.get("tbp", {}).get("points", []) or []:
        if point.get("temperature_C") is None or point.get("cumulative_wt_pct") is None:
            continue
        pts.append((float(point["temperature_C"]), float(point["cumulative_wt_pct"])))

    if len(pts) < 5:
        return QAResult("FAIL", flags=["INSUFFICIENT_TBP_POINTS"])

    flags: list[str] = []
    warnings: list[str] = []
    for i, (t, y) in enumerate(pts):
        if not 0 <= y <= 100:
            flags.append(f"TBP_YIELD_OUT_OF_RANGE_AT_{i}")
        if i:
            pt, py = pts[i - 1]
            if t < pt:
                flags.append(f"TBP_TEMPERATURE_NON_MONOTONIC_AT_{i}")
            if y < py:
                flags.append(f"TBP_YIELD_NON_MONOTONIC_AT_{i}")
            if t == pt and y != py:
                warnings.append(f"DUPLICATE_TEMPERATURE_AT_{i}")
            if y == py and t != pt:
                warnings.append(f"DUPLICATE_YIELD_AT_{i}")

    max_y = max(y for _, y in pts)
    if max_y < 90:
        flags.append("TBP_COVERAGE_BELOW_O2")
    elif max_y < 97:
        warnings.append("TBP_COVERAGE_BELOW_O3")

    return QAResult(
        "FAIL" if flags else "PASS",
        flags=flags,
        warnings=warnings,
        metrics={"point_count": len(pts), "max_cumulative_wt_pct": max_y},
    )


def _has_viscosity(bulk: dict[str, Any]) -> bool:
    return any(
        bulk.get(k) is not None
        for k in (
            "viscosity_cSt_20C",
            "viscosity_cSt_40C",
            "viscosity_cSt_50C",
            "viscosity_cSt_100C",
        )
    )


def completeness_check(assay: dict[str, Any]) -> QAResult:
    flags: list[str] = []
    warnings: list[str] = []
    bulk = assay.get("bulk", {}) or {}
    source = assay.get("source", {}) or {}

    if not assay.get("crude_id"):
        flags.append("MISSING_CRUDE_ID")
    if not source.get("tag"):
        flags.append("MISSING_SOURCE_TAG")
    if bulk.get("api_gravity") is None and bulk.get("specific_gravity_15C") is None:
        flags.append("MISSING_API_OR_SG")
    if not _has_viscosity(bulk):
        flags.append("MISSING_VISCOSITY")
    if bulk.get("sulfur_wt_pct") is None:
        flags.append("MISSING_SULFUR")

    tbp = validate_tbp(assay)
    le = normalize_light_ends(assay)
    flags.extend(tbp.flags)
    flags.extend(le.flags)
    warnings.extend(tbp.warnings)
    warnings.extend(le.warnings)

    if flags:
        return QAResult(
            "OX",
            flags=sorted(set(flags)),
            warnings=sorted(set(warnings)),
            metrics={"tbp": tbp.metrics, "light_ends": le.metrics},
        )

    strong = [
        "specific_gravity_15C",
        "rvp_kPa",
        "ccr_wt_pct",
        "asphaltenes_wt_pct",
        "tan_mgKOH_g",
        "vanadium_wt_ppm",
        "nickel_wt_ppm",
        "salt_norm_ppm",
    ]
    coverage = 100.0 * sum(bulk.get(k) is not None for k in strong) / len(strong)
    status = (
        "O3"
        if coverage >= 75
        and tbp.metrics.get("max_cumulative_wt_pct", 0) >= 97
        and source.get("confidence") in {"high", "medium"}
        else "O2"
    )
    return QAResult(
        status,
        warnings=sorted(set(warnings)),
        metrics={
            "strong_field_coverage_percent": coverage,
            "tbp": tbp.metrics,
            "light_ends": le.metrics,
        },
    )


def compare_boundary_tbp(light: dict[str, Any], heavy: dict[str, Any]) -> QAResult:
    """Basrah (light) should generally exceed Mishrif yield at the same T."""
    light_pts = {
        float(p["temperature_C"]): float(p["cumulative_wt_pct"])
        for p in light.get("tbp", {}).get("points", [])
        if p.get("temperature_C") is not None and p.get("cumulative_wt_pct") is not None
    }
    heavy_pts = {
        float(p["temperature_C"]): float(p["cumulative_wt_pct"])
        for p in heavy.get("tbp", {}).get("points", [])
        if p.get("temperature_C") is not None and p.get("cumulative_wt_pct") is not None
    }
    common = sorted(set(light_pts) & set(heavy_pts))
    if len(common) < 5:
        return QAResult("FAIL", flags=["BOUNDARY_TBP_TOO_FEW_COMMON_POINTS"])

    inversions = 0
    for t in common:
        # Allow tiny tolerance; at 40 C proposal has slight Mishrif > Basrah
        if light_pts[t] + 0.5 < heavy_pts[t]:
            inversions += 1

    warnings: list[str] = []
    flags: list[str] = []
    if inversions > max(2, len(common) // 4):
        flags.append("BOUNDARY_TBP_REPEATED_INVERSION")
    elif inversions:
        warnings.append(f"BOUNDARY_TBP_MINOR_INVERSIONS={inversions}")

    return QAResult(
        "FAIL" if flags else "PASS",
        flags=flags,
        warnings=warnings,
        metrics={"common_points": len(common), "inversions": inversions},
    )


def diagnose_assay(assay: dict[str, Any]) -> AssayDiagnosis:
    qa = completeness_check(assay)
    crude = str(assay.get("crude_id") or "?")
    role = (assay.get("design") or {}).get("role")
    bulk = assay.get("bulk") or {}
    evidence = [
        f"Assay: {crude} ({assay.get('display_name') or ''})".strip(),
        f"Source: {(assay.get('source') or {}).get('tag')}",
        f"Role: {role}",
        f"API / SG: {bulk.get('api_gravity')} / {bulk.get('specific_gravity_15C')}",
        f"QA status: {qa.status}",
    ]
    if qa.flags:
        evidence.append("Flags: " + ", ".join(qa.flags))
    if qa.warnings:
        evidence.append("Warnings: " + ", ".join(qa.warnings))
    tbp_m = (qa.metrics or {}).get("tbp") or {}
    if tbp_m:
        evidence.append(
            f"TBP points: {tbp_m.get('point_count')}; "
            f"max cum wt%={tbp_m.get('max_cumulative_wt_pct')}"
        )
    le_m = (qa.metrics or {}).get("light_ends") or {}
    if le_m.get("raw_sum") is not None:
        evidence.append(f"LE cut sum: {le_m.get('raw_sum'):.2f} wt%")

    if qa.status == "OX":
        return AssayDiagnosis(
            state="OX",
            summary=STATE_LABELS["OX"],
            evidence=evidence,
            next_actions=expert_next_actions("OX"),
            qa=qa,
            assay_id=crude,
            assay=assay,
        )

    if qa.status == "O3":
        return AssayDiagnosis(
            state="O3",
            summary=STATE_LABELS["O3"],
            evidence=evidence,
            next_actions=expert_next_actions("O3"),
            qa=qa,
            assay_id=crude,
            assay=assay,
        )

    return AssayDiagnosis(
        state="O2",
        summary=STATE_LABELS["O2"],
        evidence=evidence,
        next_actions=expert_next_actions("O2"),
        qa=qa,
        assay_id=crude,
        assay=assay,
    )


def diagnose_mrc_pack() -> AssayDiagnosis:
    """Load both boundary assays + support files; return combined PE board diagnosis."""
    basrah = load_assay("BASRAH")
    mishrif = load_assay("MISHRIF")
    support = load_mrc_support()
    d_b = diagnose_assay(basrah)
    d_m = diagnose_assay(mishrif)
    boundary = compare_boundary_tbp(basrah, mishrif)

    feed = (support["battery_limits"] or {}).get("feed_seed") or {}
    mb = support["material_balance"] or {}
    rate = (mb.get("volumetric_crude_rate_m3_h_15C") or {}).get("nominal_100pct")

    evidence = [
        "MRC pack loaded from docs/intelligence/cases/",
        f"Basrah QA: {d_b.state} — flags={d_b.qa.flags if d_b.qa else []}",
        f"Mishrif QA: {d_m.state} — flags={d_m.qa.flags if d_m.qa else []}",
        f"Boundary TBP compare: {boundary.status} "
        f"(inversions={boundary.metrics.get('inversions')})",
        f"FEED seed: T={feed.get('temperature_C')} C, "
        f"P={feed.get('pressure_kg_cm2_g')} kg/cm2 g, "
        f"rate={rate} m3/h @15C",
    ]
    if boundary.warnings:
        evidence.append("Boundary warnings: " + ", ".join(boundary.warnings))
    if boundary.flags:
        evidence.append("Boundary flags: " + ", ".join(boundary.flags))

    worst = "OX" if "OX" in {d_b.state, d_m.state} or boundary.status == "FAIL" else d_b.state
    if d_m.state == "OX" or d_b.state == "OX":
        worst = "OX"
    elif d_b.state == "O2" or d_m.state == "O2":
        worst = "O2"

    actions = [
        *expert_next_actions(worst),
        "Use basrah_assay.json / mishrif_assay.json for Oil Manager entry.",
        "Material balance / FINAL_TARGETS are yield & CDU checks — not assay inputs.",
    ]
    return AssayDiagnosis(
        state=worst,
        summary=STATE_LABELS.get(worst, worst),
        evidence=evidence,
        next_actions=actions,
        handoff_to_cdu=False,
        assay_id="MRC_PACK",
        assay=basrah,
    )


def diagnose_case(snapshot: CaseSnapshot | None) -> AssayDiagnosis:
    """HYSYS live-case heuristics (COM). Separate from assay-JSON QA."""
    if snapshot is None:
        return AssayDiagnosis(
            state="O0",
            summary=STATE_LABELS["O0"],
            evidence=["No HYSYS CaseSnapshot."],
            next_actions=expert_next_actions("O0"),
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

    if n_streams == 0:
        return AssayDiagnosis(
            state="OX",
            summary=STATE_LABELS["OX"],
            evidence=evidence + ["No material streams visible."],
            next_actions=expert_next_actions("OX"),
        )

    if "count=" in oil_hint and "count=0" in oil_hint.replace(" ", "").lower():
        return AssayDiagnosis(
            state="O2",
            summary=STATE_LABELS["O2"],
            evidence=evidence + ["Oil/assay collection reports Count=0."],
            next_actions=expert_next_actions("O2"),
        )

    if "no oils/oilmanager" in oil_hint or "not found" in oil_hint:
        return AssayDiagnosis(
            state="O1",
            summary=STATE_LABELS["O1"],
            evidence=evidence + ["Oil Manager COM path not discovered for this build."],
            next_actions=expert_next_actions("O1"),
        )

    if n_comp < 5:
        return AssayDiagnosis(
            state="O2",
            summary=STATE_LABELS["O2"],
            evidence=evidence + [f"Few fluid-package components ({n_comp})."],
            next_actions=expert_next_actions("O2"),
        )

    if n_comp >= 20:
        return AssayDiagnosis(
            state="O3",
            summary=STATE_LABELS["O3"],
            evidence=evidence + ["Component count suggests characterized package."],
            next_actions=expert_next_actions("O3"),
        )

    return AssayDiagnosis(
        state="O1",
        summary=STATE_LABELS["O1"],
        evidence=evidence,
        next_actions=expert_next_actions("O1"),
    )


def format_pe_board(diagnosis: AssayDiagnosis) -> str:
    lines = [
        pe_banner(),
        "",
        "=== Oil Characterization — PE board ===",
        f"State: {diagnosis.state} — {diagnosis.summary}",
        f"Assay id: {diagnosis.assay_id or '(none)'}",
        f"CDU hand-off OK: {'YES' if diagnosis.handoff_to_cdu else 'NO (not yet)'}",
        "",
        "Evidence:",
    ]
    for item in diagnosis.evidence:
        lines.append(f"  • {item}")
    lines.append("")
    lines.append("Next (expert PE):")
    for item in diagnosis.next_actions:
        lines.append(f"  → {item}")
    lines.append("")
    lines.append("Safety: never auto-save; never silent Oil Manager rewrite.")

    flags = list(diagnosis.qa.flags) if diagnosis.qa else []
    gate = apply_complementary_gate(
        qa_status=diagnosis.state if diagnosis.state in {"O0", "O1", "O2", "O3", "O4", "OX"} else "OX",
        flags=flags,
        hypo_reviewed=False,
        feed_attached=False,
        oil_installed=False,
    )
    if diagnosis.handoff_to_cdu and gate.o4_blocked:
        lines.append("")
        lines.append("Note: hand-off suppressed by complementary O4 gate.")
    lines.append("")
    lines.append(format_identity_block())
    lines.append("")
    lines.append(format_complementary_block(gate))
    lines.append("")
    lines.append(format_aspen_block(diagnosis.assay))
    return "\n".join(lines)
