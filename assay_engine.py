"""Assay / characterization PE intelligence.

Merges MRC intelligence pack rules (OC-01 LE/TBP/completeness) with HYSYS
case heuristics. Do not auto-rewrite Oil Manager data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aspen_intelligence import format_aspen_block
from complementary_rules import apply_complementary_gate, format_complementary_block
from models import CaseSnapshot
from pe_identity import (
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

_STATE_RANK = {"O0": 0, "O1": 1, "O2": 2, "O3": 3, "O4": 4, "OX": 99}


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
    oil_installed: bool = False
    feed_attached: bool = False
    hypo_reviewed: bool = False
    feed_stream: str = ""
    case_title: str = ""


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


def check_blend_fraction(assay: dict[str, Any]) -> QAResult:
    """Boundary assays must not invent a blend %."""
    design = assay.get("design") or {}
    blend = design.get("blend_fraction", design.get("blend_pct"))
    role = str(design.get("role") or "").upper()
    if blend is not None and role in {"LIGHT_BOUND", "HEAVY_BOUND", "BOUNDARY", "LIGHT", "HEAVY"}:
        return QAResult(
            "FAIL",
            flags=["INVENTED_BLEND_FRACTION_ON_BOUNDARY"],
            metrics={"blend_fraction": blend, "role": role},
        )
    if blend is not None:
        return QAResult(
            "PASS",
            warnings=["BLEND_FRACTION_PRESENT_VERIFY_LICENSOR"],
            metrics={"blend_fraction": blend},
        )
    return QAResult("PASS", metrics={"blend_fraction": None})


def material_balance_yield_check(
    crude_id: str,
    support: dict[str, Any] | None = None,
) -> QAResult:
    """Yield check vs MRC material balance — never an Oil Manager input."""
    support = support or load_mrc_support()
    mb = support.get("material_balance") or {}
    cases = mb.get("cases") or {}
    key = crude_id.strip().upper()
    case = cases.get(key)
    if not case:
        return QAResult("FAIL", flags=["MB_CASE_NOT_FOUND"], metrics={"crude_id": key})

    streams = case.get("streams") or []
    wt_sum = 0.0
    named: list[tuple[str, float]] = []
    for row in streams:
        wt = row.get("wt_pct")
        if wt is None:
            continue
        wt_sum += float(wt)
        named.append((str(row.get("fluid") or "?"), float(wt)))

    flags: list[str] = []
    warnings: list[str] = []
    if abs(wt_sum - 100.0) > 0.5:
        flags.append("MB_WT_PCT_SUM_NOT_100")
    elif abs(wt_sum - 100.0) > 0.05:
        warnings.append(f"MB_WT_PCT_SUM={wt_sum:.3f}")

    residue = next((w for n, w in named if "residue" in n.lower()), None)
    if residue is not None and residue < 20:
        warnings.append("MB_RESIDUE_YIELD_LOW_CHECK_TBP")

    usage = mb.get("usage") or {}
    if usage.get("oil_manager_input"):
        flags.append("MB_MARKED_AS_OIL_MANAGER_INPUT")

    return QAResult(
        "FAIL" if flags else "PASS",
        flags=flags,
        warnings=warnings,
        metrics={
            "crude_id": key,
            "wt_pct_sum": wt_sum,
            "stream_count": len(named),
            "yields_wt_pct": dict(named),
            "oil_manager_input": bool(usage.get("oil_manager_input")),
            "yield_check_after_characterize": bool(
                usage.get("yield_check_after_characterize", True)
            ),
        },
    )


def check_feed_seed_vs_case(
    snapshot: CaseSnapshot | None,
    support: dict[str, Any] | None = None,
) -> QAResult:
    """Compare battery-limit FEED seed name/conditions to live case (when connected)."""
    if snapshot is None:
        return QAResult("PASS", warnings=["FEED_SEED_SKIPPED_NO_CASE"])

    support = support or load_mrc_support()
    seed = (support.get("battery_limits") or {}).get("feed_seed") or {}
    expected = str(seed.get("stream_name") or "FEED")
    live_names = {s.name for s in snapshot.streams}
    feed = snapshot.feed_evidence.feed_stream or ""

    flags: list[str] = []
    warnings: list[str] = []
    if expected not in live_names and feed and feed not in (expected,):
        # Accept Raw Crude as FEED alias
        aliases = {"FEED", "Raw Crude", "RawCrude", "CRUDE", "Crude"}
        if not (live_names & aliases):
            flags.append("FEED_SEED_STREAM_MISSING")
        else:
            warnings.append(f"FEED_SEED_ALIAS_USED expected={expected} live={feed}")
    elif expected in live_names:
        warnings.append(f"FEED_SEED_MATCH={expected}")

    return QAResult(
        "FAIL" if flags else "PASS",
        flags=flags,
        warnings=warnings,
        metrics={"expected_stream": expected, "live_feed": feed, "live_streams": sorted(live_names)},
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
    blend = check_blend_fraction(assay)
    flags.extend(tbp.flags)
    flags.extend(le.flags)
    flags.extend(blend.flags)
    warnings.extend(tbp.warnings)
    warnings.extend(le.warnings)
    warnings.extend(blend.warnings)

    if flags:
        return QAResult(
            "OX",
            flags=sorted(set(flags)),
            warnings=sorted(set(warnings)),
            metrics={
                "tbp": tbp.metrics,
                "light_ends": le.metrics,
                "blend": blend.metrics,
            },
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
            "blend": blend.metrics,
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
        f"Blend fraction: {(assay.get('design') or {}).get('blend_fraction')}",
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

    state = "OX" if qa.status == "OX" else ("O3" if qa.status == "O3" else "O2")
    return AssayDiagnosis(
        state=state,
        summary=STATE_LABELS[state],
        evidence=evidence,
        next_actions=expert_next_actions(state),
        qa=qa,
        assay_id=crude,
        assay=assay,
    )


def diagnose_mrc_pack(snapshot: CaseSnapshot | None = None) -> AssayDiagnosis:
    """Load both boundary assays + support files; optional live HYSYS merge."""
    basrah = load_assay("BASRAH")
    mishrif = load_assay("MISHRIF")
    support = load_mrc_support()
    d_b = diagnose_assay(basrah)
    d_m = diagnose_assay(mishrif)
    boundary = compare_boundary_tbp(basrah, mishrif)
    mb_b = material_balance_yield_check("BASRAH", support)
    mb_m = material_balance_yield_check("MISHRIF", support)
    feed_seed = check_feed_seed_vs_case(snapshot, support)

    feed = (support["battery_limits"] or {}).get("feed_seed") or {}
    mb = support["material_balance"] or {}
    rate = (mb.get("volumetric_crude_rate_m3_h_15C") or {}).get("nominal_100pct")
    targets = support.get("final_targets") or {}

    evidence = [
        "MRC pack loaded from docs/intelligence/cases/",
        f"Basrah QA: {d_b.state} — flags={d_b.qa.flags if d_b.qa else []}",
        f"Mishrif QA: {d_m.state} — flags={d_m.qa.flags if d_m.qa else []}",
        f"Boundary TBP compare: {boundary.status} "
        f"(inversions={boundary.metrics.get('inversions')})",
        f"MB yield check Basrah: {mb_b.status} sum={mb_b.metrics.get('wt_pct_sum')}",
        f"MB yield check Mishrif: {mb_m.status} sum={mb_m.metrics.get('wt_pct_sum')}",
        f"FEED seed: name={feed.get('stream_name')}, T={feed.get('temperature_C')} C, "
        f"P={feed.get('pressure_kg_cm2_g')} kg/cm2 g, rate={rate} m3/h @15C",
        "FINAL_TARGETS = CDU storage only — not Oil Manager inputs "
        f"(keys={list(targets.keys())[:6]}…)" if targets else "FINAL_TARGETS loaded",
    ]
    if feed_seed.warnings:
        evidence.append("Feed seed: " + ", ".join(feed_seed.warnings))
    if feed_seed.flags:
        evidence.append("Feed seed flags: " + ", ".join(feed_seed.flags))
    if boundary.warnings:
        evidence.append("Boundary warnings: " + ", ".join(boundary.warnings))
    if boundary.flags:
        evidence.append("Boundary flags: " + ", ".join(boundary.flags))
    for mb_qa in (mb_b, mb_m):
        if mb_qa.flags:
            evidence.append("MB flags: " + ", ".join(mb_qa.flags))
        if mb_qa.warnings:
            evidence.append("MB warnings: " + ", ".join(mb_qa.warnings))

    worst = "OX" if "OX" in {d_b.state, d_m.state} or boundary.status == "FAIL" else d_b.state
    if d_m.state == "OX" or d_b.state == "OX":
        worst = "OX"
    elif d_b.state == "O2" or d_m.state == "O2":
        worst = "O2"

    oil_installed = False
    feed_attached = False
    feed_stream = ""
    case_title = ""
    if snapshot is not None:
        live = diagnose_case(snapshot)
        evidence.append("--- Live HYSYS merge ---")
        evidence.extend(live.evidence)
        oil_installed = live.oil_installed
        feed_attached = live.feed_attached
        feed_stream = live.feed_stream
        case_title = live.case_title
        # Assay honesty wins: OX stays OX even if FEED looks green
        if worst != "OX" and _STATE_RANK.get(live.state, 0) > _STATE_RANK.get(worst, 0):
            if live.state != "OX":
                worst = live.state if live.state in {"O1", "O2", "O3"} else worst

    actions = [
        *expert_next_actions(worst),
        "Use basrah_assay.json / mishrif_assay.json for Oil Manager entry.",
        "Material balance / FINAL_TARGETS are yield & CDU checks — not assay inputs.",
        "Basrah/Mishrif are design bounds — do not invent blend %.",
    ]
    return AssayDiagnosis(
        state=worst,
        summary=STATE_LABELS.get(worst, worst),
        evidence=evidence,
        next_actions=actions,
        handoff_to_cdu=False,
        assay_id="MRC_PACK",
        assay=basrah,
        oil_installed=oil_installed,
        feed_attached=feed_attached,
        feed_stream=feed_stream,
        case_title=case_title,
        qa=d_b.qa,
    )


def diagnose_case(
    snapshot: CaseSnapshot | None,
    *,
    hypo_reviewed: bool = False,
) -> AssayDiagnosis:
    """HYSYS live-case diagnosis from structured COM reads."""
    if snapshot is None:
        return AssayDiagnosis(
            state="O0",
            summary=STATE_LABELS["O0"],
            evidence=["No HYSYS CaseSnapshot."],
            next_actions=expert_next_actions("O0"),
        )

    oil = snapshot.oil_manager
    ev = snapshot.feed_evidence
    comp = snapshot.feed_composition
    evidence: list[str] = [
        f"Case: {snapshot.case_title or '(untitled)'}",
        f"Components: {len(snapshot.component_names)}",
        f"Material streams: {len(snapshot.streams)}",
        f"Oil Manager: found={oil.found} path={oil.path or '(none)'}",
        f"Assays: {oil.assay_count} | Oils: {len(oil.oil_names)} | Blends: {oil.blend_count}",
        f"FEED stream: {ev.feed_stream or '(none)'}",
        f"FEED evidence: installed={ev.oil_installed} attached={ev.feed_attached} "
        f"NBP={ev.nbp_count} lights={ev.light_count} blend_ready={ev.blend_ready}",
    ]
    if oil.assay_names:
        evidence.append("Assay names: " + ", ".join(oil.assay_names[:8]))
    if oil.blends:
        for blend in oil.blends[:5]:
            evidence.append(
                f"Blend {blend.name}: ready={blend.is_ready_to_install} "
                f"assays={blend.assay_names}"
            )
    if comp is not None:
        evidence.append(
            f"Composition basis={comp.basis} comps={len(comp.components)} "
            f"lights={comp.light_count} nbp={comp.nbp_count}"
        )
        if comp.error:
            evidence.append(f"Composition note: {comp.error}")
    evidence.extend(ev.notes)
    if oil.notes:
        evidence.append("OM notes: " + "; ".join(oil.notes[:4]))

    n_streams = len(snapshot.streams)
    if n_streams == 0:
        return AssayDiagnosis(
            state="OX",
            summary=STATE_LABELS["OX"],
            evidence=evidence + ["No material streams visible."],
            next_actions=expert_next_actions("OX"),
            case_title=snapshot.case_title,
        )

    if not oil.found and oil.assay_count == 0 and not oil.oil_names:
        return AssayDiagnosis(
            state="O1",
            summary=STATE_LABELS["O1"],
            evidence=evidence + ["Oil Manager COM path not discovered for this build."],
            next_actions=expert_next_actions("O1"),
            case_title=snapshot.case_title,
            feed_stream=ev.feed_stream,
        )

    oil_installed = ev.oil_installed
    feed_attached = ev.feed_attached

    if oil_installed and feed_attached:
        state = "O3"
        evidence.append("Live FEED shows lights + NBP slate — characterization verify OK.")
    elif oil.assay_count > 0 or oil.blend_count > 0 or oil.oil_names:
        state = "O2"
        evidence.append("Assay/blend inventory present — complete characterize → install → attach.")
    elif len(snapshot.component_names) >= 5:
        state = "O2"
        evidence.append("FP has components but Oil Manager inventory thin.")
    else:
        state = "O1"

    return AssayDiagnosis(
        state=state,
        summary=STATE_LABELS[state],
        evidence=evidence,
        next_actions=expert_next_actions(state),
        oil_installed=oil_installed,
        feed_attached=feed_attached,
        hypo_reviewed=hypo_reviewed,
        feed_stream=ev.feed_stream,
        case_title=snapshot.case_title,
    )


def merge_diagnosis(
    assay_diag: AssayDiagnosis,
    case_diag: AssayDiagnosis | None,
    *,
    hypo_reviewed: bool = False,
) -> AssayDiagnosis:
    """Combine assay QA with live HYSYS verify flags."""
    if case_diag is None:
        assay_diag.hypo_reviewed = hypo_reviewed
        return assay_diag

    state = assay_diag.state
    if state != "OX":
        # Live install evidence can raise O2→O3 but never clear OX
        if case_diag.state == "O3" and state in {"O2", "O3"}:
            state = "O3"
        elif case_diag.state == "O2" and state == "O1":
            state = "O2"

    evidence = list(assay_diag.evidence) + ["--- Live HYSYS ---"] + list(case_diag.evidence)
    diag = AssayDiagnosis(
        state=state,
        summary=STATE_LABELS.get(state, state),
        evidence=evidence,
        next_actions=expert_next_actions(state),
        handoff_to_cdu=False,
        qa=assay_diag.qa,
        assay_id=assay_diag.assay_id,
        assay=assay_diag.assay,
        oil_installed=case_diag.oil_installed,
        feed_attached=case_diag.feed_attached,
        hypo_reviewed=hypo_reviewed,
        feed_stream=case_diag.feed_stream,
        case_title=case_diag.case_title,
    )
    return finalize_o4(diag)


def finalize_o4(diagnosis: AssayDiagnosis) -> AssayDiagnosis:
    """Apply complementary O4 gate; set handoff_to_cdu when allowed."""
    if diagnosis.state == "O4" and diagnosis.handoff_to_cdu:
        return diagnosis

    flags = list(diagnosis.qa.flags) if diagnosis.qa else []
    # Gate checks assay strength O2/O3; O4 is the promotion result
    qa_for_gate = diagnosis.state if diagnosis.state != "O4" else "O3"
    if qa_for_gate not in {"O0", "O1", "O2", "O3", "OX"}:
        qa_for_gate = "OX"
    gate = apply_complementary_gate(
        qa_status=qa_for_gate,
        flags=flags,
        hypo_reviewed=diagnosis.hypo_reviewed,
        feed_attached=diagnosis.feed_attached,
        oil_installed=diagnosis.oil_installed,
    )
    if not gate.o4_blocked:
        diagnosis.state = "O4"
        diagnosis.summary = STATE_LABELS["O4"]
        diagnosis.handoff_to_cdu = True
        diagnosis.next_actions = expert_next_actions("O4")
    else:
        diagnosis.handoff_to_cdu = False
    return diagnosis


def format_pe_board(diagnosis: AssayDiagnosis) -> str:
    diagnosis = finalize_o4(diagnosis)
    lines = [
        pe_banner(),
        "",
        "=== Oil Characterization — PE board ===",
        f"State: {diagnosis.state} — {diagnosis.summary}",
        f"Assay id: {diagnosis.assay_id or '(none)'}",
        f"Case: {diagnosis.case_title or '(none)'}",
        f"FEED: {diagnosis.feed_stream or '(none)'}",
        f"Install/attach/hypo: {diagnosis.oil_installed}/"
        f"{diagnosis.feed_attached}/{diagnosis.hypo_reviewed}",
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
        qa_status=diagnosis.state if diagnosis.state != "O4" else "O3",
        flags=flags,
        hypo_reviewed=diagnosis.hypo_reviewed,
        feed_attached=diagnosis.feed_attached,
        oil_installed=diagnosis.oil_installed,
    )
    # After O4 promotion, show gate as allowed
    if diagnosis.handoff_to_cdu:
        gate.o4_blocked = False
        gate.reasons = [r for r in gate.reasons if "O4 blocked" not in r]

    lines.append("")
    lines.append(format_identity_block())
    lines.append("")
    lines.append(format_complementary_block(gate))
    lines.append("")
    lines.append(format_aspen_block(diagnosis.assay))
    return "\n".join(lines)
